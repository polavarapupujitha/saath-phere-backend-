"""JWT helpers + device fingerprint."""
import hashlib
from fastapi import Request, HTTPException
from app.supabase_client import supabase_admin

def decode_supabase_jwt(token: str) -> dict:
    """Verify a Supabase-issued JWT using Supabase Admin API."""
    try:
        # Admin API call to get user directly from token
        user_response = supabase_admin.auth.get_user(token)
        if not user_response or not user_response.user:
            raise ValueError("Invalid token")
        
        # Convert Supabase user object to dict format we need
        return {
            "sub": user_response.user.id,
            "email": user_response.user.email,
            "role": user_response.user.user_metadata.get("role", "user")
        }
    except Exception as e:
        raise ValueError(f"Invalid token: {e}")

def device_fingerprint(request: Request) -> str:
    ua = request.headers.get("user-agent", "")
    ip = request.client.host if request.client else ""
    raw = f"{ua}|{ip}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]

def client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"