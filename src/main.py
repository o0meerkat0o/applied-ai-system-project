"""
Command line runner for the Music Recommender Simulation.

Run with:
    python -m src.main

Loads the song catalog and runs recommendations for three distinct user profiles.
"""

from src.recommender import load_songs, recommend_songs


# ---------------------------------------------------------------------------
# Three distinct user profiles (rubric requires at least 3)
# ---------------------------------------------------------------------------

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


def main() -> None:
    songs = load_songs("data/songs.csv")

    for profile_name, user_prefs in PROFILES:
        recommendations = recommend_songs(user_prefs, songs, k=5)

        print(f"\n{'=' * 60}")
        print(f"Profile: {profile_name}")
        print(f"  genre={user_prefs['genre']}  mood={user_prefs['mood']}  "
              f"energy={user_prefs['energy']}  acoustic={user_prefs['likes_acoustic']}")
        print(f"{'=' * 60}")

        for rank, (song, score, explanation) in enumerate(recommendations, start=1):
            print(f"  #{rank}  {song['title']} — {song['artist']}")
            print(f"       Score : {score:.2f}")
            print(f"       Why   : {explanation}")
            print()


if __name__ == "__main__":
    main()