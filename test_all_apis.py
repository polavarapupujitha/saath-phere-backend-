import pytest
import httpx
import random
import string

BASE_URL = "http://127.0.0.1:8000/api/v1"

def generate_random_email():
    """Generate a unique email for testing"""
    return f"test_{''.join(random.choices(string.ascii_lowercase, k=5))}@example.com"

@pytest.mark.asyncio
async def test_all_apis():
    async with httpx.AsyncClient() as client:
        print("\n--- Starting API Automated Tests ---")
        
        # 1. TEST LOGIN
        # NOTE: Supabase lo test@example.com ane user create chesi undali (Auto-Confirm)
        email = "test@example.com"
        password = "Password@123"
        
        print(f"1. Testing Login with {email}...")
        login_data = {"email": email, "password": password, "remember_me": True}
        res = await client.post(f"{BASE_URL}/auth/login", json=login_data, timeout=10.0)
        
        if res.status_code != 200:
            print(f"❌ Login Failed! Make sure user {email} exists in Supabase. Error: {res.text}")
            return
        
        print("✅ Login Successful")
        token = res.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        user_id = res.json()["data"]["user"]["id"]

        # 2. TEST PROFILE UPDATE
        print("2. Testing Profile Update...")
        profile_data = {
            "full_name": "Test User",
            "date_of_birth": "1995-05-15",
            "gender": "male",
            "religion": "Hindu",
            "about_me": "This is an automated test profile."
        }
        res = await client.put(f"{BASE_URL}/profiles/me/basic", json=profile_data, headers=headers, timeout=10.0)
        if res.status_code == 200:
            print("✅ Profile Update Successful")
        else:
            print(f"❌ Profile Update Failed: {res.text}")

        # 3. TEST SEARCH
        print("3. Testing Search API...")
        res = await client.get(f"{BASE_URL}/search?religion=Hindu", headers=headers, timeout=10.0)
        if res.status_code == 200:
            print("✅ Search API Successful")
        else:
            print(f"❌ Search API Failed: {res.text}")

        # 4. TEST SEND INTEREST (Validation Check)
        print("4. Testing Send Interest...")
        interest_data = {"receiver_id": user_id}
        res = await client.post(f"{BASE_URL}/interests/send", json=interest_data, headers=headers, timeout=10.0)
        if res.status_code == 400 and "yourself" in res.text:
             print("✅ Interest API validation working (Cannot send to self)")
        else:
             print(f"❌ Interest API Failed: {res.text}")

        # 5. TEST CHAT START (Validation Check)
        print("5. Testing Chat Start...")
        chat_data = {"receiver_id": user_id}
        res = await client.post(f"{BASE_URL}/chats/start", json=chat_data, headers=headers, timeout=10.0)
        if res.status_code == 400 and "yourself" in res.text:
             print("✅ Chat API validation working (Cannot chat with self)")
        else:
             print(f"❌ Chat API Failed: {res.text}")

        # 6. TEST NOTIFICATIONS
        print("6. Testing Notifications...")
        res = await client.get(f"{BASE_URL}/notifications", headers=headers, timeout=10.0)
        if res.status_code == 200:
            print("✅ Notifications API Successful")
        else:
            print(f"❌ Notifications API Failed: {res.text}")

        # 7. TEST PREMIUM PAYMENTS (Mock)
        print("7. Testing Mock Payment...")
        pay_data = {"plan_name": "Gold", "amount": 999}
        res = await client.post(f"{BASE_URL}/payments/mock-checkout", json=pay_data, headers=headers, timeout=10.0)
        if res.status_code == 200:
            print("✅ Payment API Successful")
        else:
            print(f"❌ Payment API Failed: {res.text}")

        print("\n--- All Tests Completed! ---")