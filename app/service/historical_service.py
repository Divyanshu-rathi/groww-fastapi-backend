from app.utils.exceptions import TradeException
from app.service.base_groww_service import BaseGrowwService


class HistoricalService(BaseGrowwService):

    def __init__(self, user):
        super().__init__(user)
        self.client = self.groww_client.client

    def get_historical_candles(
        self,
        trading_symbol: str,
        exchange: str,
        segment: str,
        start_time: str,
        end_time: str,
        interval_in_minutes: int | None = None
    ):
        try:
            EXCHANGE_MAP = {
                "NSE": self.client.EXCHANGE_NSE,
                "BSE": self.client.EXCHANGE_BSE,
                "MCX": self.client.EXCHANGE_MCX
            }

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

            exchange_const = EXCHANGE_MAP.get(exchange.upper())
            segment_const = SEGMENT_MAP.get(segment.upper())

            if not exchange_const or not segment_const:
                raise TradeException("Invalid exchange or segment")

            return self.client.get_historical_candle_data(
                trading_symbol=trading_symbol,
                exchange=exchange_const,
                segment=segment_const,
                start_time=start_time,
                end_time=end_time,
                interval_in_minutes=interval_in_minutes
            )

        except Exception as e:
            raise TradeException(str(e))
