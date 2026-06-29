from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from app.defaults import default_state
from app.models import AgentProfile, DecisionRecord, MemoryEvent, OutboxMessage
from app.services.decision_kernel import Decision, decide
from app.services.memory import create_memory, recent_memories, unresolved_memories
from app.services.renderer import render
from app.services.state_engine import apply_interaction, apply_time_passage


def get_agent(db: Session, agent_id: str) -> AgentProfile | None:
    return db.get(AgentProfile, agent_id)


def create_agent(db: Session, agent_id: str, name: str) -> AgentProfile:
    existing = get_agent(db, agent_id)
    if existing:
        return existing

    agent = AgentProfile(id=agent_id, name=name, state=default_state())
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


def _memory_context(db: Session, agent_id: str) -> tuple[int, float, MemoryEvent | None]:
    unresolved = unresolved_memories(db, agent_id, limit=10)
    recent = recent_memories(db, agent_id, limit=10)
    chosen = unresolved[0] if unresolved else (recent[0] if recent else None)
    importance = chosen.importance if chosen else 0.0
    return len(unresolved), importance, chosen


def _save_decision(
    db: Session,
    *,
    agent: AgentProfile,
    trigger: str,
    decision: Decision,
    content: str | None,
    autonomous: bool,
) -> None:
    agent.state["meta"]["last_action"] = decision.action

    if autonomous and decision.action != "stay_silent" and content:
        now = datetime.now(timezone.utc)
        agent.state["pressure"]["last_initiation_at"] = now.isoformat()
        agent.state["pressure"]["initiations_today"] += 1
        db.add(
            OutboxMessage(
                agent_id=agent.id,
                action=decision.action,
                content=content,
            )
        )

    db.add(
        DecisionRecord(
            agent_id=agent.id,
            trigger=trigger,
            action=decision.action,
            reason=decision.reason,
            scores=decision.scores,
            blocked=decision.blocked,
            seed=decision.seed,
        )
    )
    agent.updated_at = datetime.now(timezone.utc)
    db.add(agent)


def process_interaction(
    db: Session,
    *,
    agent: AgentProfile,
    message: str,
    topic: str | None,
    valence: float,
    novelty: float,
    importance: float,
    unresolved: bool,
    user_typing: bool,
    safety_allowed: bool,
    seed: int | None,
) -> tuple[AgentProfile, Decision, str | None]:
    state, impact = apply_interaction(
        agent.state,
        valence=valence,
        novelty=novelty,
        importance=importance,
        unresolved=unresolved,
    )
    agent.state = state

    create_memory(
        db,
        agent_id=agent.id,
        event_type="user_interaction",
        summary=message[:1000],
        topic=topic,
        importance=importance,
        valence=valence,
        novelty=novelty,
        unresolved=unresolved,
        emotional_impact=impact,
    )

    unresolved_count, memory_importance, memory = _memory_context(db, agent.id)
    decision = decide(
        agent.state,
        trigger="user_message",
        unresolved_count=unresolved_count,
        memory_importance=memory_importance,
        user_typing=user_typing,
        safety_allowed=safety_allowed,
        seed=seed,
    )
    content = render(decision.action, agent.state, memory)
    _save_decision(
        db,
        agent=agent,
        trigger="user_message",
        decision=decision,
        content=content,
        autonomous=False,
    )
    flag_modified(agent, "state")
    db.commit()
    db.refresh(agent)
    return agent, decision, content


def process_tick(
    db: Session,
    *,
    agent: AgentProfile,
    minutes: float,
    user_typing: bool,
    safety_allowed: bool,
    seed: int | None,
) -> tuple[AgentProfile, Decision, str | None]:
    agent.state = apply_time_passage(agent.state, minutes)

    unresolved_count, memory_importance, memory = _memory_context(db, agent.id)
    decision = decide(
        agent.state,
        trigger="autonomous_tick",
        unresolved_count=unresolved_count,
        memory_importance=memory_importance,
        user_typing=user_typing,
        safety_allowed=safety_allowed,
        seed=seed,
    )
    content = render(decision.action, agent.state, memory)
    _save_decision(
        db,
        agent=agent,
        trigger="autonomous_tick",
        decision=decision,
        content=content,
        autonomous=True,
    )
    flag_modified(agent, "state")
    db.commit()
    db.refresh(agent)
    return agent, decision, content


def list_memories(db: Session, agent_id: str, limit: int = 50) -> list[MemoryEvent]:
    statement = (
        select(MemoryEvent)
        .where(MemoryEvent.agent_id == agent_id)
        .order_by(desc(MemoryEvent.created_at))
        .limit(limit)
    )
    return list(db.scalars(statement))


def list_decisions(db: Session, agent_id: str, limit: int = 50) -> list[DecisionRecord]:
    statement = (
        select(DecisionRecord)
        .where(DecisionRecord.agent_id == agent_id)
        .order_by(desc(DecisionRecord.created_at))
        .limit(limit)
    )
    return list(db.scalars(statement))


def consume_outbox(db: Session, agent_id: str) -> list[OutboxMessage]:
    statement = (
        select(OutboxMessage)
        .where(
            OutboxMessage.agent_id == agent_id,
            OutboxMessage.delivered.is_(False),
        )
        .order_by(OutboxMessage.created_at)
    )
    messages = list(db.scalars(statement))
    for message in messages:
        message.delivered = True
        db.add(message)
    db.commit()
    return messages
