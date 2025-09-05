from fastapi import FastAPI
from .v1.chat import router as chat_router

def register_routes(app: FastAPI):
    app.include_router(chat_router, prefix="/chat", tags=["chat"])