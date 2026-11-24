"""Pydantic models for AI/ML Features (§8)"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any

class CompatibilityRequest(BaseModel):
    user_id: str

class AstrologyMatchRequest(BaseModel):
    user_id: str

class CompatibilityResponse(BaseModel):
    score: int
    breakdown: Dict[str, int]
    message: str