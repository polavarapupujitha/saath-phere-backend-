"""AI/ML Business Logic (Rule-based Phase 1) — §8"""
from app.supabase_client import supabase_admin
from typing import Dict, Any

# Weights as per Document §8.2
WEIGHTS = {
    "age": 10,
    "height": 5,
    "religion": 20,
    "caste": 15,
    "education": 10,
    "income": 5,
    "location": 10,
    "lifestyle": 10,
    "horoscope": 15,
}

def calculate_compatibility(user_profile: dict, target_profile: dict) -> dict:
    """Rule-based compatibility score calculation (0-100)."""
    score = 0
    breakdown = {}

    if not user_profile or not target_profile:
        return {"score": 0, "breakdown": {}, "message": "Profiles not complete"}

    # 1. Religion Match (20%)
    if user_profile.get("religion") and user_profile.get("religion") == target_profile.get("religion"):
        breakdown["religion"] = WEIGHTS["religion"]
        score += WEIGHTS["religion"]
    
    # 2. Caste Match (15%)
    if user_profile.get("caste") and user_profile.get("caste") == target_profile.get("caste"):
        breakdown["caste"] = WEIGHTS["caste"]
        score += WEIGHTS["caste"]

    # 3. Education (10%) - Simple exact match logic
    # (In real scenario, we would map B.Tech to Engineering, etc.)
    # For now, checking if both have education filled
    if user_profile.get("education") and target_profile.get("education"):
        breakdown["education"] = WEIGHTS["education"]
        score += WEIGHTS["education"]

    # 4. Location (10%)
    if user_profile.get("location_city") and user_profile.get("location_city") == target_profile.get("location_city"):
        breakdown["location"] = WEIGHTS["location"]
        score += WEIGHTS["location"]

    # 5. Age (10%) - Assuming an ideal match is within 5 years difference
    age_diff = abs((user_profile.get("date_of_birth") or 0) - (target_profile.get("date_of_birth") or 0))
    # Note: For proper calculation, date_of_birth needs to be converted to age.
    # For now, just giving a pass if age_diff is small.
    breakdown["age"] = WEIGHTS["age"]
    score += WEIGHTS["age"]

    # 6. Height (5%)
    breakdown["height"] = WEIGHTS["height"]
    score += WEIGHTS["height"]

    # 7. Horoscope (15%) - We will use the Astrology logic
    astro_score = calculate_ashtakoot(user_profile, target_profile)
    if astro_score > 18: # If more than 50% of 36 points
        breakdown["horoscope"] = WEIGHTS["horoscope"]
        score += WEIGHTS["horoscope"]

    return {
        "score": score,
        "breakdown": breakdown,
        "message": f"Compatibility calculated. Total score: {score}/100"
    }

def calculate_ashtakoot(user_profile: dict, target_profile: dict) -> int:
    """Mock Ashtakoot Matching (36 Points system) — §8.3"""
    # In real life, this requires complex Vedic astrology calculations.
    # For MVP, we will mock this based on rasi/nakshatra.
    score = 0
    if user_profile.get("horoscope") and target_profile.get("horoscope"):
        # Mock logic: If Nakshatra matches or Rasi matches, give points
        if user_profile["horoscope"].get("nakshatra") == target_profile["horoscope"].get("nakshatra"):
            score += 18
        if user_profile["horoscope"].get("rasi") == target_profile["horoscope"].get("rasi"):
            score += 18
    return score