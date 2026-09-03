# backend/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from core.settings import get_settings
from router.auth import router as auth_router
from router.chat import router as chat_router
from router.teams_actions import router as teams_actions_router 

settings = get_settings()

app = FastAPI(title="MAF Graph Mail Agent", version="0.2.0")

app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET_KEY)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(teams_actions_router)  # ← and this


@app.get("/health")
async def health():
    return {"status": "ok"}


# Mounted LAST — this is critical. FastAPI checks routes in the order
# they're registered, so if this mount came before the routers above,
# it would swallow every request (including /teams-action, /chat,
# /auth/*) before they ever reached your actual endpoints.
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")