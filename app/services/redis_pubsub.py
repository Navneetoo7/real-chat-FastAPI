import asyncio
import json
import logging

from redis.asyncio import Redis

from app.services.messaging import REDIS_CHANNEL_PREFIX, manager

logger = logging.getLogger(__name__)


async def redis_subscriber_loop(redis: Redis) -> None:
    pubsub = redis.pubsub()
    await pubsub.psubscribe(f"{REDIS_CHANNEL_PREFIX}*")
    try:
        async for raw in pubsub.listen():
            if raw["type"] != "pmessage":
                continue
            try:
                payload = json.loads(raw["data"])
                conversation_id = payload["conversation_id"]
                await manager.broadcast_local(conversation_id, payload)
            except Exception:
                logger.exception("Failed to handle pubsub message")
    finally:
        await pubsub.unsubscribe()
        await pubsub.aclose()