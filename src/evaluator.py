"""
Evaluation / Test Harness for the Music Recommender System.

Runs predefined test cases and checks whether the system's top
recommendation meets expected criteria. Prints a pass/fail summary.

Run with:
    python -m src.evaluator
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.recommender import load_songs, recommend_songs
from src.guardrails import validate_profile


# ---------------------------------------------------------------------------
# Test cases: (profile_name, user_prefs, expected_top_genre, expected_top_mood)
# ---------------------------------------------------------------------------

TEST_CASES = [
    (
        "Pop/Happy should return a pop song at #1",
        {"genre": "pop", "mood": "happy", "energy": 0.85, "likes_acoustic": False},
        "pop", "happy",
    ),
    (
        "Lofi/Chill should return a lofi song at #1",
        {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True},
        "lofi", "chill",
    ),
    (
        "EDM/Intense should return an edm song at #1",
        {"genre": "edm", "mood": "intense", "energy": 0.95, "likes_acoustic": False},
        "edm", "intense",
    ),
    (
        "Guardrail: invalid energy (1.5) should be blocked",
        {"genre": "pop", "mood": "happy", "energy": 1.5, "likes_acoustic": False},
        None, None,  # expected to fail validation, not reach recommender
    ),
    (
        "Guardrail: unknown genre should be blocked",
        {"genre": "bossa nova", "mood": "relaxed", "energy": 0.4, "likes_acoustic": True},
        None, None,
    ),
    (
        "Country/Relaxed should return a country song at #1",
        {"genre": "country", "mood": "relaxed", "energy": 0.45, "likes_acoustic": True},
        "country", "relaxed",
    ),
]


def run_evaluation(csv_path: str = "data/songs.csv") -> None:
    """Run all test cases and print a pass/fail summary."""
    songs = load_songs(csv_path)

    passed = 0
    failed = 0
    total = len(TEST_CASES)

    print("=" * 60)
    print("EVALUATION HARNESS — Music Recommender System")
    print("=" * 60)

    for name, prefs, expected_genre, expected_mood in TEST_CASES:
        print(f"\nTEST: {name}")

        is_valid, messages = validate_profile(prefs)

        # Cases that should be blocked by guardrails
        if expected_genre is None:
            if not is_valid:
                print(f"  PASS — correctly blocked by guardrail")
                for m in messages:
                    print(f"    {m}")
                passed += 1
            else:
                print(f"  FAIL — should have been blocked but passed validation")
                failed += 1
            continue

        # Cases that should pass validation and produce results
        if not is_valid:
            print(f"  FAIL — unexpectedly blocked by guardrail")
            for m in messages:
                print(f"    {m}")
            failed += 1
            continue

        results = recommend_songs(prefs, songs, k=1)
        if not results:
            print(f"  FAIL — no results returned")
            failed += 1
            continue

        top_song, top_score, _ = results[0]
        genre_ok = top_song["genre"] == expected_genre
        mood_ok = top_song["mood"] == expected_mood

        if genre_ok and mood_ok:
            print(f"  PASS — #{1} is '{top_song['title']}' "
                  f"(genre={top_song['genre']}, mood={top_song['mood']}, score={top_score:.2f})")
            passed += 1
        else:
            print(f"  FAIL — expected genre={expected_genre}/mood={expected_mood}, "
                  f"got genre={top_song['genre']}/mood={top_song['mood']}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} tests passed, {failed}/{total} failed")
    print("=" * 60)


if __name__ == "__main__":
    run_evaluation()
