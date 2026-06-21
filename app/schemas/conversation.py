import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.message import MessageRole


class ConversationCreate(BaseModel):
    title: str = Field(default="New conversation", max_length=255)


class ConversationUpdate(BaseModel):
    title: str = Field(max_length=255)


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_id: uuid.UUID | None
    role: MessageRole
    content: str
    created_at: datetime


class PaginatedMessages(BaseModel):
    items: list[MessageResponse]
    total: int
    page: int
    page_size: int