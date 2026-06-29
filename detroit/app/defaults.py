from datetime import datetime, timezone


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return round(max(minimum, min(maximum, value)), 3)


def default_state() -> dict:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "emotions": {
            "curiosity": 50.0,
            "interest": 50.0,
            "frustration": 10.0,
            "satisfaction": 45.0,
            "anxiety": 10.0,
        },
        "needs": {
            "social_need": 30.0,
            "novelty_need": 30.0,
            "competence_need": 40.0,
            "closure_need": 20.0,
        },
        "relationship": {
            "trust": 50.0,
            "affinity": 50.0,
            "familiarity": 0.0,
            "engagement_strength": 0.0,
            "conflict_count": 0,
        },
        "pressure": {
            "boredom": 100.0,
            "idle_minutes": 0.0,
            "interaction_saturation": 0.0,
            "last_initiation_at": None,
            "initiations_today": 0,
            "initiation_day": datetime.now(timezone.utc).date().isoformat(),
        },
        "identity": {
            "curiosity_trait": 55.0,
            "talkativeness": 45.0,
            "assertiveness": 45.0,
            "helpfulness_bias": 50.0,
            "emotional_volatility": 30.0,
            "independence": 55.0,
        },
        "evidence": {
            "positive": 0.0,
            "negative": 0.0,
            "exploration": 0.0,
            "avoidance": 0.0,
        },
        "meta": {
            "interaction_count": 0,
            "last_interaction_at": now,
            "last_action": "stay_silent",
        },
    }
