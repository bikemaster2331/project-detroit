from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models import MemoryEvent


def create_memory(
    db: Session,
    *,
    agent_id: str,
    event_type: str,
    summary: str,
    topic: str | None,
    importance: float,
    valence: float,
    novelty: float,
    unresolved: bool,
    emotional_impact: dict[str, float],
) -> MemoryEvent:
    memory = MemoryEvent(
        agent_id=agent_id,
        event_type=event_type,
        summary=summary,
        topic=topic,
        importance=importance,
        valence=valence,
        novelty=novelty,
        unresolved=unresolved,
        emotional_impact=emotional_impact,
    )
    db.add(memory)
    db.flush()
    return memory


def recent_memories(db: Session, agent_id: str, limit: int = 10) -> list[MemoryEvent]:
    statement = (
        select(MemoryEvent)
        .where(MemoryEvent.agent_id == agent_id)
        .order_by(desc(MemoryEvent.created_at))
        .limit(limit)
    )
    return list(db.scalars(statement))


def unresolved_memories(db: Session, agent_id: str, limit: int = 10) -> list[MemoryEvent]:
    statement = (
        select(MemoryEvent)
        .where(MemoryEvent.agent_id == agent_id, MemoryEvent.unresolved.is_(True))
        .order_by(desc(MemoryEvent.importance), desc(MemoryEvent.created_at))
        .limit(limit)
    )
    return list(db.scalars(statement))
