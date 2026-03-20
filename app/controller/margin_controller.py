from fastapi import APIRouter, HTTPException, Query, Body, Depends, Header
from typing import List
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.service.margin_service import MarginService
from app.dto.order_margin_dto import OrderMarginRequestDTO
from app.utils.exceptions import TradeException
from app.utils.json_sanitizer import sanitize_for_json

router = APIRouter(prefix="/margin", tags=["Margin"])


def get_current_user(
    x_user_id: int = Header(...),
    db: Session = Depends(get_db)
) -> User:
    user = db.query(User).filter(User.id == x_user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid user")
    return user


def get_margin_service(
    user: User = Depends(get_current_user)
):
    return MarginService(user)


@router.get("/available")
def get_available_margin(
    service: MarginService = Depends(get_margin_service)
):
    try:
        result = service.get_available_margin()
        return {
            "status": "success",
            "available_margin": sanitize_for_json(result)
        }

    except TradeException as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post("/required")
def get_required_margin(
    segment: str = Query(..., example="CASH"),
    orders: List[OrderMarginRequestDTO] = Body(...),
    service: MarginService = Depends(get_margin_service)
):
    try:
        orders_payload = [
            order.dict(exclude_none=True)
            for order in orders
        ]

        result = service.get_required_margin_for_order(
            segment=segment,
            orders=orders_payload
        )

        return {
            "status": "success",
            "segment": segment,
            "required_margin": sanitize_for_json(result)
        }

    except TradeException as e:
        raise HTTPException(status_code=400, detail=str(e))
