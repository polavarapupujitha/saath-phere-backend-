"""Supabase clients — one anon (user-facing), one admin (service role)."""
from supabase import create_client, Client
from app.config import settings

# Anon client — used for signInWithPassword, signInWithOtp, OAuth
supabase_anon: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_ANON_KEY,
)

# Admin client — used to create/read users, bypass RLS where needed
supabase_admin: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY,
)