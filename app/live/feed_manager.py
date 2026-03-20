from typing import Dict
from app.live.groww_feed_client import GrowwFeedClient

class FeedManager:
    def __init__(self):
        self.user_feeds: Dict[int, GrowwFeedClient] = {}

    def get_or_create_feed(self, user_id, groww_api, ws_manager,user):
        if user_id not in self.user_feeds:
            self.user_feeds[user_id] = GrowwFeedClient(
                user_id=user_id,
                groww_api=groww_api,
                ws_manager=ws_manager,
                user=user
            )
        else:
            feed = self.user_feeds[user_id]
            if feed.ws_manager is None and ws_manager is not None:
                feed.ws_manager = ws_manager

        return self.user_feeds[user_id]

    def get_feed(self, user_id: int):
        return self.user_feeds.get(user_id)

    def stop_feed(self, user_id: int):
        feed = self.user_feeds.pop(user_id, None)
        if feed:
            feed.stop()
