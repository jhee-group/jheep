import aioredis

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from .config import settings


@cache()
async def get_cache():
    return 1


async def init_cache():
    redis = aioredis.from_url(settings.redis_url, encoding="utf8", decode_response=True)
    FastAPICache.init(RedisBackend(redis), prefix="jheep-cache")
