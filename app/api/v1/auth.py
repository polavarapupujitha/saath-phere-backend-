"""All login-related endpoints."""
from fastapi import APIRouter, Request, HTTPException
from app.schemas.common import SuccessResponse
from app.schemas.auth import (
    LoginRequest, OTPRequest, OTPVerifyRequest,
    RefreshRequest, LogoutRequest, ForgotPasswordRequest, ResetPasswordRequest,
)
from app.services import auth_service
from app.services.auth_service import AuthError
from app.services import session_service
from app.core.rate_limit import rate_limit_login, rate_limit_otp, rate_limit_password
from app.core.security import device_fingerprint, client_ip, decode_supabase_jwt
from app.core.audit_log import write_audit, redact_email
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


def _err(code: str, message: str, status: int, details=None) -> HTTPException:
    return HTTPException(
        status_code=status,
        detail={"code": code, "message": message, "details": details or {}},
    )

def _build_user_payload(user_id: str, email: str, email_verified: bool,
                        role: str, profile_completed: bool, auth_provider: str) -> dict:
    return {
        "id": user_id,
        "email": email,
        "role": role,
        "email_verified": email_verified,
        "profile_completed": profile_completed,
        "auth_provider": auth_provider,
    }

# ============================================================
# 1. POST /auth/login — Email + Password
# ============================================================
@router.post("/login", response_model=SuccessResponse)
async def login(payload: LoginRequest, request: Request):
    await rate_limit_login(request, payload.email)
    ip = client_ip(request)
    fp = device_fingerprint(request)

    try:
        result = await auth_service.password_login(payload.email, payload.password)
    except AuthError as e:
        write_audit("login_failed", None, ip, fp, False,
                    {"reason": e.code, "email": redact_email(payload.email)})
        raise _err(e.code, e.message, e.status_code, e.details)

    user_id = result["user_id"]
    profile = await auth_service.get_or_create_user_profile(user_id, payload.email, "email")

    # Session TTL — v5.0 Open Question #2 (remember_me semantics) resolved: 30d
    ttl = settings.REFRESH_TOKEN_TTL_REMEMBER if payload.remember_me else settings.REFRESH_TOKEN_TTL
    session_service.store_session(user_id, fp, result["refresh_token"], ttl)

    write_audit("login_success", user_id, ip, fp, True,
                {"email": redact_email(payload.email), "remember_me": payload.remember_me})

    user_payload = _build_user_payload(
        user_id=user_id,
        email=payload.email,
        email_verified=result["email_verified"],
        role=profile["role"],
        profile_completed=profile["profile_completed"],
        auth_provider="email",
    )
    return SuccessResponse(
        data={
            "access_token": result["access_token"],
            "refresh_token": result["refresh_token"],
            "token_type": "bearer",
            "expires_in": result["expires_in"],
            "user": user_payload,
        },
        message="Login successful",
    )

# ============================================================
# 2. POST /auth/otp/send
# ============================================================
@router.post("/otp/send", response_model=SuccessResponse)
async def otp_send(payload: OTPRequest, request: Request):
    await rate_limit_otp(request, payload.email)
    try:
        out = await auth_service.otp_send(payload.email)
    except AuthError as e:
        raise _err(e.code, e.message, e.status_code, e.details)
    write_audit("otp_requested", None, client_ip(request), device_fingerprint(request),
                True, {"email": redact_email(payload.email)})
    return SuccessResponse(data=out, message="OTP sent to your email")

# ============================================================
# 3. POST /auth/otp/verify
# ============================================================
@router.post("/otp/verify", response_model=SuccessResponse)
async def otp_verify(payload: OTPVerifyRequest, request: Request):
    await rate_limit_otp(request, payload.email)
    ip = client_ip(request)
    fp = device_fingerprint(request)
    try:
        result = await auth_service.otp_verify(payload.email, payload.otp)
    except AuthError as e:
        write_audit("otp_failed", None, ip, fp, False,
                    {"reason": e.code, "email": redact_email(payload.email)})
        raise _err(e.code, e.message, e.status_code, e.details)

    user_id = result["user_id"]
    profile = await auth_service.get_or_create_user_profile(user_id, payload.email, "email")
    session_service.store_session(user_id, fp, result["refresh_token"], settings.REFRESH_TOKEN_TTL)
    write_audit("otp_verified", user_id, ip, fp, True, {"email": redact_email(payload.email)})

    return SuccessResponse(
        data={
            "access_token": result["access_token"],
            "refresh_token": result["refresh_token"],
            "token_type": "bearer",
            "expires_in": result["expires_in"],
            "user": _build_user_payload(
                user_id, payload.email, True,
                profile["role"], profile["profile_completed"], "email"
            ),
        },
        message="OTP verified",
    )

