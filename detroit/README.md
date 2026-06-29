# Project Detroit

Project Detroit is an experimental persistent agent whose behavior changes through memory, internal state, needs, relationships, and slowly evolving personality traits. It can respond, ask, initiate, switch topics, reflect on memories, or choose silence.

## What this starter proves

- Persistent state stored in SQLite
- Structured event memory
- Short-term emotions
- Longer-term needs and relationship state
- Slow personality drift
- Competing action scores
- Hard blockers such as cooldowns and interruption limits
- Silence as a real decision
- Autonomous messages through an outbox
- A small browser interface for testing

The language renderer is intentionally simple. First prove that the agent chooses actions correctly. Add an LLM only after the decision kernel is understandable and testable.

## Requirements

- Python 3.12 recommended
- Git

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
fastapi dev app/main.py
```

Open:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

## Test

```bash
pytest
```

## Important endpoints

- `POST /api/agents` creates an agent.
- `GET /api/agents/{agent_id}` returns its full state.
- `POST /api/agents/{agent_id}/interact` records an interaction and runs a decision cycle.
- `POST /api/agents/{agent_id}/tick` simulates elapsed time and runs an autonomous decision.
- `GET /api/agents/{agent_id}/outbox` retrieves autonomous messages.
- `GET /api/agents/{agent_id}/memories` returns structured memories.
- `GET /api/agents/{agent_id}/decisions` returns score traces for debugging.

## Architecture

```text
event or time
    |
    v
memory update
    |
    v
short-term state update
    |
    v
slow personality drift
    |
    v
hard rules
    |
    v
action scoring + bounded noise
    |
    v
one winning action or silence
    |
    v
template renderer / later an LLM
```

## Development order

1. Tune state updates.
2. Tune decision scores.
3. Add better memory retrieval.
4. Add an LLM only as the language renderer.
5. Add richer autonomous scheduling.
6. Add evaluation and replay tools.
