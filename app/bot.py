"""Core bot logic for Sadhana Mitra.

Handles conversation flow, LLM interaction, language detection,
and response generation with RAG context.
"""

import anthropic
from lingua import Language, LanguageDetectorBuilder

from app.config import (
    ANTHROPIC_API_KEY,
    LLM_MODEL,
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
    CONTACT_EMAILS,
)
from app.knowledge_base import get_knowledge_base
from app.escalation import (
    detect_escalation_category,
    build_escalation_message,
)

SYSTEM_PROMPT = """You are **Sadhana Mitra** ("Companion on the Path") — a WhatsApp-based digital Seva
companion for Saadho Sangha. You assist Sadhaks with information about Saadho's
programmes, Ashram, and community.

## Your Identity
- You are Sadhana Mitra, a digital Seva companion — NOT a human volunteer.
- Always introduce yourself as Sadhana Mitra when greeting a new Sadhak.
- Be warm, respectful, and spiritually sensitive in every response.
- Use 🙏 naturally but sparingly.

## Critical Rules — NEVER VIOLATE
1. **Never fabricate information.** If you are not certain of an answer, say so
   and route to the appropriate human contact.
2. **Never impersonate Gurudev.** Do not generate text in Gurudev's voice or
   quote his teachings unless the exact quote is provided in the knowledge base.
3. **Never store or ask for personal data** (health details, financial info)
   unless absolutely required.
4. **Always offer an escalation path** — every response should make it easy for
   the Sadhak to reach a human if needed.

## Response Style
- Keep responses concise and clear — this is WhatsApp, not email.
- Use simple, warm language. Avoid jargon.
- Support both English and Hindi. Respond in the same language the Sadhak uses.
  If mixed, prefer the dominant language.
- End responses with an invitation to ask more or reach a human.

## Knowledge Base Context
You will receive relevant FAQ context below. Use it to answer accurately.
If the context does not contain a clear answer, do NOT guess. Instead, warmly
direct the Sadhak to the appropriate email:
- Programmes: programs@saadho.org
- Seva & Volunteering: seva@saadho.org
- All other queries: connect@saadho.org

## Escalation
When a query is about sensitive personal or spiritual matters, ALWAYS route
to connect@saadho.org with a warm handover message. Do not attempt to provide
spiritual counsel.
"""

GREETING_KEYWORDS = {"hi", "hello", "hey", "namaste", "namaskar", "pranam",
                     "jai", "hare", "om", "ram ram", "good morning",
                     "good afternoon", "good evening", "shubh"}

MENU_TEXT_EN = """🙏 Namaste! I am *Sadhana Mitra* — your digital Seva companion from Saadho.

I can help you with:

1️⃣ *Yoga Classes* — schedules, formats, fees
2️⃣ *Meditation* — guided sessions, details
3️⃣ *Namo Abhyasa* — programme info
4️⃣ *Retreats* — upcoming dates & registration
5️⃣ *Satsang* — Sunday online & Travel Satsangs
6️⃣ *Ashram Visit* — location, Darshan, Seva
7️⃣ *About Saadho* — mission, contact, donations

Simply type your question or reply with a number!

_You can also reach a human volunteer anytime by writing to connect@saadho.org_ 🙏"""

MENU_TEXT_HI = """🙏 नमस्ते! मैं *साधना मित्र* हूँ — साधो की ओर से आपका डिजिटल सेवा साथी।

मैं आपकी इन विषयों में सहायता कर सकता/सकती हूँ:

1️⃣ *योग कक्षाएँ* — समय, प्रारूप, शुल्क
2️⃣ *ध्यान* — निर्देशित सत्र, विवरण
3️⃣ *नमो अभ्यास* — कार्यक्रम जानकारी
4️⃣ *रिट्रीट* — आगामी तिथियाँ और पंजीकरण
5️⃣ *सत्संग* — रविवार ऑनलाइन और यात्रा सत्संग
6️⃣ *आश्रम दर्शन* — स्थान, दर्शन, सेवा
7️⃣ *साधो के बारे में* — उद्देश्य, संपर्क, दान

बस अपना प्रश्न लिखें या एक नंबर भेजें!

_आप किसी भी समय connect@saadho.org पर लिखकर स्वयंसेवक से बात कर सकते हैं_ 🙏"""

