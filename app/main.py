from dotenv import load_dotenv
load_dotenv()

import asyncio
from fastapi import FastAPI,  Request
from fastapi.responses import JSONResponse
from app.utils.exceptions import TradeException
from app.controller.trade_controller import router as trade_router
from app.controller.instrument_controller import router as instrument_router
from app.controller.portfolio_controller import router as portfolio_router
from app.controller.margin_controller import router as margin_router
from app.controller.historical_controller import router as historical_router
from app.controller.backtesting_controller import router as backtesting_router
from app.controller.live_data_controller import router as live_data_router
from app.controller.user_controller import router as user_router
from app.controller.ws_controller import router as ws_router
from app.controller.groww_auth_controller import router as groww_auth_router
from app.controller.ltp_controller import router as live_router
from app.controller.live_feed_controller import router as livefeed_router
from app.websocket.ws_manager import WebSocketManager
from app.db.init_db import init_db

app = FastAPI(title="Groww Trading Backend")

@app.on_event("startup")
def startup_event():
    init_db()
    print("Database ready")

    loop = asyncio.get_running_loop()
    app.state.ws_manager.set_event_loop(loop)

ws_manager = WebSocketManager()
app.state.ws_manager = ws_manager

app.include_router(trade_router)
app.include_router(instrument_router)
app.include_router(portfolio_router)
app.include_router(margin_router) 
app.include_router(historical_router)
app.include_router(backtesting_router)
app.include_router(live_data_router)
app.include_router(user_router)
app.include_router(ws_router)
app.include_router(groww_auth_router)
app.include_router(live_router)
app.include_router(livefeed_router)

@app.get("/")
def health():
    return {"status": "Groww API Backend Running"}

@app.exception_handler(TradeException)
async def trade_exception_handler(request: Request, exc: TradeException):
    return JSONResponse(
        status_code=403,
        content={
            "success": False,
            "message": str(exc)
        }
    )


