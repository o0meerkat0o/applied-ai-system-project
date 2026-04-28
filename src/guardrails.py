"""
Input validation guardrails for the Music Recommender.

Catches bad or conflicting user profiles before they reach the
scoring function, and logs warnings for edge cases that may
produce poor recommendations.
"""

from typing import Tuple, List

VALID_GENRES = {
    "pop", "lofi", "edm", "rock", "jazz", "ambient",
    "hip-hop", "folk", "country", "synthwave", "r&b", "indie pop"
}

VALID_MOODS = {
    "happy", "chill", "intense", "moody", "relaxed", "focused"
}

# Genres that are structurally low-energy — flagged if user requests high energy
LOW_ENERGY_GENRES = {"ambient", "lofi", "folk", "jazz"}

# Energy threshold above which a low-energy genre triggers a conflict warning
HIGH_ENERGY_THRESHOLD = 0.7


def validate_profile(user_prefs: dict) -> Tuple[bool, List[str]]:
    """
    Validate a user preference profile.

    Returns (is_valid, messages) where is_valid is False if any hard
    errors are found, and messages contains all errors and warnings.
    """
    errors = []
    warnings = []

    # --- Hard errors (block execution) ---

    genre = user_prefs.get("genre", "")
    if not genre:
        errors.append("ERROR: 'genre' is required.")
    elif genre.lower() not in VALID_GENRES:
        errors.append(
            f"ERROR: '{genre}' is not a recognized genre. "
            f"Valid options: {', '.join(sorted(VALID_GENRES))}"
        )

    mood = user_prefs.get("mood", "")
    if not mood:
        errors.append("ERROR: 'mood' is required.")
    elif mood.lower() not in VALID_MOODS:
        errors.append(
            f"ERROR: '{mood}' is not a recognized mood. "
            f"Valid options: {', '.join(sorted(VALID_MOODS))}"
        )

    energy = user_prefs.get("energy")
    if energy is None:
        errors.append("ERROR: 'energy' is required.")
    elif not isinstance(energy, (int, float)):
        errors.append("ERROR: 'energy' must be a number between 0.0 and 1.0.")
    elif not (0.0 <= energy <= 1.0):
        errors.append(f"ERROR: 'energy' must be between 0.0 and 1.0, got {energy}.")

    likes_acoustic = user_prefs.get("likes_acoustic")
    if likes_acoustic is None:
        errors.append("ERROR: 'likes_acoustic' is required (True or False).")
    elif not isinstance(likes_acoustic, bool):
        errors.append("ERROR: 'likes_acoustic' must be True or False.")

    # --- Soft warnings (allow execution, but flag issues) ---

    if not errors:
        if genre.lower() in LOW_ENERGY_GENRES and energy > HIGH_ENERGY_THRESHOLD:
            warnings.append(
                f"WARNING: '{genre}' is a low-energy genre but you requested "
                f"energy={energy}. Recommendations may not match your energy target. "
                f"Consider trying 'edm', 'rock', or 'pop' for high-energy results."
            )

        if genre.lower() in LOW_ENERGY_GENRES and mood == "intense":
            warnings.append(
                f"WARNING: '{genre}' songs are rarely intense. "
                f"Your mood preference may not be satisfiable within this genre."
            )

    all_messages = errors + warnings
    is_valid = len(errors) == 0
    return is_valid, all_messages


def print_validation_result(user_prefs: dict, profile_name: str = "") -> bool:
    """
    Validate and print results. Returns True if valid, False if blocked.
    """
    is_valid, messages = validate_profile(user_prefs)
    if messages:
        label = f" ({profile_name})" if profile_name else ""
        for msg in messages:
            print(f"  [GUARDRAIL{label}] {msg}")
    return is_valid
