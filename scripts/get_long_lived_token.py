"""Exchange short-lived Meta token for a 60-day Long-Lived Access Token."""

import sys
import httpx
from app.config import settings

def exchange_token(short_lived_token: str) -> str:
    app_id = settings.meta_app_id
    app_secret = settings.meta_app_secret
    
    if not app_id or not app_secret:
        print("Error: META_APP_ID and META_APP_SECRET must be set in .env")
        sys.exit(1)
        
    url = "https://graph.facebook.com/v20.0/oauth/access_token"
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_lived_token.strip(),
    }
    
    print(f"Exchanging token with Meta for App ID: {app_id}...")
    res = httpx.get(url, params=params)
    data = res.json()
    
    if res.status_code != 200 or "access_token" not in data:
        print("Error from Meta:", data)
        sys.exit(1)
        
    long_lived_token = data["access_token"]
    expires_in = data.get("expires_in", 5184000)
    days = expires_in // 86400
    print(f"\nSUCCESS! Retrieved 60-day Long-Lived Token (valid for ~{days} days):")
    print(f"\n{long_lived_token}\n")
    return long_lived_token

if __name__ == "__main__":
    token = sys.argv[1] if len(sys.argv) > 1 else settings.instagram_access_token
    if not token:
        print("Usage: python -m scripts.get_long_lived_token <SHORT_LIVED_TOKEN>")
        sys.exit(1)
    exchange_token(token)
