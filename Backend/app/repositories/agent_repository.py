"""Agent repository — database queries for Agent model."""

from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent import Agent


class AgentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, agent_id: int) -> Agent | None:
        result = await self.db.execute(select(Agent).where(Agent.id == agent_id))
        return result.scalar_one_or_none()

    async def get_active_by_id(self, agent_id: int) -> Agent | None:
        result = await self.db.execute(
            select(Agent).where(Agent.id == agent_id, Agent.is_active.is_(True))
        )
        return result.scalar_one_or_none()

    async def list_active(self) -> list[Agent]:
        result = await self.db.execute(
            select(Agent).where(Agent.is_active.is_(True)).order_by(Agent.id)
        )
        return list(result.scalars().all())

    async def find_by_username_and_url(self, username: str, base_url: str) -> Agent | None:
        """Tìm agent theo username + base_url (ưu tiên active, rồi mới nhất)."""
        result = await self.db.execute(
            select(Agent)
            .where(Agent.username == username, Agent.base_url == base_url)
            .order_by(Agent.is_active.desc(), Agent.updated_at.desc().nulls_last())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create(self, agent: Agent) -> Agent:
        self.db.add(agent)
        await self.db.commit()
        await self.db.refresh(agent)
        return agent

    async def update_fields(self, agent_id: int, values: dict) -> None:
        values["updated_at"] = datetime.now(UTC)
        await self.db.execute(
            update(Agent).where(Agent.id == agent_id).values(**values)
        )
        await self.db.commit()

    async def soft_delete(self, agent_id: int) -> None:
        await self.db.execute(
            update(Agent).where(Agent.id == agent_id).values(is_active=False)
        )
        await self.db.commit()

    async def refresh(self, agent: Agent) -> Agent:
        await self.db.refresh(agent)
        return agent
