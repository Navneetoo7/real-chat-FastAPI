import uuid
from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id", index=True)
    sender_id: uuid.UUID | None = Field(default=None, foreign_key="users.id")
    role: MessageRole
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)