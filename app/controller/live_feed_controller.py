from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.groww_session import GrowwSession
from app.client.grow_client import GrowwClient
from app.live.feed_manager import FeedManager
from app.dto.livedata_dto import SubscribeLTPRequest

router = APIRouter(prefix="/live/feed", tags=["Live Feed"])
feed_manager = FeedManager()


def get_current_user(
    x_user_id: int = Header(...),
    db: Session = Depends(get_db)
):
    return db.query(User).filter(User.id == x_user_id).first()


def get_user_feed(request: Request, db: Session, user: User):
    session = db.query(GrowwSession).filter(
        GrowwSession.user_id == user.id
    ).first()

    groww_client = GrowwClient(session.access_token)

    return feed_manager.get_or_create_feed(
        user_id=user.id,
        groww_api=groww_client.client,
        ws_manager=request.app.state.ws_manager,
        user=user
    )



@router.post("/index/subscribe")
def subscribe_index(
    payload: SubscribeLTPRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    feed = get_user_feed(request, db, user)
    feed.subscribe_indices(payload.instruments)
    return {"status": "success", "message": "Index subscribed"}


@router.post("/index/unsubscribe")
def unsubscribe_index(
    payload: SubscribeLTPRequest,
    user: User = Depends(get_current_user),
):
    feed = feed_manager.user_feeds.get(user.id)

    if not feed:
        return {"status": "success", "message": "No active feed"}

    if not feed.has_index(payload.instruments):
        return {"status": "success", "message": "Index not subscribed"}

    feed.unsubscribe_indices(payload.instruments)
    return {"status": "success", "message": "Index unsubscribed"}



@router.post("/depth/subscribe")
def subscribe_depth(
    payload: SubscribeLTPRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    feed = get_user_feed(request, db, user)
    feed.subscribe_market_depth(payload.instruments)
    return {"status": "success", "message": "Market depth subscribed"}


@router.post("/depth/unsubscribe")
def unsubscribe_depth(
    payload: SubscribeLTPRequest,
    user: User = Depends(get_current_user),
):
    feed = feed_manager.user_feeds.get(user.id)

    if not feed:
        return {"status": "success", "message": "No active feed"}

    if not feed.has_market_depth(payload.instruments):
        return {"status": "success", "message": "Market depth not subscribed"}

    feed.unsubscribe_market_depth(payload.instruments)
    return {"status": "success", "message": "Market depth unsubscribed"}



@router.post("/orders/subscribe")
def subscribe_orders(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    feed = get_user_feed(request, db, user)
    feed.subscribe_order_updates()
    return {"status": "success", "message": "Order updates subscribed"}


@router.post("/orders/unsubscribe")
def unsubscribe_orders(
    user: User = Depends(get_current_user),
):
    feed = feed_manager.user_feeds.get(user.id)

    if not feed:
        return {"status": "success", "message": "No active feed"}

    feed.unsubscribe_order_updates()
    return {"status": "success", "message": "Order updates unsubscribed"}



@router.post("/positions/subscribe")
def subscribe_positions(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    feed = get_user_feed(request, db, user)
    feed.subscribe_position_updates()
    return {"status": "success", "message": "Position updates subscribed"}


@router.post("/positions/unsubscribe")
def unsubscribe_positions(
    user: User = Depends(get_current_user),
):
    feed = feed_manager.user_feeds.get(user.id)

    if not feed:
        return {"status": "success", "message": "No active feed"}

    feed.unsubscribe_position_updates()
    return {"status": "success", "message": "Position updates unsubscribed"}
