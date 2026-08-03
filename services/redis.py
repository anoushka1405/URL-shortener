import redis

from config import REDIS_HOST, REDIS_PORT


redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)


def get_cached_url(short_code: str):
    return redis_client.get(short_code)


def set_cached_url(short_code: str, long_url: str):
    redis_client.set(
        short_code,
        long_url,
        ex=3600
    )