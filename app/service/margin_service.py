from app.utils.exceptions import TradeException
from app.service.base_groww_service import BaseGrowwService


class MarginService(BaseGrowwService):

    def __init__(self, user):
        super().__init__(user)
        self.client = self.groww_client.client

    def get_available_margin(self):
        try:
            return self.client.get_available_margin_details()
        except Exception as e:
            raise TradeException(str(e))
        
    def get_required_margin_for_order(self, segment: str, orders: list):
        try:
            return self.client.get_order_margin_details(
                segment=segment,
                orders=orders
            )
        except Exception as e:
            raise TradeException(str(e))
