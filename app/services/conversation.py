from uuid import UUID

from fastapi import HTTPException, status

from app.models.user import User
from app.repositories.conversation import ConversationRepository
from app.repositories.message import MessageRepository
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
    MessageResponse,
    PaginatedMessages,
)


class ConversationService:
    def __init__(
        self,
        conv_repo: ConversationRepository,
        msg_repo: MessageRepository,
    ) -> None:
        self.conv_repo = conv_repo
        self.msg_repo = msg_repo

    async def create(self, user: User, data: ConversationCreate) -> ConversationResponse:
        conv = await self.conv_repo.create(user.id, data.title)
        return ConversationResponse.model_validate(conv)

    async def list(self, user: User) -> list[ConversationResponse]:
        convs = await self.conv_repo.list_for_user(user.id)
        return [ConversationResponse.model_validate(c) for c in convs]

    async def rename(self, user: User, conv_id: UUID, data: ConversationUpdate) -> ConversationResponse:
        conv = await self._get_owned(conv_id, user.id)
        updated = await self.conv_repo.update_title(conv, data.title)
        return ConversationResponse.model_validate(updated)

    async def delete(self, user: User, conv_id: UUID) -> None:
        conv = await self._get_owned(conv_id, user.id)
        await self.conv_repo.delete(conv)

    async def get_messages(
        self, user: User, conv_id: UUID, page: int, page_size: int
    ) -> PaginatedMessages:
        await self._get_owned(conv_id, user.id)
        messages, total = await self.msg_repo.list_paginated(conv_id, page, page_size)
        return PaginatedMessages(
            items=[MessageResponse.model_validate(m) for m in messages],
            total=total,
            page=page,
            page_size=page_size,
        )

    async def _get_owned(self, conv_id: UUID, user_id: UUID):
        conv = await self.conv_repo.get_owned(conv_id, user_id)
        if not conv:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found")
        return conv