import asyncio
from datetime import datetime, timezone
import logging

from sqlalchemy import select

from app.config import settings
from app.database import SessionLocal
from app.models import AgentProfile
from app.services.agent_service import process_tick


logger = logging.getLogger(__name__)


async def autonomy_loop() -> None:
    previous = datetime.now(timezone.utc)

    while True:
        await asyncio.sleep(settings.autonomy_tick_seconds)
        now = datetime.now(timezone.utc)
        elapsed_minutes = max((now - previous).total_seconds() / 60.0, 0.0)
        previous = now

        with SessionLocal() as db:
            agents = list(db.scalars(select(AgentProfile)))
            for agent in agents:
                try:
                    process_tick(
                        db,
                        agent=agent,
                        minutes=elapsed_minutes,
                        user_typing=False,
                        safety_allowed=True,
                        seed=None,
                    )
                except Exception:
                    db.rollback()
                    logger.exception("Autonomy tick failed for agent %s", agent.id)
