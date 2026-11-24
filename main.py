"""FastAPI entrypoint — wires routers, CORS, security headers."""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from app.config import settings

# Import Routers
from app.api.v1.auth import router as auth_router
from app.api.v1.profiles import router as profile_router
from app.api.v1.interaction import router as interaction_router
from app.api.v1.chat import router as chat_router
from app.api.v1.admin import router as admin_router
from app.api.v1.ai_ml import router as ai_ml_router

app = FastAPI(
    title="Matrimony Backend",
    version="1.0.0",
    docs_url="/docs" if settings.APP_ENV == "development" else None,
)

# ---- CORS (§4.1 Layer 1) ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)

# ---- Security headers (§4.3) ----
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Swagger UI (/docs) load avvadaniki CDN allow chesamu, migatha APIs ki strict security
    if "/docs" in request.url.path or "/openapi.json" in request.url.path:
        response.headers["Content-Security-Policy"] = "default-src 'self' https://cdn.jsdelivr.net https://unpkg.com 'unsafe-inline' 'unsafe-eval'"
    else:
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
    return response

# ---- Global exception → standard error envelope (§10.3) ----
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    from app.core.audit_log import redact
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Something went wrong",
                "details": {"hint": redact(str(exc))} if settings.APP_ENV == "development" else {},
            },
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        },
    )

# ---- Routes ----
app.include_router(auth_router, prefix="/api/v1")
app.include_router(profile_router, prefix="/api/v1")
app.include_router(interaction_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(ai_ml_router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.APP_ENV}