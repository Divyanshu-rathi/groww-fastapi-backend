import asyncio
import threading
from typing import Dict, Set, Optional
from fastapi import WebSocket


class WebSocketManager:


    def __init__(self):
        self._connections: Dict[int, Set[WebSocket]] = {}
        self._lock = threading.Lock()
        self._loop: Optional[asyncio.AbstractEventLoop] = None


    def set_event_loop(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

 
    async def connect(self, user_id: int, websocket: WebSocket):
        with self._lock:
            self._connections.setdefault(user_id, set()).add(websocket)


    async def disconnect(self, user_id: int, websocket: WebSocket):
        with self._lock:
            sockets = self._connections.get(user_id)
            if not sockets:
                return

            sockets.discard(websocket)
            if not sockets:
                self._connections.pop(user_id, None)

 
    def disconnect_user(self, user_id: int):
        with self._lock:
            sockets = list(self._connections.get(user_id, set()))
            self._connections.pop(user_id, None)

        for ws in sockets:
            self._schedule(ws.close())


    def send_to_user(self, user_id: int, message: dict):
        with self._lock:
            sockets = list(self._connections.get(user_id, set()))

        for ws in sockets:
            self._schedule(ws.send_json(message))


    def _schedule(self, coro):
        try:
            if self._loop and self._loop.is_running():
                asyncio.run_coroutine_threadsafe(coro, self._loop)
            else:
                asyncio.create_task(coro)
        except Exception:
            pass
