from __future__ import annotations

import json
import time
from typing import Any

from fastapi import APIRouter, Depends, FastAPI, WebSocket
from prometheus_fastapi_instrumentator import Instrumentator

from .deps import Settings, settings

app = FastAPI(title=settings.app_name, openapi_tags=[
    {"name": "API"},
    {"name": "WebSocket"},
    {"name": "Metrics"},
])

# Placeholder routers
api_router = APIRouter(prefix="/api", tags=["API"])


@api_router.get("/brokers")
async def get_brokers() -> dict[str, str]:
    return {"detail": "broker list"}


@api_router.get("/sensors")
async def get_sensors() -> dict[str, str]:
    return {"detail": "sensor list"}


app.include_router(api_router)


@app.websocket("/ws/monitor")
async def monitor_ws(
    websocket: WebSocket, settings: Settings = Depends(lambda: settings)
) -> None:
    await websocket.accept()
    last = time.time()
    count = 0
    try:
        while True:
            data: Any = await websocket.receive_text()
            now = time.time()
            latency = now - last
            count += 1
            payload = {
                "sensor_id": data,
                "last": last,
                "count": count,
                "latency": latency,
            }
            await websocket.send_text(json.dumps(payload))
            last = now
    except Exception:
        await websocket.close()


Instrumentator().instrument(app).expose(app)
