"""AI/ML APIs (§8) — Compatibility & Astrology"""
from fastapi import APIRouter, Depends, HTTPException
from app.middleware.dependencies import get_current_user
from app.schemas.common import SuccessResponse
from app.schemas.ai_ml import CompatibilityRequest, AstrologyMatchRequest
from app.services import ai_ml_service
from app.supabase_client import supabase_admin

router = APIRouter(tags=["AI/ML"])

@router.post("/ai/compatibility", response_model=SuccessResponse)
async def get_compatibility_score(payload: CompatibilityRequest, user: dict = Depends(get_current_user)):
    """Calculate compatibility score with another user (Rule-based §8.2)"""
    user_id = user.get("sub")
    
    # 1. Fetch both profiles
    my_profile = supabase_admin.table("profiles").select("*").eq("user_id", user_id).execute().data
    target_profile = supabase_admin.table("profiles").select("*").eq("user_id", payload.user_id).execute().data
    
    if not my_profile or not target_profile:
        raise HTTPException(status_code=404, detail="Profile not found for one or both users")
        
    # 2. Calculate Score
    result = ai_ml_service.calculate_compatibility(my_profile[0], target_profile[0])
    return SuccessResponse(data=result, message="Compatibility score calculated")

@router.post("/ai/astrology", response_model=SuccessResponse)
async def get_astrology_match(payload: AstrologyMatchRequest, user: dict = Depends(get_current_user)):
    """Get Astrology (Ashtakoot) match details (§8.3)"""
    user_id = user.get("sub")
    
    my_horoscope = supabase_admin.table("horoscope").select("*").eq("user_id", user_id).execute().data
    target_horoscope = supabase_admin.table("horoscope").select("*").eq("user_id", payload.user_id).execute().data
    
    if not my_horoscope or not target_horoscope:
        raise HTTPException(status_code=404, detail="Horoscope details not found")
        
    # For now, we are just returning the mocked match
    match_score = ai_ml_service.calculate_ashtakoot(
        {"horoscope": my_horoscope[0]}, 
        {"horoscope": target_horoscope[0]}
    )
    
    return SuccessResponse(
        data={"ashtakoot_score": match_score, "max_score": 36},
        message="Astrology match calculated"
    )