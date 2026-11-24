"""Pydantic models for login APIs — §4.2 Input Validation."""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    remember_me: bool = False

class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)

    @field_validator("otp")
    @classmethod
    def otp_digits(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("OTP must be 6 digits")
        return v

class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=10)

class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    access_token: str
    new_password: str = Field(..., min_length=8, max_length=128)

class UserPublic(BaseModel):
    id: str
    email: str
    role: str
    email_verified: bool
    profile_completed: bool
    auth_provider: str = "email"