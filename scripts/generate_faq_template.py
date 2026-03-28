"""Generate the FAQ spreadsheet template for the Saadho communications team.

Run: python scripts/generate_faq_template.py

This creates an Excel file that the Saadho team can fill with their FAQs.
The bot's knowledge base can then be updated from this spreadsheet.
"""

import pandas as pd
from pathlib import Path

TEMPLATE_PATH = Path(__file__).parent.parent / "knowledge_base" / "faq_template.xlsx"

# Sample data to show the expected format
sample_data = [
    {
        "ID": "yoga_classes",
        "Category": "Programme Information",
        "Question": "What yoga classes does Saadho offer?",
        "Answer": "Saadho offers yoga classes in both online and in-person formats. For the current schedule, fee structure, and registration details, please write to programs@saadho.org.",
        "Keywords": "yoga, class, classes, yoga session, asana",
        "Routing Email": "programs@saadho.org",
    },
    {
        "ID": "guided_meditation",
        "Category": "Programme Information",
        "Question": "Tell me about guided meditation sessions.",
        "Answer": "Saadho conducts guided meditation sessions for practitioners at all levels. For session details, duration, and prerequisites, please write to programs@saadho.org.",
        "Keywords": "meditation, guided meditation, dhyana, meditate",
        "Routing Email": "programs@saadho.org",
    },
    {
        "ID": "ashram_visit",
        "Category": "Saadho Ashram",
        "Question": "How can I visit the Ashram?",
        "Answer": "Visiting the Saadho Ashram is a beautiful experience. For the complete visit process, please write to connect@saadho.org.",
        "Keywords": "visit ashram, ashram visit, come to ashram",
        "Routing Email": "connect@saadho.org",
    },
    {
        "ID": "seva",
        "Category": "Saadho Ashram",
        "Question": "How can I do Seva at the Ashram?",
        "Answer": "Seva (selfless service) is a beautiful way to contribute. To learn about Seva roles, please write to seva@saadho.org.",
        "Keywords": "seva, volunteer, volunteering, service",
        "Routing Email": "seva@saadho.org",
    },
    {
        "ID": "",
        "Category": "",
        "Question": "",
        "Answer": "",
        "Keywords": "",
        "Routing Email": "",
    },
]

CATEGORIES = [
    "Programme Information",
    "Saadho Ashram",
    "General Information",
]

ROUTING_EMAILS = [
    "programs@saadho.org",
    "seva@saadho.org",
    "connect@saadho.org",
]


def generate_template():
    """Generate the FAQ template Excel file."""
    df = pd.DataFrame(sample_data)

    TEMPLATE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(TEMPLATE_PATH, engine="openpyxl") as writer:
        # Main FAQ sheet
        df.to_excel(writer, sheet_name="FAQs", index=False)

        # Instructions sheet
        instructions = pd.DataFrame({
            "Instructions": [
                "Fill in the FAQs sheet with your questions and answers.",
                "",
                "Column Descriptions:",
                "  ID — A unique short identifier (e.g., yoga_classes, ashram_visit)",
                "  Category — One of: Programme Information, Saadho Ashram, General Information",
                "  Question — The question a Sadhak might ask",
                "  Answer — The accurate, verified answer",
                "  Keywords — Comma-separated keywords for search matching",
                "  Routing Email — Email to route to if human help is needed",
                "",
                "Available Routing Emails:",
                "  programs@saadho.org — Programme registrations, fees, availability",
                "  seva@saadho.org — Seva applications, volunteering",
                "  connect@saadho.org — Ashram visits, donations, general queries",
                "",
                "Important Notes:",
                "  - Only include verified, accurate information",
                "  - Do not include Gurudev's quotes unless from verified sources",
                "  - Keep answers concise — suitable for WhatsApp",
                "  - The first 4 rows are samples — you can modify or delete them",
            ]
        })
        instructions.to_excel(writer, sheet_name="Instructions", index=False)

    print(f"FAQ template created at: {TEMPLATE_PATH}")


if __name__ == "__main__":
    generate_template()
