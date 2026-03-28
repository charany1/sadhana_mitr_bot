"""Sadhana Mitra — WhatsApp Bot API Server.

FastAPI application that handles incoming WhatsApp messages via Twilio webhooks,
processes them through the RAG-powered bot, and sends responses back.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Form, Response
from twilio.rest import Client as TwilioClient
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

from app.config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_NUMBER,
    APP_ENV,
    WEBHOOK_BASE_URL,
)
from app.bot import generate_response
from app.knowledge_base import get_knowledge_base

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("sadhana_mitra")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the knowledge base on startup."""
    logger.info("Initializing Sadhana Mitra knowledge base...")
    kb = get_knowledge_base()
    logger.info(f"Knowledge base loaded with {kb.count()} FAQs.")
    yield
    logger.info("Sadhana Mitra shutting down. 🙏")


app = FastAPI(
    title="Sadhana Mitra",
    description="WhatsApp Bot for Saadho Sangha — Sadhak Support",
    version="1.0.0",
    lifespan=lifespan,
)


def validate_twilio_request(request_url: str, params: dict, signature: str) -> bool:
    """Validate that a request genuinely came from Twilio."""
    if APP_ENV == "development":
        return True
    validator = RequestValidator(TWILIO_AUTH_TOKEN)
    return validator.validate(request_url, params, signature)


@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "Sadhana Mitra",
        "description": "WhatsApp Bot for Saadho Sangha",
    }


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...),
    ProfileName: str = Form(default="Sadhak"),
):
    """Handle incoming WhatsApp messages from Twilio.

    Twilio sends a POST with form data including:
    - From: sender's WhatsApp number (whatsapp:+91...)
    - Body: message text
    - ProfileName: sender's WhatsApp display name
    """
    # Validate Twilio signature in production
    signature = request.headers.get("X-Twilio-Signature", "")
    request_url = f"{WEBHOOK_BASE_URL}/webhook/whatsapp"
    form_data = {"From": From, "Body": Body, "ProfileName": ProfileName}

    if not validate_twilio_request(request_url, form_data, signature):
        logger.warning(f"Invalid Twilio signature from {From}")
        return Response(status_code=403)

    logger.info(f"Message from {ProfileName} ({From}): {Body[:100]}")

    # Generate bot response
    try:
        bot_response = generate_response(Body)
    except Exception as e:
        logger.error(f"Error generating response: {e}", exc_info=True)
        bot_response = (
            "🙏 I apologize, something went wrong on my end.\n\n"
            "Please write to connect@saadho.org for assistance. 🙏"
        )

    logger.info(f"Response to {ProfileName}: {bot_response[:100]}...")

    # Build TwiML response
    twiml = MessagingResponse()
    twiml.message(bot_response)

    return Response(content=str(twiml), media_type="application/xml")


@app.post("/webhook/whatsapp/status")
async def whatsapp_status_callback(request: Request):
    """Handle message delivery status callbacks from Twilio."""
    form = await request.form()
    message_sid = form.get("MessageSid", "unknown")
    status = form.get("MessageStatus", "unknown")
    logger.info(f"Message {message_sid} status: {status}")
    return {"status": "ok"}


@app.get("/api/faqs")
async def list_faqs():
    """List all FAQs in the knowledge base (admin endpoint)."""
    kb = get_knowledge_base()
    return {"faqs": kb.get_all_faqs(), "count": len(kb.get_all_faqs())}


@app.post("/api/reload")
async def reload_knowledge_base():
    """Reload the knowledge base from the FAQ file (admin endpoint)."""
    kb = get_knowledge_base()
    kb.load_faqs()
    return {"status": "reloaded", "count": kb.count()}


@app.post("/api/test")
async def test_bot(message: dict):
    """Test endpoint — send a message and get a bot response without WhatsApp.

    Usage: POST /api/test with JSON body: {"message": "your question here"}
    """
    user_message = message.get("message", "")
    if not user_message:
        return {"error": "Please provide a 'message' field."}

    response = generate_response(user_message)
    return {"user_message": user_message, "bot_response": response}
