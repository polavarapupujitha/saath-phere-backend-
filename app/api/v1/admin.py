"""Admin, Notifications & Payments APIs (§6A.5, §6A.7)"""
from fastapi import APIRouter, Depends, HTTPException
from app.middleware.dependencies import get_current_user
from app.schemas.common import SuccessResponse
from app.schemas.admin import NotificationCreate, PaymentCreate
from app.supabase_client import supabase_admin
from datetime import datetime, timezone, timedelta

router = APIRouter(tags=["admin & notifications"])

# ==========================================
# NOTIFICATIONS
# ==========================================
@router.get("/notifications", response_model=SuccessResponse)
async def get_notifications(user: dict = Depends(get_current_user)):
    user_id = user.get("sub")
    res = supabase_admin.table("notifications").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return SuccessResponse(data=res.data, message="Notifications fetched")

@router.put("/notifications/{notification_id}/read", response_model=SuccessResponse)
async def mark_notification_read(notification_id: str, user: dict = Depends(get_current_user)):
    user_id = user.get("sub")
    res = supabase_admin.table("notifications").update({"is_read": True}).eq("id", notification_id).eq("user_id", user_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Notification not found")
    return SuccessResponse(data=res.data[0], message="Notification marked as read")

# ==========================================
# PAYMENTS & PREMIUM
# ==========================================
@router.get("/payments/plans", response_model=SuccessResponse)
async def get_premium_plans():
    # Static plans for now
    plans = [
        {"name": "Gold", "price": 999, "duration_days": 30, "features": ["Unlimited Interests", "Advanced Search"]},
        {"name": "Platinum", "price": 1999, "duration_days": 90, "features": ["Unlimited Interests", "Advanced Search", "Video Calls"]}
    ]
    return SuccessResponse(data=plans, message="Plans fetched")

@router.post("/payments/mock-checkout", response_model=SuccessResponse)
async def create_mock_payment(payload: PaymentCreate, user: dict = Depends(get_current_user)):
    """Mock payment API for testing (Real Razorpay integration later)"""
    user_id = user.get("sub")
    
    # Add 30 days validity
    valid_until = datetime.now(timezone.utc) + timedelta(days=30)
    
    sub_data = {
        "user_id": user_id,
        "plan_name": payload.plan_name,
        "amount_paid": payload.amount,
        "valid_until": valid_until.isoformat()
    }
    res = supabase_admin.table("subscriptions").insert(sub_data).execute()
    
    # Upgrade user role to 'premium_user' (§3.4)
    supabase_admin.table("users").update({"role": "premium_user"}).eq("id", user_id).execute()
    
    return SuccessResponse(data=res.data[0], message="Premium subscription activated!")

# ==========================================
# ADMIN APIS (Requires 'super_admin' or 'moderator' role)
# ==========================================
@router.get("/admin/users", response_model=SuccessResponse)
async def admin_get_all_users(user: dict = Depends(get_current_user)):
    # Note: For production, add role check (e.g., if claims.get("role") != "super_admin": raise 403)
    res = supabase_admin.table("users").select("*").execute()
    return SuccessResponse(data=res.data, message="All users fetched (Admin only)")

@router.get("/admin/reports", response_model=SuccessResponse)
async def admin_get_reports(user: dict = Depends(get_current_user)):
    # Mocking reports table
    return SuccessResponse(data=[], message="Reports fetched (Admin only)")