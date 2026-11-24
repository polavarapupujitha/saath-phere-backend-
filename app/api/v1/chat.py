"""Chat & Messaging APIs (§6)"""
from fastapi import APIRouter, Depends, HTTPException
from app.middleware.dependencies import get_current_user
from app.schemas.common import SuccessResponse
from app.schemas.chat import MessageCreate, ChatCreate
from app.supabase_client import supabase_admin
from datetime import datetime, timezone, timedelta

router = APIRouter(prefix="/chats", tags=["chats"])

@router.get("", response_model=SuccessResponse)
async def get_my_chats(user: dict = Depends(get_current_user)):
    """Get active chats (last 24 hours)"""
    user_id = user.get("sub")
    
    # Document logic: Fetch chats where user is participant and not archived
    res = supabase_admin.table("chats").select("*").or_(f"participant1_id.eq.{user_id},participant2_id.eq.{user_id}").eq("is_archived", False).execute()
    
    return SuccessResponse(data=res.data, message="Chats fetched")

@router.post("/start", response_model=SuccessResponse)
async def start_chat(payload: ChatCreate, user: dict = Depends(get_current_user)):
    """Start a chat with a matched user"""
    user_id = user.get("sub")
    receiver_id = str(payload.receiver_id)

    if user_id == receiver_id:
        raise HTTPException(status_code=400, detail="Cannot chat with yourself")

    # Check if chat already exists
    existing = supabase_admin.table("chats").or_(
        f"and(participant1_id.eq.{user_id},participant2_id.eq.{receiver_id}),and(participant1_id.eq.{receiver_id},participant2_id.eq.{user_id})"
    ).execute()

    if existing.data:
        return SuccessResponse(data=existing.data[0], message="Chat already exists")

    # Create new chat
    new_chat = supabase_admin.table("chats").insert({
        "participant1_id": user_id,
        "participant2_id": receiver_id
    }).execute()

    return SuccessResponse(data=new_chat.data[0], message="Chat started successfully")

@router.get("/{chat_id}/messages", response_model=SuccessResponse)
async def get_messages(chat_id: str, user: dict = Depends(get_current_user)):
    """Get messages for a specific chat"""
    user_id = user.get("sub")
    
    # Verify user is part of the chat
    chat = supabase_admin.table("chats").select("*").eq("id", chat_id).or_(f"participant1_id.eq.{user_id},participant2_id.eq.{user_id}").execute()
    if not chat.data:
        raise HTTPException(status_code=403, detail="Access denied to this chat")

    messages = supabase_admin.table("messages").select("*").eq("chat_id", chat_id).eq("is_deleted", False).order("created_at", desc=False).execute()
    
    return SuccessResponse(data=messages.data, message="Messages fetched")

@router.post("/{chat_id}/messages", response_model=SuccessResponse)
async def send_message(chat_id: str, payload: MessageCreate, user: dict = Depends(get_current_user)):
    """Send a message to a chat"""
    user_id = user.get("sub")
    
    chat = supabase_admin.table("chats").select("*").eq("id", chat_id).or_(f"participant1_id.eq.{user_id},participant2_id.eq.{user_id}").execute()
    if not chat.data:
        raise HTTPException(status_code=403, detail="Access denied to this chat")

    msg_data = {
        "chat_id": chat_id,
        "sender_id": user_id,
        "content": payload.content,
        "message_type": payload.message_type,
        "file_url": payload.file_url
    }
    
    new_msg = supabase_admin.table("messages").insert(msg_data).execute()
    
    # Update last_message_at in chat
    supabase_admin.table("chats").update({"last_message_at": datetime.now(timezone.utc).isoformat()}).eq("id", chat_id).execute()

    return SuccessResponse(data=new_msg.data[0], message="Message sent")