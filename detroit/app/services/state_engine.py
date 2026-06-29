from datetime import datetime, timezone

from app.defaults import clamp
from app.services.personality import apply_slow_personality_drift


def apply_interaction(
    state: dict,
    *,
    valence: float,
    novelty: float,
    importance: float,
    unresolved: bool,
) -> tuple[dict, dict[str, float]]:
    emotions = state["emotions"]
    needs = state["needs"]
    relationship = state["relationship"]
    pressure = state["pressure"]
    evidence = state["evidence"]
    meta = state["meta"]

    impact = {
        "curiosity": 6.0 * novelty,
        "interest": 5.0 * importance,
        "frustration": -5.0 * valence if valence > 0 else 8.0 * abs(valence),
        "satisfaction": 6.0 * max(valence, 0.0) - 4.0 * max(-valence, 0.0),
        "anxiety": 5.0 if unresolved else -2.0,
    }

    for key, delta in impact.items():
        emotions[key] = clamp(emotions[key] + delta)

    needs["social_need"] = clamp(needs["social_need"] - 8.0)
    needs["novelty_need"] = clamp(needs["novelty_need"] - 10.0 * novelty)
    needs["competence_need"] = clamp(
        needs["competence_need"] + (6.0 if unresolved else -3.0)
    )
    needs["closure_need"] = clamp(
        needs["closure_need"] + (10.0 * importance if unresolved else -4.0)
    )

    # Relationship changes faster than personality but still stays bounded.
    relationship["trust"] = clamp(relationship["trust"] + 5.0 * valence)
    relationship["affinity"] = clamp(relationship["affinity"] + 3.0 * valence)
    relationship["familiarity"] = clamp(relationship["familiarity"] + 1.0)
    relationship["engagement_strength"] = clamp(
        relationship["engagement_strength"] + 2.0 * importance
    )
    if valence <= -0.5:
        relationship["conflict_count"] += 1

    pressure["boredom"] = clamp(pressure["boredom"] - 12.0 * max(novelty, 0.2))
    pressure["idle_minutes"] = 0.0
    pressure["interaction_saturation"] = clamp(
        pressure["interaction_saturation"] + 8.0
    )

    evidence["positive"] += max(valence, 0.0)
    evidence["negative"] += max(-valence, 0.0)
    evidence["exploration"] += novelty
    evidence["avoidance"] += 1.0 - novelty

    meta["interaction_count"] += 1
    meta["last_interaction_at"] = datetime.now(timezone.utc).isoformat()

    apply_slow_personality_drift(state)
    return state, impact


def apply_time_passage(state: dict, minutes: float) -> dict:
    emotions = state["emotions"]
    needs = state["needs"]
    pressure = state["pressure"]

    hours = minutes / 60.0
    pressure["idle_minutes"] = clamp(
        pressure["idle_minutes"] + minutes, maximum=10080.0
    )
    pressure["boredom"] = clamp(pressure["boredom"] + 2.0 * minutes)
    pressure["interaction_saturation"] = clamp(
        pressure["interaction_saturation"] - 5.0 * hours
    )

    needs["social_need"] = clamp(needs["social_need"] + 2.5 * hours)
    needs["novelty_need"] = clamp(needs["novelty_need"] + 3.0 * hours)
    needs["closure_need"] = clamp(needs["closure_need"] + 0.5 * hours)

    emotions["interest"] = clamp(emotions["interest"] - 1.5 * hours)
    emotions["satisfaction"] = clamp(emotions["satisfaction"] - 1.0 * hours)
    emotions["frustration"] = clamp(emotions["frustration"] - 1.5 * hours)
    emotions["anxiety"] = clamp(emotions["anxiety"] - 0.5 * hours)

    return state
