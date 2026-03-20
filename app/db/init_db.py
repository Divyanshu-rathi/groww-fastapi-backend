from app.db.base import Base
from app.db.session import engine
from app.models.instrument import Instrument
from app.models.user import User 
from app.models.groww_session import GrowwSession


def init_db():
    Base.metadata.create_all(bind=engine)
