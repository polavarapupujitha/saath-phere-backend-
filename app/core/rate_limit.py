"""Redis sliding-window rate limiter — §4.2 API Security."""
from fastapi import HTTPException, Request
from app.database import redis_client
from app.config import settings


def _key(scope: str, identifier: str) -> str:
    return f"rl:{scope}:{identifier}"


async def check_rate_limit(scope: str, identifier: str, limit_per_min: int):
    """
    Increment counter for (scope, identifier). Raise 429 if exceeded.
    Window = 60 seconds.
    """
    key = _key(scope, identifier)
    count = redis_client.incr(key)
    if count == 1:
        redis_client.expire(key, 60)

    if count > limit_per_min:
        ttl = redis_client.ttl(key)
        raise HTTPException(
            status_code=429,
            detail={
                "code": "RATE_LIMITED",
                "message": f"Too many requests. Retry in {ttl}s.",
                "details": {"retry_after": ttl},
            },
        )


async def rate_limit_login(request: Request, email: str = ""):
    """5/min per IP AND per email."""
    ip = request.client.host if request.client else "unknown"
    await check_rate_limit("login_ip", ip, settings.RATE_LOGIN)
    if email:
        await check_rate_limit("login_email", email.lower(), settings.RATE_LOGIN)


async def rate_limit_otp(request: Request, email: str = ""):
    ip = request.client.host if request.client else "unknown"
    await check_rate_limit("otp_ip", ip, settings.RATE_OTP)
    if email:
        await check_rate_limit("otp_email", email.lower(), settings.RATE_OTP)


async def rate_limit_password(request: Request, email: str = ""):
    ip = request.client.host if request.client else "unknown"
    await check_rate_limit("pwd_ip", ip, settings.RATE_PASSWORD)
    if email:
        await check_rate_limit("pwd_email", email.lower(), settings.RATE_PASSWORD)