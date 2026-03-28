# 🙏 Sadhana Mitra — WhatsApp Bot for Saadho Sangha

**Sadhana Mitra** ("Companion on the Path") is an intelligent WhatsApp bot that handles routine Sadhak queries, provides accurate information about Saadho's programmes and Ashram, and routes complex queries to the right human volunteer.

## Architecture

```
WhatsApp → Twilio API → FastAPI Server → Claude LLM (with RAG) → Response
                                  ↕
                          ChromaDB Vector Store
                          (FAQ Knowledge Base)
```

**Option A — AI-Powered (RAG)** as recommended in the design brief.

- **WhatsApp API**: Twilio (handles message send/receive)
- **Server**: Python + FastAPI
- **LLM**: Anthropic Claude (Haiku tier for cost efficiency)
- **RAG**: ChromaDB + sentence-transformers for semantic FAQ retrieval
- **Escalation**: Rule-based routing to appropriate email contacts

## Project Structure

```
sadhana_mitr_bot/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, webhook endpoints
│   ├── bot.py               # Core bot logic, LLM interaction
│   ├── config.py            # Configuration & routing rules
│   ├── escalation.py        # Escalation routing logic
│   └── knowledge_base.py    # RAG knowledge base (ChromaDB)
├── knowledge_base/
│   ├── faqs.json            # Structured FAQ data
│   └── faq_template.xlsx    # Template for Saadho team (after generation)
├── scripts/
│   ├── generate_faq_template.py   # Generate Excel template
│   └── load_faqs_from_excel.py    # Load FAQs from Excel to JSON
├── tests/
│   └── test_bot.py          # Bot tests
├── .env.example             # Environment variable template
├── .gitignore
├── requirements.txt
├── run.py                   # Application entry point
└── README.md
```

## Setup

### 1. Prerequisites

- Python 3.11+
- A Twilio account with WhatsApp sandbox or Business API
- An Anthropic API key

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/charany1/sadhana_mitr_bot.git
cd sadhana_mitr_bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy the environment template
cp .env.example .env

# Edit .env with your credentials
# - TWILIO_ACCOUNT_SID
# - TWILIO_AUTH_TOKEN
# - TWILIO_WHATSAPP_NUMBER
# - ANTHROPIC_API_KEY
# - WEBHOOK_BASE_URL
```

### 4. Run the Bot

```bash
python run.py
```

The server starts at `http://localhost:8000`.

### 5. Expose to the Internet (for Twilio webhooks)

For development, use ngrok:

```bash
ngrok http 8000
```

Then set your Twilio WhatsApp webhook URL to:
```
https://your-ngrok-url.ngrok.io/webhook/whatsapp
```

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Health check |
| `/webhook/whatsapp` | POST | Twilio WhatsApp webhook (incoming messages) |
| `/webhook/whatsapp/status` | POST | Twilio delivery status callback |
| `/api/test` | POST | Test bot without WhatsApp (`{"message": "..."}`) |
| `/api/faqs` | GET | List all FAQs |
| `/api/reload` | POST | Reload knowledge base from JSON |

## Managing the Knowledge Base

### Option 1: Edit JSON Directly

Edit `knowledge_base/faqs.json` and call `POST /api/reload`.

### Option 2: Use the Excel Template

```bash
# Generate the template
python scripts/generate_faq_template.py

# Fill in the Excel file at knowledge_base/faq_template.xlsx

# Convert Excel to JSON
python scripts/load_faqs_from_excel.py

# Reload the bot's knowledge base
curl -X POST http://localhost:8000/api/reload
```

## Escalation Routing

| Query Type | Routed To |
|---|---|
| Programme registrations, fees | programs@saadho.org |
| Seva applications, volunteering | seva@saadho.org |
| Ashram visit, Gurudev Darshan | connect@saadho.org |
| Donations, financial support | connect@saadho.org |
| Sensitive personal/spiritual matters | connect@saadho.org |

## Design Guardrails

- **Never fabricates** — routes to human if uncertain
- **Never impersonates Gurudev** — no generated quotes
- **Bilingual** — English and Hindi support
- **Always transparent** — identifies itself as Sadhana Mitra, a digital companion
- **Always offers escalation** — every response includes a path to a human
- **Privacy-first** — no personal data stored

## Testing

```bash
# Test without WhatsApp using the API
curl -X POST http://localhost:8000/api/test \
  -H "Content-Type: application/json" \
  -d '{"message": "What yoga classes do you offer?"}'

# Test a greeting
curl -X POST http://localhost:8000/api/test \
  -H "Content-Type: application/json" \
  -d '{"message": "Namaste"}'

# Run unit tests
pytest tests/
```

## Twilio WhatsApp Setup

1. Go to [Twilio Console](https://console.twilio.com/)
2. Navigate to **Messaging > Try it out > Send a WhatsApp message**
3. Follow the sandbox setup instructions
4. Set the webhook URL to `https://your-domain.com/webhook/whatsapp`
5. For production, apply for a Twilio WhatsApp Business Profile

## Estimated Costs

| Item | Monthly Cost |
|---|---|
| Twilio WhatsApp API | INR 1,500 – 3,500 |
| Anthropic Claude API (Haiku) | INR 800 – 4,000 |
| Cloud hosting | INR 500 – 1,500 |
| **Total** | **INR 2,800 – 9,000** |

---

*May this Seva be in the spirit of offering — Saadho Sangha* 🙏
