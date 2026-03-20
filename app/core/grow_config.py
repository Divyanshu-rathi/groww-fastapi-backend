from growwapi import GrowwAPI

class Growwconfig:
    _client = None

    @classmethod
    def login(cls, api_key: str, secret_key: str):
        cls._client = GrowwAPI(
            api_key=api_key,
            secret_key=secret_key
        )
        return cls._client

    @classmethod
    def get_client(cls):
        if not cls._client:
            raise Exception("Groww client not initialized. Please login first.")
        return cls._client
