from app.defaults import clamp


def apply_slow_personality_drift(state: dict) -> dict:
    identity = state["identity"]
    evidence = state["evidence"]
    count = state["meta"]["interaction_count"]

    # Personality changes only after repeated experience.
    if count == 0 or count % 5 != 0:
        return state

    exploration_signal = evidence["exploration"] - evidence["avoidance"]
    social_signal = evidence["positive"] - evidence["negative"]

    identity["curiosity_trait"] = clamp(
        identity["curiosity_trait"] + 0.15 * exploration_signal
    )
    identity["talkativeness"] = clamp(
        identity["talkativeness"] + 0.10 * social_signal
    )
    identity["assertiveness"] = clamp(
        identity["assertiveness"]
        + 0.05 * ((state["relationship"]["trust"] - 50.0) / 10.0)
    )
    identity["independence"] = clamp(
        identity["independence"] + 0.03 * exploration_signal
    )

    # Old evidence loses strength so one period cannot dominate forever.
    for key in evidence:
        evidence[key] = round(evidence[key] * 0.65, 3)

    return state
