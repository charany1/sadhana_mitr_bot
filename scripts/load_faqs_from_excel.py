"""Load FAQs from the Excel template into the JSON knowledge base.

Run: python scripts/load_faqs_from_excel.py

This reads the FAQ template Excel file and converts it to the JSON format
used by the bot's knowledge base.
"""

import json
from pathlib import Path

import pandas as pd

EXCEL_PATH = Path(__file__).parent.parent / "knowledge_base" / "faq_template.xlsx"
JSON_PATH = Path(__file__).parent.parent / "knowledge_base" / "faqs.json"


def load_from_excel(excel_path: str | Path | None = None):
    """Convert the FAQ Excel template to JSON for the knowledge base."""
    path = Path(excel_path) if excel_path else EXCEL_PATH

    df = pd.read_excel(path, sheet_name="FAQs")

    # Filter out empty rows
    df = df.dropna(subset=["ID", "Question", "Answer"])
    df = df[df["ID"].str.strip() != ""]

    faqs = []
    for _, row in df.iterrows():
        keywords = [k.strip() for k in str(row.get("Keywords", "")).split(",") if k.strip()]
        faq = {
            "id": str(row["ID"]).strip(),
            "category": str(row.get("Category", "General Information")).strip(),
            "question": str(row["Question"]).strip(),
            "answer": str(row["Answer"]).strip(),
            "keywords": keywords,
            "routing_email": str(row.get("Routing Email", "connect@saadho.org")).strip(),
        }
        faqs.append(faq)

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(faqs, f, indent=2, ensure_ascii=False)

    print(f"Loaded {len(faqs)} FAQs from {path}")
    print(f"Saved to {JSON_PATH}")


if __name__ == "__main__":
    load_from_excel()
