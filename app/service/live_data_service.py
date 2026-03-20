from typing import List, Union

from app.service.base_groww_service import BaseGrowwService
from app.utils.exceptions import TradeException


class LiveDataService(BaseGrowwService):

    def __init__(self, user):
        super().__init__(user)
        self.client = self.groww_client.client

    def get_quote(
        self,
        trading_symbol: str,
        exchange: str,
        segment: str
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
                "COMMODITY": self.client.SEGMENT_COMMODITY,
                "CURRENCY": self.client.SEGMENT_CURRENCY,
                "CDS": self.client.SEGMENT_CURRENCY
            }

            exchange_const = EXCHANGE_MAP.get(exchange.upper())
            segment_const = SEGMENT_MAP.get(segment.upper())

            if not exchange_const or not segment_const:
                raise TradeException("Invalid exchange or segment")

            return self.client.get_quote(
                exchange=exchange_const,
                segment=segment_const,
                trading_symbol=trading_symbol
            )

        except Exception as e:
            raise TradeException(str(e))

   
    def get_ohlc(
        self,
        segment: str,
        exchange_trading_symbols: Union[str, List[str]]
    ):
        try:
            SEGMENT_MAP = {
                "CASH": self.client.SEGMENT_CASH,
                "FNO": self.client.SEGMENT_FNO,
                "NFO": self.client.SEGMENT_FNO,
                "COMMODITY": self.client.SEGMENT_COMMODITY,
                "CURRENCY": self.client.SEGMENT_CURRENCY,
                "CDS": self.client.SEGMENT_CURRENCY
            }

            segment_const = SEGMENT_MAP.get(segment.upper())
            if not segment_const:
                raise TradeException("Invalid segment")

           
            if isinstance(exchange_trading_symbols, list):
                if len(exchange_trading_symbols) > 50:
                    raise TradeException("Maximum 50 instruments allowed")
                exchange_trading_symbols = tuple(exchange_trading_symbols)

            return self.client.get_ohlc(
                segment=segment_const,
                exchange_trading_symbols=exchange_trading_symbols
            )

        except Exception as e:
            raise TradeException(str(e))
        
    
    def get_option_chain(
        self,
        exchange: str,
        underlying: str,
        expiry_date: str
    ):
        try:
            EXCHANGE_MAP = {
                "NSE": self.client.EXCHANGE_NSE,
                "BSE": self.client.EXCHANGE_BSE,
                "MCX": self.client.EXCHANGE_MCX
            }

            exchange_const = EXCHANGE_MAP.get(exchange.upper())
            if not exchange_const:
                raise TradeException("Invalid exchange")

            return self.client.get_option_chain(
                exchange=exchange_const,
                underlying=underlying,
                expiry_date=expiry_date
            )

        except Exception as e:
            raise TradeException(str(e))
        

    def get_greeks(
        self,
        exchange: str,
        underlying: str,
        trading_symbol: str,
        expiry: str
    ):
        try:
            EXCHANGE_MAP = {
                "NSE": self.client.EXCHANGE_NSE,
                "BSE": self.client.EXCHANGE_BSE,
                "MCX": self.client.EXCHANGE_MCX
            }

            exchange_const = EXCHANGE_MAP.get(exchange.upper())
            if not exchange_const:
                raise TradeException("Invalid exchange")

            return self.client.get_greeks(
                exchange=exchange_const,
                underlying=underlying,
                trading_symbol=trading_symbol,
                expiry=expiry
            )

        except Exception as e:
            raise TradeException(str(e))
