from app.utils.exceptions import TradeException
from app.service.base_groww_service import BaseGrowwService


class PortfolioService(BaseGrowwService):

    def __init__(self, user):
        super().__init__(user)
        self.client = self.groww_client.client   

    def get_holdings(self, timeout: int = 5):
        try:
            return self.client.get_holdings_for_user(timeout=timeout)
        except Exception as e:
            raise TradeException(str(e))

    def get_all_positions(self):
        try:
            return self.client.get_positions_for_user()
        except Exception as e:
            raise TradeException(str(e))

    def get_positions_by_segment(self, segment: str):
        try:
            return self.client.get_positions_for_user(segment=segment)
        except Exception as e:
            raise TradeException(str(e))

    def get_position_for_trading_symbol(
        self,
        trading_symbol: str,
        segment: str
    ):
        try:
            return self.client.get_position_for_trading_symbol(
                trading_symbol=trading_symbol,
                segment=segment
            )
        except Exception as e:
            raise TradeException(str(e))
