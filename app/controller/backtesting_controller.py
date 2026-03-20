from fastapi import APIRouter, HTTPException, Query, Depends, Header
from sqlalchemy.orm import Session

from app.service.backtesting_service import BacktestingService
from app.models.user import User
from app.db.session import get_db
from app.utils.exceptions import TradeException
from app.utils.json_sanitizer import sanitize_for_json

router = APIRouter(prefix="/backtesting", tags=["Backtesting"])


def get_current_user(
    x_user_id: int = Header(...),
    db: Session = Depends(get_db)
) -> User:
    user = db.query(User).filter(User.id == x_user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user


def get_backtesting_service(
    user: User = Depends(get_current_user)
):
    return BacktestingService(user)


@router.get("/expiries")
def get_expiries(
    exchange: str = Query(..., example="NSE"),
    underlying_symbol: str = Query(..., example="NIFTY"),
    year: int = Query(..., example=2024),
    month: int = Query(..., example=1),
    service: BacktestingService = Depends(get_backtesting_service)
):
    try:
        result = service.get_expiries(exchange, underlying_symbol, year, month)
        return {
            "status": "success",
            "data": sanitize_for_json(result)
        }
    except TradeException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/contracts")
def get_contracts(
    exchange: str = Query(..., example="NSE"),
    underlying_symbol: str = Query(..., example="NIFTY"),
    expiry_date: str = Query(..., example="2025-01-25"),
    service: BacktestingService = Depends(get_backtesting_service)
):
    try:
        result = service.get_contracts(exchange, underlying_symbol, expiry_date)
        return {
            "status": "success",
            "data": sanitize_for_json(result)
        }
    except TradeException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/candles")
def get_historical_candles(
    exchange: str = Query(..., example="NSE"),
    segment: str = Query(..., example="CASH"),
    groww_symbol: str = Query(..., example="NSE-WIPRO"),
    start_time: str = Query(..., example="2025-09-24 10:56:00"),
    end_time: str = Query(..., example="2025-09-24 12:00:00"),
    candle_interval: int = Query(15, example=15),
    service: BacktestingService = Depends(get_backtesting_service)
):
    try:
        result = service.get_historical_candles(
            exchange,
            segment,
            groww_symbol,
            start_time,
            end_time,
            candle_interval
        )
        return {
            "status": "success",
            "data": sanitize_for_json(result)
        }
    except TradeException as e:
        raise HTTPException(status_code=400, detail=str(e))
