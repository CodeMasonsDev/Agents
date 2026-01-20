from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

from livekit.api import AccessToken, VideoGrants, LiveKitAPI, CreateAgentDispatchRequest


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TokenRequest(BaseModel):
    room: str
    identity: str
    name: str | None = None

@app.post("/token")
async def create_token(data: TokenRequest):
    lk_url = os.environ["LIVEKIT_URL"]
    lk_key = os.environ["LIVEKIT_API_KEY"]
    lk_secret = os.environ["LIVEKIT_API_SECRET"]

    at = AccessToken(lk_key, lk_secret).with_identity(data.identity)
    if data.name:
        at = at.with_name(data.name)

    token = at.with_grants(
        VideoGrants(
            room_join=True,
            room=data.room,
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True,
        )
    )

    # ✅ Dispatch the agent job (async-safe)
    try:
        lkapi = LiveKitAPI(lk_url, lk_key, lk_secret)
        request = CreateAgentDispatchRequest(room=data.room)
        await lkapi.agent_dispatch.create_dispatch(request)
        await lkapi.aclose()  # important: close aiohttp session
    except Exception:
        import traceback
        print("DISPATCH FAILED")
        traceback.print_exc()

    return {"token": token.to_jwt(), "url": lk_url, "room": data.room}