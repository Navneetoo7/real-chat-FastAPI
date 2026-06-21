from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.dependencies import get_current_user, get_db_session
from app.models.user import User
from app.repositories.conversation import ConversationRepository
from app.repositories.message import MessageRepository
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
    PaginatedMessages,
)
from app.services.conversation import ConversationService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/conversations", tags=["conversations"])


def get_conversation_service(
    session: AsyncSession = Depends(get_db_session),
) -> ConversationService:
    return ConversationService(ConversationRepository(session), MessageRepository(session))


@router.post("", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    body: ConversationCreate,
    user: User = Depends(get_current_user),
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationResponse:
    return await service.create(user, body)


@router.get("", response_model=list[ConversationResponse])
async def list_conversations(
    user: User = Depends(get_current_user),
    service: ConversationService = Depends(get_conversation_service),
) -> list[ConversationResponse]:
    return await service.list(user)


@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def rename_conversation(
    conversation_id: UUID,
    body: ConversationUpdate,
    user: User = Depends(get_current_user),
    service: ConversationService = Depends(get_conversation_service),
) -> ConversationResponse:
    return await service.rename(user, conversation_id, body)


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: UUID,
    user: User = Depends(get_current_user),
    service: ConversationService = Depends(get_conversation_service),
) -> None:
    await service.delete(user, conversation_id)


@router.get("/{conversation_id}/messages", response_model=PaginatedMessages)
async def get_messages(
    conversation_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    user: User = Depends(get_current_user),
    service: ConversationService = Depends(get_conversation_service),
) -> PaginatedMessages:
    return await service.get_messages(user, conversation_id, page, page_size)