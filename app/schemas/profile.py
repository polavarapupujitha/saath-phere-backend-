"""Pydantic models for Profile APIs."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time

class ProfileBase(BaseModel):
    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    height_cm: Optional[int] = Field(None, ge=100, le=250)
    religion: Optional[str] = None
    caste: Optional[str] = None
    mother_tongue: Optional[str] = None
    location_city: Optional[str] = None
    location_state: Optional[str] = None
    about_me: Optional[str] = None

class FamilyDetailsBase(BaseModel):
    father_occupation: Optional[str] = None
    mother_occupation: Optional[str] = None
    siblings_count: Optional[int] = None
    family_type: Optional[str] = None
    family_values: Optional[str] = None

class EducationCareerBase(BaseModel):
    highest_education: Optional[str] = None
    college_name: Optional[str] = None
    occupation: Optional[str] = None
    company_name: Optional[str] = None
    annual_income_inr: Optional[int] = None

class HoroscopeBase(BaseModel):
    manglik_status: Optional[str] = None
    rasi: Optional[str] = None
    nakshatra: Optional[str] = None
    birth_time: Optional[time] = None
    birth_place: Optional[str] = None

class PartnerPreferencesBase(BaseModel):
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    height_min_cm: Optional[int] = None
    height_max_cm: Optional[int] = None
    religion_preference: Optional[str] = None
    education_preference: Optional[str] = None
    location_preference: Optional[str] = None