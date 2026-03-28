"""Escalation and routing logic for Sadhana Mitra."""

from app.config import ESCALATION_ROUTES, CONTACT_EMAILS


def detect_escalation_category(message: str) -> str | None:
    """Detect if a message should be escalated and return the category."""
    message_lower = message.lower()
    for category, route in ESCALATION_ROUTES.items():
        for keyword in route["keywords"]:
            if keyword in message_lower:
                return category
    return None


def get_escalation_email(category: str) -> str:
    """Get the email address for a given escalation category."""
    if category in ESCALATION_ROUTES:
        return ESCALATION_ROUTES[category]["email"]
    return CONTACT_EMAILS["general"]


def build_escalation_message(category: str, language: str = "en") -> str:
    """Build a warm handover message for escalation."""
    email = get_escalation_email(category)

    category_labels = {
        "programmes": "programme registrations and details",
        "seva": "Seva and volunteering",
        "ashram": "Ashram visits and Gurudev Darshan",
        "donations": "donations and financial support",
        "sensitive": "personal and spiritual matters",
    }

    topic = category_labels.get(category, "your query")

    if language == "hi":
        return (
            f"🙏 इस विषय के लिए — {topic} — हमारी समर्पित टीम आपकी "
            f"सबसे अच्छी सहायता कर सकती है।\n\n"
            f"कृपया उन्हें यहाँ लिखें: *{email}*\n\n"
            f"वे आपसे शीघ्र ही संपर्क करेंगे। 🙏"
        )

    return (
        f"🙏 For {topic}, our dedicated team can assist you best.\n\n"
        f"Please write to them at: *{email}*\n\n"
        f"They will get back to you soon. 🙏"
    )
