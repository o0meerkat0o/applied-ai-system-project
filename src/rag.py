"""
Retrieval-Augmented Generation (RAG) module for the Music Recommender.

Loads plain-text genre knowledge documents from the knowledge_base/ folder
and retrieves the most relevant context for a given user profile.
"""

import os
from typing import Optional


KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge_base")

# Map genre names to their knowledge base files
GENRE_FILE_MAP = {
    "pop": "pop.txt",
    "lofi": "lofi.txt",
    "edm": "edm.txt",
    "rock": "rock.txt",
    "jazz": "jazz.txt",
    "ambient": "ambient.txt",
    "hip-hop": "hip-hop.txt",
    "folk": "folk.txt",
    "country": "country.txt",
    "synthwave": "synthwave_rb_indiepop.txt",
    "r&b": "synthwave_rb_indiepop.txt",
    "indie pop": "synthwave_rb_indiepop.txt",
}


def load_genre_context(genre: str) -> Optional[str]:
    """
    Load and return the knowledge base text for a given genre.

    Returns None if no document exists for that genre.
    """
    filename = GENRE_FILE_MAP.get(genre.lower())
    if not filename:
        return None

    filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)
    if not os.path.exists(filepath):
        return None

    with open(filepath, encoding="utf-8") as f:
        return f.read().strip()


def retrieve_context(user_prefs: dict) -> str:
    """
    Build a retrieval context string for a user profile.

    Pulls the genre knowledge doc and adds a brief summary of
    the user's preferences to ground the AI explanation.
    """
    genre = user_prefs.get("genre", "unknown")
    mood = user_prefs.get("mood", "unknown")
    energy = user_prefs.get("energy", 0.5)
    likes_acoustic = user_prefs.get("likes_acoustic", False)

    genre_doc = load_genre_context(genre)

    context_parts = []

    if genre_doc:
        context_parts.append(f"[Genre Knowledge: {genre.upper()}]\n{genre_doc}")
    else:
        context_parts.append(f"[Genre Knowledge: {genre.upper()}]\nNo specific knowledge available for this genre.")

    context_parts.append(
        f"\n[User Preferences]\n"
        f"Preferred genre: {genre}\n"
        f"Preferred mood: {mood}\n"
        f"Target energy level: {energy} (scale 0.0–1.0)\n"
        f"Prefers acoustic sound: {likes_acoustic}"
    )

    return "\n\n".join(context_parts)
