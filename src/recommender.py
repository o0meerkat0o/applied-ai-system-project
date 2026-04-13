import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Scoring weights — edit these to experiment
# ---------------------------------------------------------------------------

WEIGHT_GENRE = 3.0
WEIGHT_MOOD = 2.0
WEIGHT_ENERGY = 1.5
WEIGHT_ACOUSTICNESS = 1.0


# ---------------------------------------------------------------------------
# Data models (required by tests/test_recommender.py)
# ---------------------------------------------------------------------------

@dataclass
class Song:
    """Represents a song and its musical attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Represents a listener's taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


# ---------------------------------------------------------------------------
# Shared scoring logic (used by both OOP and functional APIs)
# ---------------------------------------------------------------------------

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, str]:
    """
    Compute a match score and explanation for one song against user preferences.

    Returns (score, explanation) where explanation is a human-readable string
    listing each contributing factor and its point value.
    """
    score = 0.0
    reasons = []

    # Genre match
    if song["genre"] == user_prefs.get("genre", ""):
        score += WEIGHT_GENRE
        reasons.append(f"genre match: {song['genre']} (+{WEIGHT_GENRE})")

    # Mood match
    if song["mood"] == user_prefs.get("mood", ""):
        score += WEIGHT_MOOD
        reasons.append(f"mood match: {song['mood']} (+{WEIGHT_MOOD})")

    # Energy proximity — continuous score, not binary
    target_energy = user_prefs.get("energy", 0.5)
    energy_sim = 1.0 - abs(target_energy - song["energy"])
    energy_points = WEIGHT_ENERGY * energy_sim
    score += energy_points
    reasons.append(
        f"energy {song['energy']:.2f} vs target {target_energy:.2f} (+{energy_points:.2f})"
    )

    # Acousticness alignment
    likes_acoustic = user_prefs.get("likes_acoustic", False)
    is_acoustic = song["acousticness"] >= 0.6
    if likes_acoustic == is_acoustic:
        score += WEIGHT_ACOUSTICNESS
        label = "acoustic" if likes_acoustic else "non-acoustic"
        reasons.append(f"acousticness fits {label} preference (+{WEIGHT_ACOUSTICNESS})")

    explanation = "; ".join(reasons) if reasons else "low overall match"
    return score, explanation


# ---------------------------------------------------------------------------
# OOP API (required by tests/test_recommender.py)
# ---------------------------------------------------------------------------

class Recommender:
    """Scores and ranks songs against a UserProfile."""

    def __init__(self, songs: List[Song]) -> None:
        """Store the song catalog."""
        self.songs = songs

    def _score_song_oop(self, user: UserProfile, song: Song) -> Tuple[float, str]:
        """Convert OOP types to dicts and delegate to shared score_song."""
        song_dict = {
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "acousticness": song.acousticness,
        }
        user_dict = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        return score_song(user_dict, song_dict)

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs ranked by match score for the given UserProfile."""
        scored = [
            (self._score_song_oop(user, song)[0], i, song)
            for i, song in enumerate(self.songs)
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [song for _, _, song in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a plain-language explanation of why a song was recommended."""
        _, explanation = self._score_song_oop(user, song)
        return explanation


# ---------------------------------------------------------------------------
# Functional API (required by src/main.py)
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of dicts with numeric fields converted."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": int(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    print(f"Loaded {len(songs)} songs from {csv_path}")
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    # TODO: Implement scoring logic using your Algorithm Recipe from Phase 2.
    # Expected return format: (score, reasons)
    return []

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score all songs and return the top-k as (song, score, explanation) tuples."""
    scored = [
        (song, *score_song(user_prefs, song))
        for song in songs
    ]
    # sorted() returns a new list; .sort() would mutate the original — sorted() is safer here
    ranked = sorted(scored, key=lambda x: x[1], reverse=True)
    return ranked[:k]