# Matrimony Backend API

A production-ready Matrimony Backend built with **FastAPI**, **Supabase**, and **Redis**. This project implements strict security, role-based access control, chat systems, and AI/ML compatibility features as per the final backend specification (v4.0 + v5.0).

## 🚀 Features

- **Authentication:** Email/Password, OTP, Google OAuth, JWT.
- **Profiles:** Detailed user profiles including Family, Education, Horoscope, and Partner Preferences.
- **Search & Match:** Advanced search, Send Interests, Mutual Matches.
- **Chat & Messaging:** 1-on-1 chat with 24-hour session logic.
- **AI/ML Features:** Rule-based Compatibility Score & Astrology (Ashtakoot) matching.
- **Admin & Notifications:** Admin controls, user verification, and real-time notifications.
- **Security:** 
  - Redis Rate Limiting (Anti-brute force)
  - Device Fingerprinting & Session Management
  - PII Redaction in Audit Logs
  - Row Level Security (RLS) in Database

## 🛠️ Technology Stack

- **Framework:** FastAPI (Python 3.11+)
- **Database:** Supabase (PostgreSQL)
- **Authentication:** Supabase Auth
- **Cache & Rate Limiter:** Redis (Memurai for Windows)
- **Testing:** Pytest & HTTPX

## 📋 Prerequisites

Before you begin, ensure you have installed:
- Python (3.11 or 3.12 recommended)
- Redis (or Memurai for Windows)
- A Supabase account and project

## ⚙️ Setup & Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd matrimony-backend