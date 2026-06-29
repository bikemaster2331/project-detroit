from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    AgentResponse,
    CreateAgentRequest,
    DecisionResponse,
    InteractionRequest,
    InteractionResponse,
    TickRequest,
)
from app.services.agent_service import (
    consume_outbox,
    create_agent,
    get_agent,
    list_decisions,
    list_memories,
    process_interaction,
    process_tick,
)


router = APIRouter(prefix="/api", tags=["agent"])


def require_agent(db: Session, agent_id: str):
    agent = get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.post("/agents", response_model=AgentResponse)
def create_agent_route(payload: CreateAgentRequest, db: Session = Depends(get_db)):
    return create_agent(db, payload.agent_id, payload.name)


@router.get("/agents/{agent_id}", response_model=AgentResponse)
def get_agent_route(agent_id: str, db: Session = Depends(get_db)):
    return require_agent(db, agent_id)


@router.post("/agents/{agent_id}/interact", response_model=InteractionResponse)
def interact(agent_id: str, payload: InteractionRequest, db: Session = Depends(get_db)):
    agent = require_agent(db, agent_id)
    agent, decision, content = process_interaction(
        db,
        agent=agent,
        message=payload.message,
        topic=payload.topic,
        valence=payload.valence,
        novelty=payload.novelty,
        importance=payload.importance,
        unresolved=payload.unresolved,
        user_typing=payload.user_typing,
        safety_allowed=payload.safety_allowed,
        seed=payload.seed,
    )
    return InteractionResponse(
        agent=agent,
        decision=DecisionResponse(
            action=decision.action,
            reason=decision.reason,
            scores=decision.scores,
            content=content,
            blocked=decision.blocked,
            seed=decision.seed,
        ),
    )


@router.post("/agents/{agent_id}/tick", response_model=InteractionResponse)
def tick(agent_id: str, payload: TickRequest, db: Session = Depends(get_db)):
    agent = require_agent(db, agent_id)
    agent, decision, content = process_tick(
        db,
        agent=agent,
        minutes=payload.minutes,
        user_typing=payload.user_typing,
        safety_allowed=payload.safety_allowed,
        seed=payload.seed,
    )
    return InteractionResponse(
        agent=agent,
        decision=DecisionResponse(
            action=decision.action,
            reason=decision.reason,
            scores=decision.scores,
            content=content,
            blocked=decision.blocked,
            seed=decision.seed,
        ),
    )


@router.get("/agents/{agent_id}/memories")
def memories(
    agent_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    require_agent(db, agent_id)
    return list_memories(db, agent_id, limit)


@router.get("/agents/{agent_id}/decisions")
def decisions(
    agent_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    require_agent(db, agent_id)
    return list_decisions(db, agent_id, limit)


@router.get("/agents/{agent_id}/outbox")
def outbox(agent_id: str, db: Session = Depends(get_db)):
    require_agent(db, agent_id)
    return consume_outbox(db, agent_id)
