import json
import logging
from typing import Any, Optional

import redis

from app.core.config import settings

logger = logging.getLogger(__name__)

_redis_client: Optional[redis.Redis] = None


def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
    return _redis_client


def cache_get(key: str) -> Optional[Any]:
    """Return the cached value or None if missing / Redis unavailable."""
    try:
        raw = get_redis().get(key)
        return json.loads(raw) if raw is not None else None
    except Exception as exc:
        logger.warning("Redis GET failed (%s): %s", key, exc)
        return None


def cache_set(key: str, value: Any, ttl: int = settings.CACHE_TTL_SECONDS) -> None:
    """Store value as JSON with a TTL. Silently skips on Redis errors."""
    try:
        get_redis().setex(key, ttl, json.dumps(value, default=str))
    except Exception as exc:
        logger.warning("Redis SET failed (%s): %s", key, exc)


def cache_delete(key: str) -> None:
    try:
        get_redis().delete(key)
    except Exception as exc:
        logger.warning("Redis DELETE failed (%s): %s", key, exc)


def cache_delete_pattern(pattern: str) -> None:
    """Invalidate all keys matching a glob pattern (e.g. 'matches:*')."""
    try:
        r = get_redis()
        keys = r.keys(pattern)
        if keys:
            r.delete(*keys)
    except Exception as exc:
        logger.warning("Redis pattern delete failed (%s): %s", pattern, exc)
