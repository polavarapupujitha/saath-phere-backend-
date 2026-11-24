"""Profile APIs — Create, Read, Update user details (§6A.1)"""
from fastapi import APIRouter, Depends
from app.middleware.dependencies import get_current_user
from app.schemas.common import SuccessResponse
from app.schemas.profile import (
    ProfileBase, FamilyDetailsBase, EducationCareerBase,
    HoroscopeBase, PartnerPreferencesBase
)
from app.supabase_client import supabase_admin

router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.get("/me", response_model=SuccessResponse)
async def get_my_profile(user: dict = Depends(get_current_user)):
    user_id = user.get("sub")
    profile = supabase_admin.table("profiles").select("*").eq("user_id", user_id).execute().data
    family = supabase_admin.table("family_details").select("*").eq("user_id", user_id).execute().data
    education = supabase_admin.table("education_career").select("*").eq("user_id", user_id).execute().data
    horoscope = supabase_admin.table("horoscope").select("*").eq("user_id", user_id).execute().data
    prefs = supabase_admin.table("partner_preferences").select("*").eq("user_id", user_id).execute().data
    
    return SuccessResponse(
        data={
            "profile": profile[0] if profile else {},
            "family": family[0] if family else {},
            "education": education[0] if education else {},
            "horoscope": horoscope[0] if horoscope else {},
            "preferences": prefs[0] if prefs else {},
        },
        message="Profile fetched successfully"
    )

@router.put("/me/basic", response_model=SuccessResponse)
async def update_basic_profile(payload: ProfileBase, user: dict = Depends(get_current_user)):
    user_id = user.get("sub")
    data = payload.model_dump(exclude_unset=True)
    
    existing = supabase_admin.table("profiles").select("id").eq("user_id", user_id).execute().data
    if existing:
        supabase_admin.table("profiles").update(data).eq("user_id", user_id).execute()
    else:
        data["user_id"] = user_id
        supabase_admin.table("profiles").insert(data).execute()
        
    return SuccessResponse(data=data, message="Basic profile updated")

@router.put("/me/family", response_model=SuccessResponse)
async def update_family(payload: FamilyDetailsBase, user: dict = Depends(get_current_user)):
    user_id = user.get("sub")
    data = payload.model_dump(exclude_unset=True)
    
    existing = supabase_admin.table("family_details").select("id").eq("user_id", user_id).execute().data
    if existing:
        supabase_admin.table("family_details").update(data).eq("user_id", user_id).execute()
    else:
        data["user_id"] = user_id
        supabase_admin.table("family_details").insert(data).execute()
        
    return SuccessResponse(data=data, message="Family details updated")

@router.put("/me/education", response_model=SuccessResponse)
async def update_education(payload: EducationCareerBase, user: dict = Depends(get_current_user)):
    user_id = user.get("sub")
    data = payload.model_dump(exclude_unset=True)
    existing = supabase_admin.table("education_career").select("id").eq("user_id", user_id).execute().data
    if existing:
        supabase_admin.table("education_career").update(data).eq("user_id", user_id).execute()
    else:
        data["user_id"] = user_id
        supabase_admin.table("education_career").insert(data).execute()
    return SuccessResponse(data=data, message="Education details updated")

@router.put("/me/horoscope", response_model=SuccessResponse)
async def update_horoscope(payload: HoroscopeBase, user: dict = Depends(get_current_user)):
    user_id = user.get("sub")
    data = payload.model_dump(exclude_unset=True)
    existing = supabase_admin.table("horoscope").select("id").eq("user_id", user_id).execute().data
    if existing:
        supabase_admin.table("horoscope").update(data).eq("user_id", user_id).execute()
    else:
        data["user_id"] = user_id
        supabase_admin.table("horoscope").insert(data).execute()
    return SuccessResponse(data=data, message="Horoscope details updated")

@router.put("/me/preferences", response_model=SuccessResponse)
async def update_preferences(payload: PartnerPreferencesBase, user: dict = Depends(get_current_user)):
    user_id = user.get("sub")
    data = payload.model_dump(exclude_unset=True)
    existing = supabase_admin.table("partner_preferences").select("id").eq("user_id", user_id).execute().data
    if existing:
        supabase_admin.table("partner_preferences").update(data).eq("user_id", user_id).execute()
    else:
        data["user_id"] = user_id
        supabase_admin.table("partner_preferences").insert(data).execute()
    return SuccessResponse(data=data, message="Partner preferences updated")