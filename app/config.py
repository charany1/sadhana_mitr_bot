"""Configuration for Sadhana Mitra WhatsApp Bot."""

import os
from dotenv import load_dotenv

load_dotenv()

# Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Application
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
APP_ENV = os.getenv("APP_ENV", "development")
WEBHOOK_BASE_URL = os.getenv("WEBHOOK_BASE_URL", "http://localhost:8000")

# LLM Settings
LLM_MODEL = "claude-haiku-4-5-20251001"
LLM_MAX_TOKENS = 1024
LLM_TEMPERATURE = 0.3

# Escalation routing
ESCALATION_ROUTES = {
    "programmes": {
        "email": "programs@saadho.org",
        "keywords": [
            "registration", "register", "fee", "fees", "cost", "price",
            "yoga class", "meditation", "namo abhyasa", "retreat", "satsang",
            "schedule", "timing", "batch", "enroll", "enrolment", "admission",
        ],
    },
    "seva": {
        "email": "seva@saadho.org",
        "keywords": [
            "seva", "volunteer", "volunteering", "service", "contribute",
            "help out", "join team",
        ],
    },
    "ashram": {
        "email": "connect@saadho.org",
        "keywords": [
            "ashram visit", "darshan", "gurudev meeting", "visit ashram",
            "accommodation", "stay at ashram",
        ],
    },
    "donations": {
        "email": "connect@saadho.org",
        "keywords": [
            "donate", "donation", "financial", "support financially",
            "contribute money", "fund",
        ],
    },
    "sensitive": {
        "email": "connect@saadho.org",
        "keywords": [
            "personal", "spiritual guidance", "crisis", "mental health",
            "depression", "anxiety", "suffering", "pain", "death",
            "private matter", "confidential",
        ],
    },
}

# All contact emails
CONTACT_EMAILS = {
    "programmes": "programs@saadho.org",
    "seva": "seva@saadho.org",
    "general": "connect@saadho.org",
}
