
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from pathlib import Path


FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

APP = FastAPI()

STATE = dict(active=False)
WEBSOCKETS: set[WebSocket] = set()


@APP.post("/toggle")
async def toggle_state():
    # - Toggle the state
    STATE["active"] = not STATE["active"]
    # - Notify all connected websockets
    for websocket in list(WEBSOCKETS):
        try:
            await websocket.send_json(STATE)
        except Exception:
            pass
    return STATE


@APP.websocket("/ws")
async def get_websocket(ws: WebSocket):
    await ws.accept()
    WEBSOCKETS.add(ws)
    try:
        # - Initial state senden
        await ws.send_json(STATE)
        while True:
            # - Keep the connection alive
            await asyncio.sleep(1)
    except Exception:
        pass
    finally:
        WEBSOCKETS.remove(ws)


# - IMPORTANT: This needs to be after the API routes (otherwise it overrides them)
APP.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
