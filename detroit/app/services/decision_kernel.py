from dataclasses import dataclass
from datetime import datetime, timezone
import random

from app.config import settings


ACTIONS = (
    "stay_silent",
    "respond_normally",
    "ask_clarification",
    "initiate_conversation",
    "offer_suggestion",
    "reflect_on_memory",
    "switch_topic",
)


@dataclass
class Decision:
    action: str
    reason: str
    scores: dict[str, float]
    blocked: bool
    seed: int


def _reset_daily_counter(state: dict) -> None:
    today = datetime.now(timezone.utc).date().isoformat()
    pressure = state["pressure"]
    if pressure["initiation_day"] != today:
        pressure["initiation_day"] = today
        pressure["initiations_today"] = 0


def _cooldown_active(state: dict) -> bool:
    raw = state["pressure"].get("last_initiation_at")
    if not raw:
        return False

    last = datetime.fromisoformat(raw)
    now = datetime.now(timezone.utc)
    elapsed_minutes = (now - last).total_seconds() / 60.0
    return elapsed_minutes < settings.autonomy_cooldown_minutes


def decide(
    state: dict,
    *,
    trigger: str,
    unresolved_count: int,
    memory_importance: float,
    user_typing: bool,
    safety_allowed: bool,
    seed: int | None = None,
) -> Decision:
    _reset_daily_counter(state)
    chosen_seed = seed if seed is not None else random.SystemRandom().randint(1, 2**31 - 1)
    rng = random.Random(chosen_seed)

    autonomous = trigger == "autonomous_tick"

    if not safety_allowed:
        return Decision(
            action="stay_silent",
            reason="Safety rules blocked action.",
            scores={"stay_silent": 100.0},
            blocked=True,
            seed=chosen_seed,
        )

    if autonomous and user_typing:
        return Decision(
            action="stay_silent",
            reason="The user is currently typing.",
            scores={"stay_silent": 100.0},
            blocked=True,
            seed=chosen_seed,
        )

    if autonomous and state["pressure"]["initiations_today"] >= settings.max_initiations_per_day:
        return Decision(
            action="stay_silent",
            reason="The daily initiation limit has been reached.",
            scores={"stay_silent": 100.0},
            blocked=True,
            seed=chosen_seed,
        )

    if autonomous and _cooldown_active(state):
        return Decision(
            action="stay_silent",
            reason="The initiation cooldown is still active.",
            scores={"stay_silent": 100.0},
            blocked=True,
            seed=chosen_seed,
        )

    e = state["emotions"]
    n = state["needs"]
    r = state["relationship"]
    p = state["pressure"]
    i = state["identity"]

    scores = {
        "stay_silent": (
            22
            + 0.36 * e["satisfaction"]
            + 0.42 * p["interaction_saturation"]
            + 0.15 * e["frustration"]
            - 0.24 * n["social_need"]
            - 0.12 * p["boredom"]
        ),
        "respond_normally": (
            (42 if trigger == "user_message" else -18)
            + 0.18 * i["helpfulness_bias"]
            + 0.20 * e["interest"]
            + 0.12 * n["competence_need"]
            + 0.08 * r["trust"]
            - 0.15 * e["frustration"]
        ),
        "ask_clarification": (
            (18 if trigger == "user_message" else 0)
            + 0.34 * e["anxiety"]
            + 0.18 * e["curiosity"]
            + 0.20 * n["competence_need"]
            + 2.5 * unresolved_count
        ),
        "initiate_conversation": (
            (-30 if trigger == "user_message" else 0)
            + 0.24 * i["independence"]
            + 0.30 * n["social_need"]
            + 0.26 * p["boredom"]
            + 0.14 * e["curiosity"]
            + 12.0 * memory_importance
            - 0.40 * p["interaction_saturation"]
        ),
        "offer_suggestion": (
            (15 if trigger == "user_message" else 0)
            + 0.28 * i["helpfulness_bias"]
            + 0.24 * n["competence_need"]
            + 0.15 * e["interest"]
            + 0.08 * r["trust"]
        ),
        "reflect_on_memory": (
            0.28 * n["closure_need"]
            + 4.0 * unresolved_count
            + 18.0 * memory_importance
            + 0.10 * r["affinity"]
            + 0.08 * e["curiosity"]
        ),
        "switch_topic": (
            0.34 * n["novelty_need"]
            + 0.30 * p["boredom"]
            + 0.14 * e["curiosity"]
            + 0.10 * i["independence"]
            - 0.16 * e["interest"]
        ),
    }

    # Imperfection is bounded and traceable. Higher volatility means more variation.
    noise_range = 6.0 * (i["emotional_volatility"] / 100.0)
    for action in ACTIONS:
        scores[action] = round(scores[action] + rng.uniform(-noise_range, noise_range), 3)

    winner = max(scores, key=scores.get)

    # A non-silence action must earn enough pressure to happen.
    if winner != "stay_silent" and scores[winner] < 35.0:
        winner = "stay_silent"

    reasons = {
        "stay_silent": "No active drive became strong enough to justify action.",
        "respond_normally": "Current engagement and response pressure won.",
        "ask_clarification": "Uncertainty and competence pressure won.",
        "initiate_conversation": "Social, boredom, curiosity, and independence pressures aligned.",
        "offer_suggestion": "Competence and helpfulness pressures won.",
        "reflect_on_memory": "Memory importance and closure pressure won.",
        "switch_topic": "Novelty and boredom pressures won.",
    }

    return Decision(
        action=winner,
        reason=reasons[winner],
        scores=scores,
        blocked=False,
        seed=chosen_seed,
    )
