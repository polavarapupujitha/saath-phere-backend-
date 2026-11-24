"""Redis connection for sessions and rate-limiting."""
import redis
from app.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)