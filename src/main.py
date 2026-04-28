"""
Command line runner for the Applied AI Music Recommender System.

Run with:
    python -m src.main

New in this version:
- Input validation guardrails catch bad profiles before scoring
- RAG retrieves genre knowledge to ground AI explanations
- Claude API generates natural-language explanations (falls back to rule-based)
"""

from src.recommender import load_songs, recommend_songs
from src.rag import retrieve_context
from src.explainer import generate_ai_explanation
from src.guardrails import print_validation_result

USE_AI_EXPLANATION = True  # Set to False to use rule-based explanations only

PROFILES = [
    (
        "Alex — Pop / Happy / High Energy",
        {"genre": "pop", "mood": "happy", "energy": 0.85, "likes_acoustic": False},
    ),
    (
        "Sam — Lofi / Chill / Acoustic",
        {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True},
    ),
    (
        "Jordan — EDM / Intense / High Energy",
        {"genre": "edm", "mood": "intense", "energy": 0.95, "likes_acoustic": False},
    ),
]

EDGE_PROFILES = [
    (
        "Riley — Conflicting Preferences (ambient + high energy)",
        {"genre": "ambient", "mood": "chill", "energy": 0.9, "likes_acoustic": False},
    ),
    (
        "Morgan — Conflicting Preferences (acoustic folk + intense mood)",
        {"genre": "folk", "mood": "intense", "energy": 0.85, "likes_acoustic": True},
    ),
    (
        "Casey — Niche Genre (country)",
        {"genre": "country", "mood": "relaxed", "energy": 0.45, "likes_acoustic": True},
    ),
]

BAD_PROFILES = [
    (
        "Bad Profile 1 — energy out of range",
        {"genre": "pop", "mood": "happy", "energy": 1.8, "likes_acoustic": False},
    ),
    (
        "Bad Profile 2 — unrecognized genre",
        {"genre": "bossa nova", "mood": "relaxed", "energy": 0.4, "likes_acoustic": True},
    ),
]


def print_recommendations(profile_name, user_prefs, songs, k=3):
    """Validate, score, retrieve context, and print recommendations."""
    print(f"\n{'=' * 60}")
    print(f"Profile: {profile_name}")
    print(f"  genre={user_prefs['genre']}  mood={user_prefs['mood']}  "
          f"energy={user_prefs['energy']}  acoustic={user_prefs['likes_acoustic']}")
    print(f"{'=' * 60}")

    is_valid = print_validation_result(user_prefs, profile_name)
    if not is_valid:
        print("  Skipping recommendations due to invalid profile.\n")
        return

    rag_context = retrieve_context(user_prefs)
    results = recommend_songs(user_prefs, songs, k=k)

    for rank, (song, score, rule_explanation) in enumerate(results, start=1):
        if USE_AI_EXPLANATION:
            explanation = generate_ai_explanation(
                song, user_prefs, rule_explanation, rag_context
            )
        else:
            explanation = rule_explanation

        print(f"\n  #{rank}  {song['title']} — {song['artist']}")
        print(f"       Score : {score:.2f}")
        print(f"       Why   : {explanation}")
    print()


def main():
    songs = load_songs("data/songs.csv")

    print("\n--- Standard Profiles ---")
    for name, prefs in PROFILES:
        print_recommendations(name, prefs, songs)

    print("\n--- Edge Case Profiles ---")
    for name, prefs in EDGE_PROFILES:
        print_recommendations(name, prefs, songs)

    print("\n--- Guardrail Demonstration (invalid profiles) ---")
    for name, prefs in BAD_PROFILES:
        print_recommendations(name, prefs, songs)


if __name__ == "__main__":
    main()