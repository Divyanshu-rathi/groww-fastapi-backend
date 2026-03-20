from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.groww_session import GrowwSession
from app.client.grow_client import GrowwClient
from app.live.feed_manager import FeedManager
from app.dto.livedata_dto import SubscribeLTPRequest

router = APIRouter(prefix="/live", tags=["Ltp subscribe"])
feed_manager = FeedManager()


def get_current_user(
    x_user_id: int = Header(...),
    db: Session = Depends(get_db)
    
):
    return db.query(User).filter(User.id == x_user_id).first()



@router.post("/ltp/subscribe")
def subscribe_ltp(
    payload: SubscribeLTPRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    instruments = payload.instruments

    session = db.query(GrowwSession).filter(
        GrowwSession.user_id == user.id
    ).first()

    if not session:
        return {"status": "error", "message": "User not logged in to Groww"}

    groww_client = GrowwClient(session.access_token)

    feed = feed_manager.get_or_create_feed(
        user_id=user.id,
        groww_api=groww_client.client,
        ws_manager=request.app.state.ws_manager,
        user=user
    )

    feed.subscribe_ltp(instruments)

    return {"status": "success", "message": "Subscribed"}



@router.post("/ltp/unsubscribe")
def unsubscribe_ltp(
    payload: SubscribeLTPRequest,
    user: User = Depends(get_current_user),
):
    instruments = payload.instruments

   
    feed = feed_manager.user_feeds.get(user.id)
    if not feed:
        return {"status": "success", "message": "No active feed"}

   
    if not feed.has_ltp(instruments):
        return {
            "status": "success",
            "message": "LTP not subscribed"
        }

    
    feed.unsubscribe_ltp(instruments)

    return {
        "status": "success",
        "message": "Unsubscribed"
    }
