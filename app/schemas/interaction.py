"""Pydantic models for Search, Interests & Matches."""
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class InterestCreate(BaseModel):
    receiver_id: UUID
    message: Optional[str] = None # Optional message to send with interest

class InterestResponse(BaseModel):
    id: UUID
    sender_id: UUID
    receiver_id: UUID
    status: str
    created_at: str