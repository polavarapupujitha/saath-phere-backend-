"""Reusable FastAPI dependency: get current user from Bearer token."""
from fastapi import Request, HTTPException
from app.core.security import decode_supabase_jwt


async def get_current_user(request: Request) -> dict:
    auth = request.headers.get("authorization", "")
    if not auth.lower().startswith("bearer "):
        raise HTTPException(
            status_code=401,
            detail={"code": "UNAUTHENTICATED", "message": "Missing bearer token", "details": {}},
        )
    token = auth.split(" ", 1)[1]
    try:
        claims = decode_supabase_jwt(token)
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail={"code": "INVALID_TOKEN", "message": "Invalid or expired token", "details": {}},
        )
    return claims


async def require_role(*allowed_roles: str):
    """Dependency factory for RBAC — §3.5."""
    async def _inner(request: Request) -> dict:
        claims = await get_current_user(request)
        role = claims.get("role") or claims.get("user_metadata", {}).get("role", "user")
        if allowed_roles and role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail={"code": "FORBIDDEN", "message": "Insufficient role", "details": {"required": list(allowed_roles)}},
            )
        return claims
    return _inner