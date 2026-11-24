"""Business logic for auth — thin wrappers around Supabase Auth."""
from typing import Optional
from app.supabase_client import supabase_anon, supabase_admin
from app.config import settings


class AuthError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, details=None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


async def password_login(email: str, password: str) -> dict:
    """Sign in via Supabase password grant."""
    try:
        resp = supabase_anon.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
    except Exception as e:
        msg = str(e).lower()
        if "invalid" in msg or "credentials" in msg:
            raise AuthError("INVALID_CREDENTIALS", "Invalid email or password", 401)
        if "email not confirmed" in msg:
            raise AuthError("EMAIL_NOT_VERIFIED", "Please verify your email first", 403)
        raise AuthError("LOGIN_FAILED", "Login failed", 500, {"raw": str(e)})

    if not resp.user:
        raise AuthError("INVALID_CREDENTIALS", "Invalid email or password", 401)

    return {
        "access_token": resp.session.access_token,
        "refresh_token": resp.session.refresh_token,
        "expires_in": resp.session.expires_in,
        "user_id": resp.user.id,
        "email": resp.user.email,
        "email_verified": bool(getattr(resp.user, "email_confirmed_at", None)),
    }


async def otp_send(email: str) -> dict:
    """Send OTP via Supabase magic-link/OTP."""
    try:
        supabase_anon.auth.sign_in_with_otp({"email": email})
    except Exception as e:
        raise AuthError("OTP_SEND_FAILED", "Could not send OTP", 500, {"raw": str(e)})
    return {"otp_sent": True, "expires_in": settings.OTP_TTL}


async def otp_verify(email: str, otp: str) -> dict:
    """Verify OTP and return session tokens."""
    try:
        resp = supabase_anon.auth.verify_otp(
            {"email": email, "token": otp, "type": "email"}
        )
    except Exception as e:
        msg = str(e).lower()
        if "expired" in msg:
            raise AuthError("OTP_EXPIRED", "OTP has expired", 400)
        if "invalid" in msg or "token" in msg:
            raise AuthError("OTP_INVALID", "Invalid OTP", 400)
        raise AuthError("OTP_VERIFY_FAILED", "OTP verification failed", 500, {"raw": str(e)})

    if not resp.user or not resp.session:
        raise AuthError("OTP_INVALID", "Invalid OTP", 400)

    return {
        "access_token": resp.session.access_token,
        "refresh_token": resp.session.refresh_token,
        "expires_in": resp.session.expires_in,
        "user_id": resp.user.id,
        "email": resp.user.email,
        "email_verified": True,
    }


def google_oauth_url(redirect_to: str) -> str:
    """Get Google OAuth URL from Supabase."""
    resp = supabase_anon.auth.sign_in_with_oauth(
        {"provider": "google", "options": {"redirect_to": redirect_to}}
    )
    return resp.url


async def refresh_tokens(refresh_token: str) -> dict:
    """Exchange refresh token for new access token."""
    try:
        resp = supabase_anon.auth.refresh_session(refresh_token)
    except Exception as e:
        raise AuthError("REFRESH_FAILED", "Could not refresh token", 401, {"raw": str(e)})

    if not resp.session:
        raise AuthError("REFRESH_FAILED", "Invalid refresh token", 401)

    return {
        "access_token": resp.session.access_token,
        "refresh_token": resp.session.refresh_token,
        "expires_in": resp.session.expires_in,
    }


async def password_forgot(email: str) -> dict:
    """Trigger Supabase password reset email."""
    try:
        supabase_anon.auth.reset_password_for_email(email)
    except Exception as e:
        # Don't leak whether email exists
        pass
    return {"message": "If the email exists, a reset link has been sent."}


async def password_reset(access_token: str, new_password: str) -> dict:
    """Set new password using recovery access token."""
    try:
        # Decode token to get user_id
        from app.core.security import decode_supabase_jwt
        claims = decode_supabase_jwt(access_token)
        user_id = claims.get("sub")

        if not user_id:
             raise AuthError("RESET_FAILED", "Invalid token", 400)

        supabase_admin.auth.admin.update_user_by_id(
            user_id,
            {"password": new_password},
        )
    except Exception as e:
        raise AuthError("RESET_FAILED", "Could not reset password", 400, {"raw": str(e)})
    return {"message": "Password updated successfully."}


async def get_or_create_user_profile(user_id: str, email: str, provider: str) -> dict:
    """
    Read users row; if missing, create with role='user' (§3.4).
    Returns dict: {role, profile_completed, auth_provider}
    """
    try:
        res = supabase_admin.table("users").select("*").eq("id", user_id).execute()
        if res.data:
            row = res.data[0]
            return {
                "role": row.get("role", "user"),
                "profile_completed": bool(row.get("profile_completed", False)),
                "auth_provider": row.get("auth_provider", provider),
            }
    except Exception:
        pass

    # create default row
    try:
        supabase_admin.table("users").insert({
            "id": user_id,
            "email": email,
            "role": "user",
            "auth_provider": provider,
            "profile_completed": False,
            "email_verified": provider != "email",
        }).execute()
    except Exception:
        # race condition — someone else inserted
        pass

    return {"role": "user", "profile_completed": False, "auth_provider": provider}