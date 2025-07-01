import httpx
from config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET

async def get_google_user(code: str, redirect_uri: str):
    """Exchange Google OAuth code for user info"""
    async with httpx.AsyncClient() as client:
        # Exchange code for tokens
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            }
        )
        token_response.raise_for_status()
        tokens = token_response.json()

        # Get user info
        user_response = await client.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        user_response.raise_for_status()
        return user_response.json()