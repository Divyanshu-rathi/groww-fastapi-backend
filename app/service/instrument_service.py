import json
import math
from sqlalchemy.orm import Session

from app.utils.exceptions import TradeException
from app.models.instrument import Instrument
from app.service.base_groww_service import BaseGrowwService


def is_nan(value) -> bool:
    return value is not None and isinstance(value, float) and math.isnan(value)


def clean_value(value):
    if is_nan(value):
        return None
    return value


def to_bool(value, default=False) -> bool:
    if value is None or is_nan(value):
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(int(value))
    if isinstance(value, str):
        return value.strip().lower() in ["1", "true", "yes", "y"]
    return default


def clean_dict(data: dict) -> dict:
    cleaned = {}
    for k, v in data.items():
        if isinstance(v, dict):
            cleaned[k] = clean_dict(v)
        elif isinstance(v, list):
            cleaned[k] = [clean_value(i) for i in v]
        else:
            cleaned[k] = clean_value(v)
    return cleaned


class InstrumentService(BaseGrowwService):

    def __init__(self, user):
        super().__init__(user)
        self.client = self.groww_client.client

  

    def sync_instruments(self, db: Session):
        instruments = self.client.get_all_instruments()

        if instruments is None or (
            hasattr(instruments, "empty") and instruments.empty
        ):
            return {"message": "No instruments received"}

        if hasattr(instruments, "iterrows"):
            iterable = (row.to_dict() for _, row in instruments.iterrows())
        else:
            iterable = instruments

        saved = 0

        for item in iterable:
            item = clean_dict(item)

            exchange_token = str(item.get("exchange_token"))
            trading_symbol = item.get("trading_symbol")

            internal_symbol = (
                item.get("internal_trading_symbol")
                or trading_symbol
            )

            raw_json = json.dumps(item, default=str)

            db_instrument = (
                db.query(Instrument)
                .filter(Instrument.exchange_token == exchange_token)
                .first()
            )

            if db_instrument:
                db_instrument.exchange = item.get("exchange")
                db_instrument.trading_symbol = trading_symbol
                db_instrument.groww_symbol = item.get("groww_symbol")
                db_instrument.internal_trading_symbol = internal_symbol
                db_instrument.is_reserved = to_bool(item.get("is_reserved"))
                db_instrument.buy_allowed = to_bool(item.get("buy_allowed"), True)
                db_instrument.sell_allowed = to_bool(item.get("sell_allowed"), True)
                db_instrument.raw_data = raw_json
            else:
                db.add(
                    Instrument(
                        exchange=item.get("exchange"),
                        exchange_token=exchange_token,
                        trading_symbol=trading_symbol,
                        groww_symbol=item.get("groww_symbol"),
                        internal_trading_symbol=internal_symbol,
                        is_reserved=to_bool(item.get("is_reserved")),
                        buy_allowed=to_bool(item.get("buy_allowed"), True),
                        sell_allowed=to_bool(item.get("sell_allowed"), True),
                        raw_data=raw_json,
                    )
                )
                saved += 1

        db.commit()

        return {
            "message": "All instruments saved successfully",
            "inserted": saved
        }

    def get_instruments(self, db: Session, limit: int = 50, offset: int = 0):
        return db.query(Instrument).offset(offset).limit(limit).all()

    def count(self, db: Session):
        return db.query(Instrument).count()

   

    def get_ltp(self, segment: str, exchange_trading_symbols: str):
        try:
            return self.client.get_ltp(
                segment=segment,
                exchange_trading_symbols=exchange_trading_symbols
            )
        except Exception as e:
            raise TradeException(str(e))

    def get_instrument_by_groww_symbol(self, groww_symbol: str):
        try:
            return self.client.get_instrument_by_groww_symbol(groww_symbol)
        except Exception as e:
            raise TradeException(str(e))

    def get_instrument_by_exchange_and_trading_symbol(
        self,
        exchange: str,
        trading_symbol: str
    ):
        try:
            return self.client.get_instrument_by_exchange_and_trading_symbol(
                exchange,
                trading_symbol
            )
        except Exception as e:
            raise TradeException(str(e))

    def get_instrument_by_exchange_token(self, exchange_token: str):
        try:
            return self.client.get_instrument_by_exchange_token(exchange_token)
        except Exception as e:
            raise TradeException(str(e))
