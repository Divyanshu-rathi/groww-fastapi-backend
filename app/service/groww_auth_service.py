from app.models.groww_session import GrowwSession
from app.utils.crypto import decrypt_value
from app.utils.exceptions import TradeException
from growwapi import GrowwAPI
from sqlalchemy.orm import Session
from app.models.user import User


class GrowwAuthService:
    def login(self, db: Session, user: User) -> str:
        try:
            api_key = decrypt_value(user.groww_api_key)
            secret_key = decrypt_value(user.groww_secret_key)         

            access_token = GrowwAPI.get_access_token(api_key, None, secret_key)

            session = (
                db.query(GrowwSession)
                .filter(GrowwSession.user_id == user.id)
                .first()
            )

            if session:
                session.access_token = access_token
            else:
                session = GrowwSession(
                    user_id=user.id,
                    access_token=access_token
                )
                db.add(session)

            db.commit()

            return access_token

        except Exception as e:
            raise TradeException(f"Groww login failed: {str(e)}")


    def logout(self, db: Session, user: User):
        sessions = (
            db.query(GrowwSession)
            .filter(GrowwSession.user_id == user.id)
            .all()
        )

        if not sessions:
            raise TradeException("User not logged into Groww")

        for s in sessions:
            db.delete(s)

        db.commit()


        return True
