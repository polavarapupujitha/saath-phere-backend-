"""Pydantic models for Chat & Messaging (§6)"""
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class ChatCreate(BaseModel):
    receiver_id: UUID

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    message_type: str = "text" # 'text', 'image', 'document', 'voice'
    file_url: Optional[str] = None

class MessageResponse(BaseModel):
    id: UUID
    sender_id: UUID
    content: Optional[str]
    message_type: str
    file_url: Optional[str]
    is_read: bool
    created_at: datetime