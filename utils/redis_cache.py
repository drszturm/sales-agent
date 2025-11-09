"""Redis cache layer for Evolution API data."""

import json
import logging
from typing import Any

import redis.asyncio as redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RedisCache:
    """Handles Redis caching operations."""

    def __init__(self, redis_url: str):
        """Initialize Redis client."""
        try:
            self.client = redis.from_url(
                redis_url, decode_responses=True, encoding="utf-8"
            )
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise Exception(f"Failed to connect to Redis: {e}")

    async def cache_event(self, key: str, data: Any, ttl: int = 3600):
        """Cache event data with TTL."""
        await self.client.setex(key, ttl, json.dumps(data))

    async def get_cached_event(self, key: str) -> dict | None:
        """Retrieve cached event."""
        data = await self.client.get(key)
        return json.loads(data) if data else None

    async def cache_instance_state(self, instance_name: str, state: dict):
        """Cache WhatsApp instance state."""
        self.client.hset("instances", instance_name, json.dumps(state))

    async def get_instance_state(self, instance_name: str) -> dict | None:
        """Get cached instance state."""
        state = await self.client.hget("instances", instance_name)
        return json.loads(state) if state else None

    async def get_recent_messages(self, instance_name: str, limit: int = 10):
        """Get recent messages from cache."""
        pattern = f"messages:{instance_name}"
        return await self.get_cached_event(pattern)
