-- Users table (extends auth.users)
create table if not exists users (
    id uuid primary key references auth.users(id) on delete cascade,
    email text unique not null,
    role text default 'user',
    auth_provider text default 'email',
    email_verified boolean default false,
    profile_completed boolean default false,
    last_login_at timestamptz,
    last_login_ip inet,
    failed_login_attempts int default 0,
    locked_until timestamptz,
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

-- Audit logs table
create table if not exists audit_logs (
    id uuid primary key default gen_random_uuid(),
    action text not null,
    user_id uuid,
    ip_address text,
    device_fp text,
    success boolean,
    metadata jsonb,
    created_at timestamptz default now()
);

-- Enable RLS
alter table users enable row level security;
alter table audit_logs enable row level security;

-- Policy for users to read own profile
create policy "Users view own profile" on users
for select using (auth.uid() = id);