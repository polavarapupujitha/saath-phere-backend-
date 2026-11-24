"""Audit log writer — §5.4 (1-year retention) with PII redaction (§4.1 L4)."""
import re
import logging
from app.supabase_client import supabase_admin
from datetime import datetime, timezone

logger = logging.getLogger("audit")


def redact_email(email: str) -> str:
    """u***@example.com — never log raw email."""
    if not email or "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    return f"{local[0]}***@{domain}"


def redact(text: str) -> str:
    """Redact any email pattern in free-form text."""
    return re.sub(r"([a-zA-Z0-9._%+-])[a-zA-Z0-9._%+-]*(@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
                  r"\1***\2", text)


def write_audit(
    action: str,
    user_id: str | None,
    ip: str,
    device_fp: str,
    success: bool,
    metadata: dict | None = None,
):
    """Insert into audit_logs table. Never raises — best effort."""
    try:
        row = {
            "action": action,
            "user_id": user_id,
            "ip_address": ip,
            "device_fp": device_fp,
            "success": success,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        supabase_admin.table("audit_logs").insert(row).execute()
    except Exception as e:
        # never let audit failure break auth flow
        logger.warning("audit write failed: %s", redact(str(e)))