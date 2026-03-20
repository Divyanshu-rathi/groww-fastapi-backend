from fastapi import APIRouter, HTTPException, Query, Depends, Header
from sqlalchemy.orm import Session

from app.service.historical_service import HistoricalService
from app.models.user import User
from app.db.session import get_db
from app.utils.exceptions import TradeException
from app.utils.json_sanitizer import sanitize_for_json

router = APIRouter(prefix="/historical", tags=["Historical Data"])


def get_current_user(
    x_user_id: int = Header(...),
    db: Session = Depends(get_db)
) -> User:
    user = db.query(User).filter(User.id == x_user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user


def get_historical_service(
    user: User = Depends(get_current_user)
):
    return HistoricalService(user)


@router.get("/candles")
def get_historical_candles(
    trading_symbol: str = Query(..., example="TCS"),
    exchange: str = Query(..., example="NSE"),
    segment: str = Query(..., example="CASH"),
    start_time: str = Query(..., example="2026-01-11 09:30:00"),
    end_time: str = Query(..., example="2026-01-11 15:15:00"),
    interval_in_minutes: int | None = Query(5, example=5),
    service: HistoricalService = Depends(get_historical_service)
):
    try:
        result = service.get_historical_candles(
            trading_symbol=trading_symbol,
            exchange=exchange,
            segment=segment,
            start_time=start_time,
            end_time=end_time,
            interval_in_minutes=interval_in_minutes
        )

        return {
            "status": "success",
            "trading_symbol": trading_symbol,
            "data": sanitize_for_json(result)
        }

    except TradeException as e:
        raise HTTPException(status_code=400, detail=str(e))
