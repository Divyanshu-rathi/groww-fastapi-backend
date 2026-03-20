from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/live")
async def live_ws(
    websocket: WebSocket,
    user_id: int = Query(..., description="Logged-in user id"),
):

    await websocket.accept()

    ws_manager = websocket.app.state.ws_manager

  
    await ws_manager.connect(user_id, websocket)

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        await ws_manager.disconnect(user_id, websocket)

    except Exception:
        await ws_manager.disconnect(user_id, websocket)
