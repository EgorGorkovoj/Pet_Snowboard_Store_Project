from fastapi_users.authentication import RedisStrategy
from redis.asyncio import from_url

from src.core.config.app import settings

redis = from_url(settings.redis_url, decode_responses=True)


def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(redis, lifetime_seconds=3600)
