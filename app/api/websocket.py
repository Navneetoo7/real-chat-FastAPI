from uuid import UUID

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status
from jose import JWTError

from app.core.security import get_user_id_from_token
from app.db.session import AsyncSessionLocal
from app.repositories.conversation import ConversationRepository
from app.schemas.websocket import WSClientMessage, WSErrorMessage, WSMessageType
from app.services.messaging import MessagingService, manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/conversations/{conversation_id}")
async def conversation_ws(
    websocket: WebSocket,
    conversation_id: UUID,
    token: str = Query(...),
) -> None:
    try:
        user_id = get_user_id_from_token(token, "access")
    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    async with AsyncSessionLocal() as session:
        conv = await ConversationRepository(session).get_owned(conversation_id, user_id)
        if not conv:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    redis = websocket.app.state.redis
    await manager.connect(conversation_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            msg = WSClientMessage.model_validate(data)
            if msg.type != WSMessageType.MESSAGE:
                continue
            async with AsyncSessionLocal() as session:
                service = MessagingService(session, redis)
                await service.handle_user_message(
                    conversation_id, user_id, msg.content, msg.client_message_id
                )
    except WebSocketDisconnect:
        manager.disconnect(conversation_id, websocket)
    except Exception as exc:
        await websocket.send_json(
            WSErrorMessage(code=4000, detail=str(exc)).model_dump(mode="json")
        )
        manager.disconnect(conversation_id, websocket)