from app.defaults import default_state
from app.services.decision_kernel import decide


def test_safety_forces_silence():
    result = decide(
        default_state(),
        trigger="autonomous_tick",
        unresolved_count=0,
        memory_importance=0.0,
        user_typing=False,
        safety_allowed=False,
        seed=1,
    )
    assert result.action == "stay_silent"
    assert result.blocked is True


def test_high_autonomy_pressure_can_initiate():
    state = default_state()
    state["needs"]["social_need"] = 100
    state["needs"]["novelty_need"] = 100
    state["pressure"]["boredom"] = 100
    state["identity"]["independence"] = 100
    state["pressure"]["interaction_saturation"] = 0

    result = decide(
        state,
        trigger="autonomous_tick",
        unresolved_count=0,
        memory_importance=0.0,
        user_typing=False,
        safety_allowed=True,
        seed=4,
    )
    assert result.action in {
        "initiate_conversation",
        "switch_topic",
        "reflect_on_memory",
    }


def test_decision_is_reproducible_with_seed():
    state = default_state()
    first = decide(
        state,
        trigger="user_message",
        unresolved_count=1,
        memory_importance=0.8,
        user_typing=False,
        safety_allowed=True,
        seed=123,
    )
    second = decide(
        state,
        trigger="user_message",
        unresolved_count=1,
        memory_importance=0.8,
        user_typing=False,
        safety_allowed=True,
        seed=123,
    )
    assert first.action == second.action
    assert first.scores == second.scores
