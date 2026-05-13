from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers import conversation, webhook
import os

app = FastAPI(
    title="ECO PRODUKT AI Sales Bot",
    description="Automatizovaný predajný asistent pre fotovoltické systémy",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(conversation.router, prefix="/api")
app.include_router(webhook.router, prefix="/webhook")

# Serve frontend from /static if it exists
frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_path, "index.html"))


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ecoprodukt-ai-bot"}
