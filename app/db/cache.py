import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# In-memory cache fallback when Redis is unavailable
_memory_cache: dict = {}

try:
    import redis
    from app.core.config import settings
    _redis_client = redis.Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
    )
    _redis_client.ping()
    USE_REDIS = True
    logger.info("Redis connected successfully")
except Exception:
    USE_REDIS = False
    logger.warning("Redis unavailable — using in-memory cache")


def cache_get(key: str) -> Optional[Any]:
    if USE_REDIS:
        try:
            raw = _redis_client.get(key)
            return json.loads(raw) if raw is not None else None
        except Exception:
            pass
    return _memory_cache.get(key)


def cache_set(key: str, value: Any, ttl: int = 30) -> None:
    if USE_REDIS:
        try:
            _redis_client.setex(key, ttl, json.dumps(value, default=str))
            return
        except Exception:
            pass
    _memory_cache[key] = value


def cache_delete(key: str) -> None:
    if USE_REDIS:
        try:
            _redis_client.delete(key)
        except Exception:
            pass
    _memory_cache.pop(key, None)


def cache_delete_pattern(pattern: str) -> None:
    if USE_REDIS:
        try:
            keys = _redis_client.keys(pattern)
            if keys:
                _redis_client.delete(*keys)
            return
        except Exception:
            pass
    # Memory cache pattern delete
    prefix = pattern.replace("*", "")
    keys_to_delete = [k for k in _memory_cache if k.startswith(prefix)]
    for k in keys_to_delete:
        del _memory_cache[k]