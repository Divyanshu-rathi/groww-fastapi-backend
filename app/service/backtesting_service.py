from app.utils.exceptions import TradeException
from app.service.base_groww_service import BaseGrowwService


class BacktestingService(BaseGrowwService):

    def __init__(self, user):
        super().__init__(user)

        self.client = self.groww_client.client

    def get_exchange_constant(self, exchange: str):

        EXCHANGE_MAP = {
            "NSE": self.client.EXCHANGE_NSE,
            "BSE": self.client.EXCHANGE_BSE,
            "MCX": self.client.EXCHANGE_MCX
        }

        exchange_const = EXCHANGE_MAP.get(exchange.upper())
        if not exchange_const:
            raise TradeException("Invalid exchange")

        return exchange_const

    def get_segment_constant(self, segment: str):

        SEGMENT_MAP = {
            "CASH": self.client.SEGMENT_CASH,
            "FNO": self.client.SEGMENT_FNO,
            "NFO": self.client.SEGMENT_FNO,
            "FUTURES": self.client.SEGMENT_FNO,
            "OPTIONS": self.client.SEGMENT_FNO,
            "COMMODITY": self.client.SEGMENT_COMMODITY,
            "MCX": self.client.SEGMENT_COMMODITY,
            "CURRENCY": self.client.SEGMENT_CURRENCY,
            "CDS": self.client.SEGMENT_CURRENCY
        }

        segment_const = SEGMENT_MAP.get(segment.upper())
        if not segment_const:
            raise TradeException("Invalid segment")

        return segment_const

    def get_expiries(
        self,
        exchange: str,
        underlying_symbol: str,
        year: int,
        month: int
    ):
        try:
            return self.client.get_expiries(
                exchange=self.get_exchange_constant(exchange),
                underlying_symbol=underlying_symbol,
                year=year,
                month=month
            )
        except Exception as e:
            raise TradeException(str(e))

    def get_contracts(
        self,
        exchange: str,
        underlying_symbol: str,
        expiry_date: str
    ):
        try:
            return self.client.get_contracts(
                exchange=self.get_exchange_constant(exchange),
                underlying_symbol=underlying_symbol,
                expiry_date=expiry_date
            )
        except Exception as e:
            raise TradeException(str(e))

    def get_historical_candles(
        self,
        exchange: str,
        segment: str,
        groww_symbol: str,
        start_time: str,
        end_time: str,
        candle_interval
    ):
        try:
            return self.client.get_historical_candles(
                exchange=self.get_exchange_constant(exchange),
                segment=self.get_segment_constant(segment),
                groww_symbol=groww_symbol,
                start_time=start_time,
                end_time=end_time,
                candle_interval=candle_interval
            )
        except Exception as e:
            raise TradeException(str(e))
