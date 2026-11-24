"""Search, Interests & Matches APIs (§6A.2, §6A.3)"""
from fastapi import APIRouter, Depends, HTTPException
from app.middleware.dependencies import get_current_user
from app.schemas.common import SuccessResponse
from app.schemas.interaction import InterestCreate
from app.supabase_client import supabase_admin

router = APIRouter(tags=["interactions"])

# ==========================================
# SEARCH API
# ==========================================
@router.get("/search", response_model=SuccessResponse)
async def search_profiles(
    religion: str = None, 
    gender: str = None, 
    min_age: int = None,
    user: dict = Depends(get_current_user)
):
    """
    Search profiles based on filters. 
    """
    query = supabase_admin.table("profiles").select("*, users(email)")
    
    if religion:
        query = query.eq("religion", religion)
    if gender:
        query = query.eq("gender", gender)
    
    try:
        res = query.execute()
        return SuccessResponse(data=res.data, message="Search results fetched")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# ==========================================
# INTERESTS APIs
# ==========================================
@router.post("/interests/send", response_model=SuccessResponse)
async def send_interest(payload: InterestCreate, user: dict = Depends(get_current_user)):
    sender_id = user.get("sub")
    
    if str(payload.receiver_id) == sender_id:
        raise HTTPException(status_code=400, detail="Cannot send interest to yourself")

    data = {
        "sender_id": sender_id,
        "receiver_id": str(payload.receiver_id),
        "status": "pending"
    }
    
    try:
        res = supabase_admin.table("interests").insert(data).execute()
        return SuccessResponse(data=res.data[0], message="Interest sent successfully")
    except Exception as e:
        if "duplicate" in str(e).lower():
            raise HTTPException(status_code=400, detail="Interest already sent")
        # Proper error handling to prevent server crash
        raise HTTPException(status_code=500, detail=f"Failed to send interest: {str(e)}")

@router.get("/interests/received", response_model=SuccessResponse)
async def received_interests(user: dict = Depends(get_current_user)):
    user_id = user.get("sub")
    try:
        res = supabase_admin.table("interests").select("*, sender:users!sender_id(email), sender_profile:profiles!sender_id(*)").eq("receiver_id", user_id).eq("status", "pending").execute()
        return SuccessResponse(data=res.data, message="Received interests fetched")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch received interests: {str(e)}")

@router.put("/interests/{interest_id}/accept", response_model=SuccessResponse)
async def accept_interest(interest_id: str, user: dict = Depends(get_current_user)):
    user_id = user.get("sub")
    
    try:
        # 1. Verify interest exists and is for this user
        interest = supabase_admin.table("interests").select("*").eq("id", interest_id).eq("receiver_id", user_id).execute().data
        if not interest:
            raise HTTPException(status_code=404, detail="Interest not found")
            
        # 2. Update status to accepted
        supabase_admin.table("interests").update({"status": "accepted"}).eq("id", interest_id).execute()
        
        # 3. Create a Match
        sender_id = interest[0]["sender_id"]
        # Ensure consistent ordering for unique constraint (user1 < user2)
        u1, u2 = sorted([user_id, sender_id])
        
        # Check if match already exists to prevent duplicate error
        existing_match = supabase_admin.table("matches").select("*").eq("user1_id", u1).eq("user2_id", u2).execute().data
        if not existing_match:
            supabase_admin.table("matches").insert({"user1_id": u1, "user2_id": u2}).execute()

        return SuccessResponse(data={}, message="Interest accepted and Match created!")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to accept interest: {str(e)}")

@router.get("/matches", response_model=SuccessResponse)
async def get_matches(user: dict = Depends(get_current_user)):
    user_id = user.get("sub")
    try:
        res = supabase_admin.table("matches").select("*").or_(f"user1_id.eq.{user_id},user2_id.eq.{user_id}").execute()
        return SuccessResponse(data=res.data, message="Matches fetched")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch matches: {str(e)}")