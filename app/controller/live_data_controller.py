from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.user import User
from app.service.live_data_service import LiveDataService
from app.utils.exceptions import TradeException
from app.utils.json_sanitizer import sanitize_for_json


router = APIRouter(prefix="/live", tags=["Live Market Data"])


def get_current_user(
    x_user_id: int = Header(...),
    db: Session = Depends(get_db)
) -> User:
    user = db.query(User).filter(User.id == x_user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user


def get_live_data_service(
    user: User = Depends(get_current_user)
):
    return LiveDataService(user)



@router.get("/quote")
def get_live_quote(
    trading_symbol: str = Query(..., example="NIFTY"),
    exchange: str = Query(..., example="NSE"),
    segment: str = Query(..., example="CASH"),
    service: LiveDataService = Depends(get_live_data_service)
):
    try:
        result = service.get_quote(
            trading_symbol=trading_symbol,
            exchange=exchange,
            segment=segment
        )

        return {
            "status": "success",
            "trading_symbol": trading_symbol,
            "quote": sanitize_for_json(result)
        }

    except TradeException as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.get("/ohlc")
def get_live_ohlc(
    segment: str = Query(..., example="CASH"),
    exchange_trading_symbols: List[str] = Query(
        ...,
        example=["NSE_NIFTY", "NSE_RELIANCE"]
    ),
    service: LiveDataService = Depends(get_live_data_service)
):
    try:
        result = service.get_ohlc(
            segment=segment,
            exchange_trading_symbols=exchange_trading_symbols
        )

        return {
            "status": "success",
            "segment": segment,
            "ohlc": sanitize_for_json(result)
        }

    except TradeException as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/option-chain")
def get_option_chain(
    exchange: str = Query(..., example="NSE"),
    underlying: str = Query(..., example="NIFTY"),
    expiry_date: str = Query(..., example="2025-11-28"),
    service: LiveDataService = Depends(get_live_data_service)
):
    try:
        result = service.get_option_chain(
            exchange=exchange,
            underlying=underlying,
            expiry_date=expiry_date
        )

        return {
            "status": "success",
            "underlying": underlying,
            "expiry_date": expiry_date,
            "option_chain": sanitize_for_json(result)
        }

    except TradeException as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/greeks")
def get_greeks(
    exchange: str = Query(..., example="NSE"),
    underlying: str = Query(..., example="NIFTY"),
    trading_symbol: str = Query(
        ...,
        example="NIFTY26FEB25600CE"
    ),
    expiry: str = Query(..., example="2026-02-26"),
    service: LiveDataService = Depends(get_live_data_service)
):
    try:
        result = service.get_greeks(
            exchange=exchange,
            underlying=underlying,
            trading_symbol=trading_symbol,
            expiry=expiry
        )

        return {
            "status": "success",
            "trading_symbol": trading_symbol,
            "greeks": sanitize_for_json(result)
        }

    except TradeException as e:
        raise HTTPException(status_code=400, detail=str(e))