# ============================================================
# 4. GET /auth/google/redirect  +  GET /auth/google/callback
# ============================================================
@router.get("/google/redirect", response_model=SuccessResponse)
async def google_redirect(redirect_to: str = "http://localhost:3000/auth/callback"):
    url = auth_service.google_oauth_url(redirect_to)
    return SuccessResponse(data={"url": url}, message="Redirect to Google")

@router.get("/google/callback", response_model=SuccessResponse)
async def google_callback(request: Request):
    """Supabase redirects here with ?access_token=...&refresh_token=... OR with ?code=... (PKCE)."""
    ip = client_ip(request)
    fp = device_fingerprint(request)
    qp = dict(request.query_params)

    access_token = qp.get("access_token")
    refresh_token = qp.get("refresh_token")

    if not access_token:
        raise _err("OAUTH_FAILED", "Missing access token from Google", 400)

    try:
        claims = decode_supabase_jwt(access_token)
    except ValueError:
        raise _err("OAUTH_FAILED", "Invalid token", 401)

    user_id = claims.get("sub")
    email = claims.get("email", "")
    if not user_id:
        raise _err("OAUTH_FAILED", "No user in token", 401)

    profile = await auth_service.get_or_create_user_profile(user_id, email, "google")
    if refresh_token:
        session_service.store_session(user_id, fp, refresh_token, settings.REFRESH_TOKEN_TTL)

    write_audit("login_success", user_id, ip, fp, True,
                {"provider": "google", "email": redact_email(email)})

    return SuccessResponse(
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_TTL,
            "user": _build_user_payload(
                user_id, email, True,
                profile["role"], profile["profile_completed"], "google"
            ),
        },
        message="Google login successful",
    )

# ============================================================
# 5. POST /auth/refresh
# ============================================================
@router.post("/refresh", response_model=SuccessResponse)
async def refresh(payload: RefreshRequest):
    try:
        out = await auth_service.refresh_tokens(payload.refresh_token)
    except AuthError as e:
        raise _err(e.code, e.message, e.status_code, e.details)
    return SuccessResponse(data=out, message="Token refreshed")

# ============================================================
# 6. POST /auth/logout
# ============================================================
@router.post("/logout", response_model=SuccessResponse)
async def logout(payload: LogoutRequest, request: Request):
    ip = client_ip(request)
    fp = device_fingerprint(request)

    user_id = None
    try:
        if payload.refresh_token:
            resp = auth_service.supabase_anon.auth.refresh_session(payload.refresh_token)
            user_id = resp.user.id if resp.user else None
    except Exception:
        pass

    if user_id:
        session_service.invalidate_session(user_id, fp)
        write_audit("logout", user_id, ip, fp, True, {})

    return SuccessResponse(data={}, message="Logged out")

# ============================================================
# 7. POST /auth/password/forgot  +  POST /auth/password/reset
# ============================================================
@router.post("/password/forgot", response_model=SuccessResponse)
async def password_forgot(payload: ForgotPasswordRequest, request: Request):
    await rate_limit_password(request, payload.email)
    out = await auth_service.password_forgot(payload.email)
    write_audit("password_forgot", None, client_ip(request), device_fingerprint(request),
                True, {"email": redact_email(payload.email)})
    return SuccessResponse(data=out, message=out["message"])

@router.post("/password/reset", response_model=SuccessResponse)
async def password_reset(payload: ResetPasswordRequest, request: Request):
    try:
        out = await auth_service.password_reset(payload.access_token, payload.new_password)
    except AuthError as e:
        raise _err(e.code, e.message, e.status_code, e.details)
    write_audit("password_reset", None, client_ip(request), device_fingerprint(request), True, {})
    return SuccessResponse(data=out, message=out["message"])