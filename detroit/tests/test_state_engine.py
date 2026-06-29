from app.defaults import default_state
from app.services.state_engine import apply_interaction, apply_time_passage


def test_positive_interaction_increases_trust():
    state = default_state()
    before = state["relationship"]["trust"]
    state, _ = apply_interaction(
        state,
        valence=1.0,
        novelty=0.5,
        importance=0.5,
        unresolved=False,
    )
    assert state["relationship"]["trust"] > before


def test_time_increases_boredom_and_social_need():
    state = default_state()
    boredom = state["pressure"]["boredom"]
    social_need = state["needs"]["social_need"]
    state = apply_time_passage(state, 120)
    assert state["pressure"]["boredom"] > boredom
    assert state["needs"]["social_need"] > social_need
