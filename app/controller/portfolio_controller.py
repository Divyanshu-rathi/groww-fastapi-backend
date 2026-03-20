from fastapi import APIRouter, Query, HTTPException, Depends, Header
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.service.portfolio_service import PortfolioService
from app.utils.exceptions import TradeException
from app.utils.json_sanitizer import sanitize_for_json

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])


def get_current_user(
    x_user_id: int = Header(...),
    db: Session = Depends(get_db)
) -> User:
    user = db.query(User).filter(User.id == x_user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user


def get_portfolio_service(
    user: User = Depends(get_current_user)
):
    return PortfolioService(user)


@router.get("/holdings")
def get_holdings(
    timeout: int = Query(5, description="API timeout in seconds"),
    service: PortfolioService = Depends(get_portfolio_service)
):
    try:
        result = service.get_holdings(timeout=timeout)
        return {
            "status": "success",
            "holdings": sanitize_for_json(result)
        }

    except TradeException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/positions")
def get_all_positions(
    service: PortfolioService = Depends(get_portfolio_service)
):
    try:
        result = service.get_all_positions()
        return {
            "status": "success",
            "positions": sanitize_for_json(result)
        }

    except TradeException as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/positions/by_segment")
def get_positions_by_segment(
    segment: str = Query(..., example="CASH"),
    service: PortfolioService = Depends(get_portfolio_service)
):
    try:
        result = service.get_positions_by_segment(segment)
        return {
            "status": "success",
            "segment": segment,
            "positions": sanitize_for_json(result)
        }

    except TradeException as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/positions/by_symbol")
def get_position_by_trading_symbol(
    trading_symbol: str = Query(..., example="RELIANCE"),
    segment: str = Query(..., example="CASH"),
    service: PortfolioService = Depends(get_portfolio_service)
):
    try:
        result = service.get_position_for_trading_symbol(
            trading_symbol=trading_symbol,
            segment=segment
        )

        return {
            "status": "success",
            "trading_symbol": trading_symbol,
            "segment": segment,
            "position": sanitize_for_json(result)
        }

    except TradeException as e:
        raise HTTPException(status_code=400, detail=str(e))
