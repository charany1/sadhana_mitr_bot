"""RAG Knowledge Base for Sadhana Mitra.

Loads FAQ data, builds a vector store using ChromaDB + sentence-transformers,
and provides semantic search for answering Sadhak queries.
"""

import json
import os
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

FAQ_PATH = Path(__file__).parent.parent / "knowledge_base" / "faqs.json"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"


class KnowledgeBase:
    """Manages the FAQ vector store for retrieval-augmented generation."""

    def __init__(self):
        self.faqs: list[dict] = []
        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name="sadhana_mitra_faqs",
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def load_faqs(self, faq_path: str | Path | None = None) -> None:
        """Load FAQs from JSON and index them in the vector store."""
        path = Path(faq_path) if faq_path else FAQ_PATH
        with open(path, "r", encoding="utf-8") as f:
            self.faqs = json.load(f)

        # Clear and reload
        existing = self.collection.count()
        if existing > 0:
            self.collection.delete(
                ids=[faq["id"] for faq in self.faqs]
            )

        documents = []
        metadatas = []
        ids = []

        for faq in self.faqs:
            # Combine question + keywords for better retrieval
            searchable_text = (
                f"{faq['question']} {faq['answer']} "
                f"{' '.join(faq.get('keywords', []))}"
            )
            documents.append(searchable_text)
            metadatas.append({
                "category": faq["category"],
                "question": faq["question"],
                "answer": faq["answer"],
                "routing_email": faq.get("routing_email", "connect@saadho.org"),
            })
            ids.append(faq["id"])

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """Search the knowledge base for relevant FAQs.

        Returns a list of dicts with keys: question, answer, category,
        routing_email, distance.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=min(top_k, self.collection.count()),
        )

        matches = []
        if results and results["metadatas"]:
            for i, metadata in enumerate(results["metadatas"][0]):
                distance = results["distances"][0][i] if results["distances"] else 1.0
                matches.append({
                    "question": metadata["question"],
                    "answer": metadata["answer"],
                    "category": metadata["category"],
                    "routing_email": metadata["routing_email"],
                    "distance": distance,
                })

        return matches

    def get_all_faqs(self) -> list[dict]:
        """Return all loaded FAQs."""
        return self.faqs


# Singleton instance
_kb_instance: KnowledgeBase | None = None


def get_knowledge_base() -> KnowledgeBase:
    """Get or create the singleton KnowledgeBase instance."""
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = KnowledgeBase()
        _kb_instance.load_faqs()
    return _kb_instance
