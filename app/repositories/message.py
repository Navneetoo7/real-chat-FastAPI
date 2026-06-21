from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message


class MessageRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_paginated(
        self, conversation_id: UUID, page: int = 1, page_size: int = 50
    ) -> tuple[list[Message], int]:
        offset = (page - 1) * page_size
        count_result = await self.session.execute(
            select(func.count()).select_from(Message).where(Message.conversation_id == conversation_id)
        )
        total = count_result.scalar_one()
        result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .offset(offset)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def create(self, message: Message) -> Message:
        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)
        return message