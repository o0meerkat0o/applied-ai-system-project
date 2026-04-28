"""
AI Explainer module for the Music Recommender System.

Uses the Google Gemini API with retrieved genre knowledge (RAG)
to generate richer, grounded explanations for recommended songs.
Falls back to the rule-based explanation if the API call fails.

Free tier: https://aistudio.google.com (no credit card required)
"""

import os
import json
import ssl
import urllib.request
import urllib.error


GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)


def get_api_key() -> str | None:
    """Read the Gemini API key from environment or .env file."""
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key

    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("GEMINI_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def generate_ai_explanation(
    song: dict,
    user_prefs: dict,
    rule_explanation: str,
    rag_context: str,
) -> str:
    """
    Call Gemini API to generate a grounded explanation for a recommendation.

    Uses the retrieved genre knowledge as context so the explanation
    references real musical characteristics, not just scoring math.
    Falls back to the rule-based explanation if the API is unavailable.
    """
    api_key = get_api_key()
    if not api_key:
        return f"[rule-based] {rule_explanation}"

    prompt = f"""You are a music recommendation assistant. Explain in 2-3 sentences why this song was recommended to this listener. Be specific, natural, and grounded in the genre knowledge provided. Do not mention scoring weights or numbers.

{rag_context}

[Recommended Song]
Title: {song['title']}
Artist: {song['artist']}
Genre: {song['genre']}
Mood: {song['mood']}
Energy: {song['energy']}
Acousticness: {song['acousticness']}

[Rule-Based Match Reasons]
{rule_explanation}

Write a 2-3 sentence explanation for why this song fits this listener. Sound like a knowledgeable friend, not a robot."""

    payload = json.dumps({
        "contents": [
            {"parts": [{"text": prompt}]}
        ],
        "generationConfig": {
            "maxOutputTokens": 150,
            "temperature": 0.7,
        }
    }).encode("utf-8")

    url = f"{GEMINI_API_URL}?key={api_key}"

    # Disable SSL verification to handle Mac certificate issues
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (urllib.error.URLError, KeyError, json.JSONDecodeError, IndexError):
        return f"[rule-based fallback] {rule_explanation}"