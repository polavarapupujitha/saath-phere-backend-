"""Session tracking in Redis — device_fp → refresh token hash."""
import hashlib
from typing import Optional
from app.database import redis_client


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def _key(user_id: str, device_fp: str) -> str:
    return f"session:{user_id}:{device_fp}"


def store_session(user_id: str, device_fp: str, refresh_token: str, ttl: int) -> None:
    redis_client.setex(_key(user_id, device_fp), ttl, _hash_token(refresh_token))


def get_session(user_id: str, device_fp: str) -> Optional[str]:
    return redis_client.get(_key(user_id, device_fp))


def invalidate_session(user_id: str, device_fp: str) -> None:
    redis_client.delete(_key(user_id, device_fp))


def invalidate_all_sessions(user_id: str) -> int:
    """Used on password reset / account lock."""
    pattern = f"session:{user_id}:*"
    keys = list(redis_client.scan_iter(match=pattern))
    if keys:
        return redis_client.delete(*keys)
    return 0