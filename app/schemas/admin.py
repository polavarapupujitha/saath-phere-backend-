"""Pydantic models for Notifications & Payments."""
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class NotificationCreate(BaseModel):
    title: str
    message: str
    type: str = "general"

class PaymentCreate(BaseModel):
    plan_name: str
    amount: float