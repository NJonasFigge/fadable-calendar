
import asyncio
from datetime import date
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

import backend


FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
WEBSOCKETS: set[WebSocket] = set()

BACKEND = backend.get_backend()

APP = FastAPI()

# - CORS settings (to allow frontend access)
APP.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@APP.get("/api/get_week", response_class=HTMLResponse)
async def get_week(around_date_str: str) -> str:
    try:
        around_date = date.fromisoformat(around_date_str)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid start date format") from exc
    return BACKEND.render_period_html(around_date)


@APP.websocket("/ws")
async def get_websocket(ws: WebSocket):
    await ws.accept()
    WEBSOCKETS.add(ws)
    try:
        # - Send initial state
        while True:
            # - Keep the connection alive
            await asyncio.sleep(1)
    except Exception:
        pass
    finally:
        WEBSOCKETS.remove(ws)


# - IMPORTANT: This needs to be after the API routes (otherwise it overrides them)
APP.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