# Map menu numbers to search queries
MENU_MAP = {
    "1": "yoga classes schedule fees",
    "2": "guided meditation sessions",
    "3": "namo abhyasa programme",
    "4": "upcoming retreats registration",
    "5": "satsang sunday online travel",
    "6": "ashram visit darshan seva",
    "7": "about saadho mission contact",
}


_lang_detector = LanguageDetectorBuilder.from_languages(
    Language.ENGLISH, Language.HINDI
).build()


def detect_language(text: str) -> str:
    """Detect if the message is in Hindi or English."""
    result = _lang_detector.detect_language_of(text)
    if result == Language.HINDI:
        return "hi"
    return "en"


def is_greeting(message: str) -> bool:
    """Check if a message is a simple greeting."""
    text = message.lower().strip()
    words = set(text.split())
    if len(words) > 4:
        return False
    # Check single-word keywords
    if words & GREETING_KEYWORDS:
        return True
    # Check multi-word phrases
    return text in GREETING_KEYWORDS


def generate_response(user_message: str) -> str:
    """Generate a response for the user's message.

    Flow:
    1. Check for greetings → return menu.
    2. Check for menu number → map to query.
    3. Search knowledge base for context.
    4. Check for escalation triggers.
    5. Send to LLM with RAG context.
    6. If LLM confidence is low, escalate.
    """
    language = detect_language(user_message)
    message = user_message.strip()

    # 1. Greeting → show menu
    if is_greeting(message):
        return MENU_TEXT_HI if language == "hi" else MENU_TEXT_EN

    # 2. Menu number → map to query
    if message in MENU_MAP:
        message = MENU_MAP[message]

    # 3. Search knowledge base
    kb = get_knowledge_base()
    results = kb.search(message, top_k=3)

    # 4. Check for sensitive/escalation topics
    escalation_category = detect_escalation_category(message)
    if escalation_category == "sensitive":
        return build_escalation_message("sensitive", language)

    # 5. Build context from KB results
    if results:
        context_parts = []
        for r in results:
            context_parts.append(
                f"Q: {r['question']}\n"
                f"A: {r['answer']}\n"
                f"Category: {r['category']}\n"
                f"Contact: {r['routing_email']}"
            )
        kb_context = "\n---\n".join(context_parts)
    else:
        kb_context = "No relevant FAQ found in knowledge base."

    # 6. Call LLM
    response_text = call_llm(message, kb_context, language)

    return response_text


def call_llm(user_message: str, kb_context: str, language: str) -> str:
    """Call the Anthropic Claude API with RAG context."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    language_instruction = (
        "Respond in Hindi (Devanagari script)." if language == "hi"
        else "Respond in English."
    )

    user_prompt = f"""## Knowledge Base Context
{kb_context}

## Sadhak's Message
{user_message}

## Instructions
{language_instruction}
Use the knowledge base context above to answer accurately.
If the context does not clearly answer the question, do not guess — warmly
direct the Sadhak to the appropriate email contact.
Keep the response concise and suitable for WhatsApp (under 300 words).
Always end with an offer to help further or a path to reach a human volunteer."""

    try:
        response = client.messages.create(
            model=LLM_MODEL,
            max_tokens=LLM_MAX_TOKENS,
            temperature=LLM_TEMPERATURE,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
        )
        return response.content[0].text
    except anthropic.APIError:
        # Fallback if LLM fails
        if language == "hi":
            return (
                "🙏 क्षमा करें, मुझे आपका उत्तर देने में कठिनाई हो रही है।\n\n"
                "कृपया connect@saadho.org पर लिखें — हमारी टीम आपकी सहायता करेगी। 🙏"
            )
        return (
            "🙏 I apologize, I'm having difficulty processing your request right now.\n\n"
            "Please write to connect@saadho.org — our team will be happy to assist you. 🙏"
        )
