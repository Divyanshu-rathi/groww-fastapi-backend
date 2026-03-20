from fastapi import APIRouter, Depends, Query, HTTPException, Header
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.service.instrument_service import InstrumentService
from app.utils.json_sanitizer import sanitize_for_json
from app.utils.exceptions import TradeException

router = APIRouter(prefix="/instruments", tags=["Instruments"])


def get_current_user(
    x_user_id: int = Header(...),
    db: Session = Depends(get_db)
) -> User:
    user = db.query(User).filter(User.id == x_user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user


def get_instrument_service(
    user: User = Depends(get_current_user)
):
    return InstrumentService(user)


@router.post("/sync")
def sync_instruments(
    db: Session = Depends(get_db),
    service: InstrumentService = Depends(get_instrument_service)
):
    return service.sync_instruments(db)


@router.get("/")
def get_instruments(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    service: InstrumentService = Depends(get_instrument_service)
):
    instruments = service.get_instruments(db, limit, offset)
    return {
        "count": service.count(db),
        "data": [
            {
                "id": i.id,
                "exchange": i.exchange,
                "exchange_token": i.exchange_token,
                "trading_symbol": i.trading_symbol,
                "groww_symbol": i.groww_symbol,
                "internal_trading_symbol": i.internal_trading_symbol,
                "is_reserved": i.is_reserved,
                "buy_allowed": i.buy_allowed,
                "sell_allowed": i.sell_allowed,
            }
            for i in instruments
        ]
    }


@router.get("/ltp")
def get_ltp(
    segment: str = Query(..., example="CASH"),
    exchange_trading_symbols: str = Query(..., example="NSE_RELIANCE"),
    service: InstrumentService = Depends(get_instrument_service)
):
    try:
        result = service.get_ltp(segment, exchange_trading_symbols)
        return {
            "status": "success",
            "ltp": sanitize_for_json(result)
        }
    except TradeException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/by_symbol")
def get_instrument_by_groww_symbol(
    groww_symbol: str = Query(..., example="NSE-RELIANCE"),
    service: InstrumentService = Depends(get_instrument_service)
):
    try:
        result = service.get_instrument_by_groww_symbol(groww_symbol)
        return {
            "status": "success",
            "instrument": sanitize_for_json(result)
        }
    except TradeException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/by_exchange_and_trading_symbol")
def get_instrument_by_exchange_and_trading_symbol(
    exchange: str = Query(..., example="NSE"),
    trading_symbol: str = Query(..., example="RELIANCE"),
    service: InstrumentService = Depends(get_instrument_service)
):
    try:
        result = service.get_instrument_by_exchange_and_trading_symbol(
            exchange,
            trading_symbol
        )
        return {
            "status": "success",
            "instrument": sanitize_for_json(result)
        }
    except TradeException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/by_exchange_token")
def get_instrument_by_exchange_token(
    exchange_token: str = Query(..., example="2885"),
    service: InstrumentService = Depends(get_instrument_service)
):
    try:
        result = service.get_instrument_by_exchange_token(exchange_token)
        return {
            "status": "success",
            "instrument": sanitize_for_json(result)
        }
    except TradeException as e:
        raise HTTPException(status_code=400, detail=str(e))
