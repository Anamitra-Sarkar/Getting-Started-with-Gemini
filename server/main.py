from fastapi import FastAPI
from .db import init_db
from .routes_auth import router as auth_router
from .routes_ai import router as ai_router
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="Gemini Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGINS", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(auth_router)
app.include_router(ai_router)
