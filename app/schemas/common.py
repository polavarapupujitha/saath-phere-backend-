"""Standard response envelope — matches §10.2 / §10.3 of backend doc."""
from datetime import datetime, timezone
from typing import Any
from pydantic import BaseModel

def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

class SuccessResponse(BaseModel):
    success: bool = True
    data: Any
    message: str
    timestamp: str = ""

    def model_post_init(self, __context):
        if not self.timestamp:
            self.timestamp = _now()

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict = {}

class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
    timestamp: str = ""

    def model_post_init(self, __context):
        if not self.timestamp:
            self.timestamp = _now()