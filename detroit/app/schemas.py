from datetime import datetime

from pydantic import BaseModel, Field


class CreateAgentRequest(BaseModel):
    agent_id: str = Field(min_length=1, max_length=100)
    name: str = Field(default="Detroit", min_length=1, max_length=100)


class InteractionRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    topic: str | None = Field(default=None, max_length=200)
    valence: float = Field(default=0.0, ge=-1.0, le=1.0)
    novelty: float = Field(default=0.5, ge=0.0, le=1.0)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    unresolved: bool = False
    user_typing: bool = False
    safety_allowed: bool = True
    seed: int | None = None


class EventRequest(BaseModel):
    event_type: str = Field(default="user_interaction", max_length=50)
    summary: str = Field(min_length=1, max_length=1000)
    topic: str | None = Field(default=None, max_length=200)
    valence: float = Field(default=0.0, ge=-1.0, le=1.0)
    novelty: float = Field(default=0.5, ge=0.0, le=1.0)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    unresolved: bool = False


class TickRequest(BaseModel):
    minutes: float = Field(default=10.0, ge=0.0, le=10080.0)
    user_typing: bool = False
    safety_allowed: bool = True
    seed: int | None = None


class AgentResponse(BaseModel):
    id: str
    name: str
    state: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DecisionResponse(BaseModel):
    action: str
    reason: str
    scores: dict[str, float]
    content: str | None
    blocked: bool
    seed: int


class InteractionResponse(BaseModel):
    agent: AgentResponse
    decision: DecisionResponse
