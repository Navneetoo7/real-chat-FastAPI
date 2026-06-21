import json
from uuid import UUID

from fastapi import WebSocket
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message, MessageRole
from app.repositories.message import MessageRepository
from app.schemas.websocket import WSServerMessage, WSMessageType
from app.services.ai_mock import generate_reply

REDIS_CHANNEL_PREFIX = "conversation:"


class ConnectionManager:
    def __init__(self) -> None:
        self.active: dict[UUID, set[WebSocket]] = {}

    async def connect(self, conversation_id: UUID, ws: WebSocket) -> None:
        await ws.accept()
        self.active.setdefault(conversation_id, set()).add(ws)

    def disconnect(self, conversation_id: UUID, ws: WebSocket) -> None:
        if conversation_id in self.active:
            self.active[conversation_id].discard(ws)
            if not self.active[conversation_id]:
                del self.active[conversation_id]

    async def broadcast_local(self, conversation_id: UUID, payload: dict) -> None:
        dead: list[WebSocket] = []
        for ws in self.active.get(conversation_id, set()):
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(conversation_id, ws)


manager = ConnectionManager()


class MessagingService:
    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        self.msg_repo = MessageRepository(session)
        self.redis = redis

    async def handle_user_message(
        self,
        conversation_id: UUID,
        user_id: UUID,
        content: str,
        client_message_id: UUID | None,
    ) -> None:
        user_msg = await self.msg_repo.create(
            Message(
                conversation_id=conversation_id,
                sender_id=user_id,
                role=MessageRole.USER,
                content=content,
            )
        )
        await self._publish(conversation_id, user_msg, client_message_id)

        reply_text = await generate_reply(content)
        assistant_msg = await self.msg_repo.create(
            Message(
                conversation_id=conversation_id,
                sender_id=None,
                role=MessageRole.ASSISTANT,
                content=reply_text,
            )
        )
        await self._publish(conversation_id, assistant_msg, None)

    async def _publish(
        self,
        conversation_id: UUID,
        message: Message,
        client_message_id: UUID | None,
    ) -> None:
        ws_type = (
            WSMessageType.MESSAGE
            if message.role == MessageRole.USER
            else WSMessageType.ASSISTANT_REPLY
        )
        payload = WSServerMessage(
            type=ws_type,
            message_id=message.id,
            conversation_id=message.conversation_id,
            role=message.role,
            content=message.content,
            sender_id=message.sender_id,
            client_message_id=client_message_id,
        ).model_dump(mode="json")
        await manager.broadcast_local(conversation_id, payload)
        channel = f"{REDIS_CHANNEL_PREFIX}{conversation_id}"
        await self.redis.publish(channel, json.dumps(payload))