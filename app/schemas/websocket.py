import uuid
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.models.message import MessageRole


class WSMessageType(str, Enum):
    MESSAGE = "message"
    ASSISTANT_REPLY = "assistant_reply"
    ERROR = "error"
    HISTORY = "history"


class WSClientMessage(BaseModel):
    type: WSMessageType = WSMessageType.MESSAGE
    content: str = Field(min_length=1, max_length=10000)
    client_message_id: uuid.UUID | None = None


class WSServerMessage(BaseModel):
    type: WSMessageType
    message_id: uuid.UUID
    conversation_id: uuid.UUID
    role: MessageRole
    content: str
    sender_id: uuid.UUID | None = None
    client_message_id: uuid.UUID | None = None


class WSErrorMessage(BaseModel):
    type: WSMessageType = WSMessageType.ERROR
    code: int
    detail: str
    extra: dict[str, Any] | None = None