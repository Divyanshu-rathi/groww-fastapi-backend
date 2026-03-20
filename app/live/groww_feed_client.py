import threading
from growwapi import GrowwFeed


class GrowwFeedClient:

    def __init__(self, user_id, groww_api, ws_manager, user):
        self.user_id = user_id
        self.user = user
        self.feed = GrowwFeed(groww_api)
        self.ws_manager = ws_manager

        self.running = False
        self.thread = None

        self.subscribed_ltp_tokens = set()
        self.subscribed_depth_tokens = set()
        self.subscribed_index_tokens = set()

        self.orders_subscribed = False
        self.positions_subscribed = False

    def on_data_received(self, meta):
        print("Groww callback meta:", meta)

        try:
            feed_type = meta.get("feed_type")

            if feed_type == "ltp":
                data = self.feed.get_ltp()
                event = "ltp"

            elif feed_type == "index_value":
                data = self.feed.get_index_value()
                event = "index"

            elif feed_type == "market_depth":
                data = self.feed.get_market_depth()
                event = "depth"

            
            elif feed_type == "order_updates":

                from app.service.margin_service import MarginService

                if meta.get("segment") == "CASH":
                    order_data = self.feed.get_equity_order_update()
                else:
                    order_data = self.feed.get_fno_order_update()

                available_margin = None

                try:
                    margin_service = MarginService(self.user)
                    available_margin = margin_service.get_available_margin()
                except Exception as margin_error:
                    print(f"[Margin Error][User {self.user_id}]: {margin_error}")

                
                if self.ws_manager:
                    self.ws_manager.send_to_user(
                        self.user_id,
                        {
                            "type": "portfolio_update",
                            "order": order_data,
                            "available_margin": available_margin
                        }
                    )
                return  

            elif feed_type == "position_updates":
                data = self.feed.get_fno_position_update()
                event = "positions"

            else:
                return

            
            if self.ws_manager:
                self.ws_manager.send_to_user(
                    self.user_id,
                    {
                        "type": event,
                        "data": data
                    }
                )

        except Exception as e:
            print(f"[GrowwFeedClient ERROR][User {self.user_id}]: {e}")

 
    def _start_if_required(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(
                target=self.feed.consume,
                daemon=True
            )
            self.thread.start()


    def has_ltp(self, instruments):
        return any(i.exchange_token in self.subscribed_ltp_tokens for i in instruments)

    def has_market_depth(self, instruments):
        return any(i.exchange_token in self.subscribed_depth_tokens for i in instruments)

    def has_index(self, instruments):
        return any(i.exchange_token in self.subscribed_index_tokens for i in instruments)

 
    def subscribe_ltp(self, instruments):
        data = []
        for i in instruments:
            self.subscribed_ltp_tokens.add(i.exchange_token)
            data.append(i.dict())
        self.feed.subscribe_ltp(data, on_data_received=self.on_data_received)
        self._start_if_required()

    def unsubscribe_ltp(self, instruments):
        data = []
        for i in instruments:
            self.subscribed_ltp_tokens.discard(i.exchange_token)
            data.append(i.dict())
        self.feed.unsubscribe_ltp(data)


    def subscribe_indices(self, instruments):
        data = []
        for i in instruments:
            self.subscribed_index_tokens.add(i.exchange_token)
            data.append(i.dict())
        self.feed.subscribe_index_value(data, on_data_received=self.on_data_received)
        self._start_if_required()

    def unsubscribe_indices(self, instruments):
        data = []
        for i in instruments:
            self.subscribed_index_tokens.discard(i.exchange_token)
            data.append(i.dict())
        self.feed.unsubscribe_index_value(data)


    def subscribe_market_depth(self, instruments):
        data = []
        for i in instruments:
            self.subscribed_depth_tokens.add(i.exchange_token)
            data.append(i.dict())
        self.feed.subscribe_market_depth(data, on_data_received=self.on_data_received)
        self._start_if_required()

    def unsubscribe_market_depth(self, instruments):
        data = []
        for i in instruments:
            self.subscribed_depth_tokens.discard(i.exchange_token)
            data.append(i.dict())
        self.feed.unsubscribe_market_depth(data)

 
    def subscribe_order_updates(self):
        if self.orders_subscribed:
            return

        self.feed.subscribe_equity_order_updates(
            on_data_received=self.on_data_received
        )
        self.feed.subscribe_fno_order_updates(
            on_data_received=self.on_data_received
        )

        self.orders_subscribed = True
        self._start_if_required()

    def unsubscribe_order_updates(self):
        if not self.orders_subscribed:
            return
        try:
            self.feed.unsubscribe_equity_order_updates()
        except Exception:
            pass
        try:
            self.feed.unsubscribe_fno_order_updates()
        except Exception:
            pass
        self.orders_subscribed = False

    def subscribe_position_updates(self):
        if self.positions_subscribed:
            return

        self.feed.subscribe_fno_position_updates(
            on_data_received=self.on_data_received
        )

        self.positions_subscribed = True
        self._start_if_required()

    def unsubscribe_position_updates(self):
        if not self.positions_subscribed:
            return
        try:
            self.feed.unsubscribe_fno_position_updates()
        except Exception:
            pass
        self.positions_subscribed = False

 
    def stop(self):
        self.running = False
        try:
            self.feed.close()
        except Exception:
            pass
