# backend/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from core.settings import get_settings
from router.auth import router as auth_router
from router.chat import router as chat_router

settings = get_settings()

app = FastAPI(title="MAF Graph Mail Agent", version="0.2.0")

# Signed cookie session — this is what "remembers" who's logged in
# between requests. No database needed.
app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET_KEY)

app.include_router(auth_router)
app.include_router(chat_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


# Serves frontend/index.html at "/" and frontend/app.js, style.css alongside it.
# Mounted last so it doesn't swallow the /auth and /chat routes above.
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")