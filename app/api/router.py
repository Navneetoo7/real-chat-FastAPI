from fastapi import APIRouter

from app.api import auth, conversations

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(conversations.router)
# Step 6: app.include_router(websocket.router) in main.py