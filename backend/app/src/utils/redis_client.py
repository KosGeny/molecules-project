import redis.asyncio as redis
from typing import Any, Optional
from ...config.settings import settings
from .logger import app_logger
import pickle
import asyncio
import time


class RedisClient:
    def __init__(self):
        self.redis_url = settings.REDIS_URL
        self.redis_client = None
        self._connection_lock = asyncio.Lock()
        self._last_failed_connection_time = 0
        self._connection_cooldown = 30

    async def connect(self):
        async with self._connection_lock:
            current_time = time.time()
            if (
                current_time - self._last_failed_connection_time
                < self._connection_cooldown
            ):
                app_logger.debug("Connection attempt skipped due to cooldown")
                return False

            try:
                self.redis_client = redis.from_url(
                    self.redis_url,
                    decode_responses=False,
                    retry_on_timeout=False,
                    socket_keepalive=True,
                    socket_connect_timeout=2,
                    socket_timeout=2,
                )
                await asyncio.wait_for(self.redis_client.ping(), timeout=3)
                app_logger.info("Connected to Redis successfully")
                return True
            except Exception as e:
                self._last_failed_connection_time = current_time
                app_logger.error(f"Failed to connect to Redis: {e}")
                return False

    async def disconnect(self):
        async with self._connection_lock:
            if self.redis_client:
                try:
                    await self.redis_client.close()
                    app_logger.info("Disconnected from Redis")
                except Exception as e:
                    app_logger.error(f"Error disconnecting from Redis: {e}")

    async def _ensure_connected(self) -> bool:
        if self.redis_client is None:
            return await self.connect()

        try:
            await asyncio.wait_for(self.redis_client.ping(), timeout=2)
            return True
        except Exception:
            return await self.connect()

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        if not await self._ensure_connected():
            return False

        try:
            serialized_value = pickle.dumps(value)
            result = await asyncio.wait_for(
                self.redis_client.set(key, serialized_value, ex=expire), timeout=3
            )
            app_logger.info(f"Set cache key: {key}, expire: {expire}")
            return result
        except Exception as e:
            app_logger.error(f"Failed to set cache: {e}")
            await self.disconnect()
            return False

    async def get(self, key: str) -> Optional[Any]:
        if not await self._ensure_connected():
            return None

        try:
            value = await asyncio.wait_for(self.redis_client.get(key), timeout=3)
            if value is not None:
                deserialized_value = pickle.loads(value)
                app_logger.info(f"Cache HIT for key: {key}")
                return deserialized_value
            else:
                app_logger.info(f"Cache MISS for key: {key}")
                return None
        except Exception as e:
            app_logger.error(f"Failed to get from cache: {e}")
            await self.disconnect()
            return None

    async def delete(self, keys: list) -> bool:
        if not await self._ensure_connected() or not keys:
            return False

        try:
            result = await asyncio.wait_for(self.redis_client.delete(*keys), timeout=3)
            app_logger.info(f"Deleted {result} keys from cache")
            return result > 0
        except Exception as e:
            app_logger.error(f"Failed to delete cache keys: {e}")
            await self.disconnect()
            return False

    async def flush_pattern(self, pattern: str) -> bool:
        if not await self._ensure_connected():
            return False

        try:
            keys = await asyncio.wait_for(self.redis_client.keys(pattern), timeout=3)
            if keys:
                result = await asyncio.wait_for(
                    self.redis_client.delete(*keys), timeout=3
                )
                app_logger.info(f"Flushed {result} keys matching pattern: {pattern}")
                return True
            return True
        except Exception as e:
            app_logger.error(f"Failed to flush cache pattern {pattern}: {e}")
            await self.disconnect()
            return False

    async def is_connected(self) -> bool:
        if self.redis_client is None:
            return False

        try:
            await asyncio.wait_for(self.redis_client.ping(), timeout=2)
            return True
        except Exception:
            return False

    async def reconnect_if_needed(self):
        """Reconnect to Redis if connection is lost"""
        await self.connect()


redis_client = RedisClient()
