from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.groww_session import GrowwSession
from app.service.groww_auth_service import GrowwAuthService
from app.utils.exceptions import TradeException
from app.live.feed_manager import FeedManager

router = APIRouter(prefix="/groww", tags=["Groww Auth"])
service = GrowwAuthService()

feed_manager = FeedManager()

@router.post("/login")
def groww_login(
    x_user_id: int = Header(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == x_user_id).first()
    token = service.login(db, user)
    return {"status": "success", "access_token": token}

@router.post("/logout")
def groww_logout(
    request: Request,
    x_user_id: int = Header(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == x_user_id).first()

    try:
        service.logout(db, user)
        feed_manager.stop_feed(user.id)
        request.app.state.ws_manager.disconnect_user(user.id)
        return {
            "status": "success",
            "message": "Groww logout successful"
        }

    except TradeException as e:
        return {
            "status": "failed",
            "message": str(e)
        }
