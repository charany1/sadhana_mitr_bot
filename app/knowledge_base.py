"""Lightweight keyword-based knowledge base for Vercel deployment.

Uses TF-IDF-style keyword matching instead of heavy vector embeddings,
keeping the bundle under Vercel's 500MB limit.
"""

import json
import math
from pathlib import Path

FAQ_PATH = Path(__file__).parent.parent / "knowledge_base" / "faqs.json"


class KnowledgeBase:
    """Lightweight FAQ search using keyword matching."""

    def __init__(self):
        self.faqs: list[dict] = []
        self._index: dict[str, list[int]] = {}  # word → list of FAQ indices

    def load_faqs(self, faq_path: str | Path | None = None) -> None:
        """Load FAQs from JSON and build keyword index."""
        path = Path(faq_path) if faq_path else FAQ_PATH
        with open(path, "r", encoding="utf-8") as f:
            self.faqs = json.load(f)

        self._index.clear()
        for i, faq in enumerate(self.faqs):
            # Build searchable text from question + answer + keywords
            text = (
                f"{faq['question']} {faq['answer']} "
                f"{' '.join(faq.get('keywords', []))}"
            ).lower()
            words = set(text.split())
            for word in words:
                cleaned = word.strip(".,!?;:'\"()[]")
                if len(cleaned) > 2:
                    self._index.setdefault(cleaned, []).append(i)

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """Search FAQs using keyword scoring.

        Returns list of dicts with: question, answer, category,
        routing_email, distance (lower = better match).
        """
        if not self.faqs:
            return []

        query_words = set(query.lower().split())
        scores: dict[int, float] = {}
        total_faqs = len(self.faqs)

        for word in query_words:
            cleaned = word.strip(".,!?;:'\"()[]")
            if cleaned in self._index:
                matching_indices = self._index[cleaned]
                # IDF-like weight: rarer words score higher
                idf = math.log(total_faqs / (1 + len(matching_indices)))
                for idx in matching_indices:
                    scores[idx] = scores.get(idx, 0) + (1 + idf)

            # Also check substring matches in keywords
            for i, faq in enumerate(self.faqs):
                for kw in faq.get("keywords", []):
                    if cleaned in kw.lower() or kw.lower() in query.lower():
                        scores[i] = scores.get(i, 0) + 2.0

        if not scores:
            return []

        # Normalize scores to a 0-1 distance (lower = better)
        max_score = max(scores.values())
        ranked = sorted(scores.items(), key=lambda x: -x[1])[:top_k]

        results = []
        for idx, score in ranked:
            faq = self.faqs[idx]
            distance = 1.0 - (score / max_score) if max_score > 0 else 1.0
            results.append({
                "question": faq["question"],
                "answer": faq["answer"],
                "category": faq["category"],
                "routing_email": faq.get("routing_email", "connect@saadho.org"),
                "distance": distance,
            })

        return results

    def get_all_faqs(self) -> list[dict]:
        """Return all loaded FAQs."""
        return self.faqs

    def count(self) -> int:
        """Return FAQ count."""
        return len(self.faqs)


# Singleton instance
_kb_instance: KnowledgeBase | None = None


def get_knowledge_base() -> KnowledgeBase:
    """Get or create the singleton KnowledgeBase instance."""
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = KnowledgeBase()
        _kb_instance.load_faqs()
    return _kb_instance
