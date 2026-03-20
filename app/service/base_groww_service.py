from app.db.session import SessionLocal
from app.models.groww_session import GrowwSession
from app.client.grow_client import GrowwClient
from app.utils.exceptions import TradeException


class BaseGrowwService:
    def __init__(self, user):
        db = SessionLocal()

        session = (
            db.query(GrowwSession)
            .filter(GrowwSession.user_id == user.id)
            .first()
        )

        if not session:
            raise TradeException("User not logged into Groww")

        self.user = user
        self.groww_client = GrowwClient(session.access_token)
