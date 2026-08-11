# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from router.chat import router as chat_router

app = FastAPI(title="MAF Graph Mail Agent", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)


@app.get("/health")
async def health():
    return {"status": "ok"}