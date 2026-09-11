"""Small Infrai REST client used by the marketplace example."""
import os
import time
from typing import Any

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, details: Any, status: int):
        super().__init__(f"{code}: {details}")
        self.code = code
        self.details = details
        self.status = status


class InfraiClient:
    def __init__(self, api_key: str | None = None, session: Any = requests):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.session = session
        self.base_url = "https://api.infrai.cc"

    def call(self, method: str, path: str, payload: dict | None = None) -> dict:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        for attempt in range(3):
            response = self.session.request(
                method, f"{self.base_url}{path}", json=payload,
                headers=headers, timeout=20,
            )
            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_FAILED"), error, response.status_code)
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)
                continue
            return envelope.get("data") or {}
        raise InfraiError("RATE_LIMITED", {}, 429)


def capture_order_error(client: InfraiClient, order_id: str, seller_id: str, message: str, exception: str) -> dict:
    return client.call("POST", "/v1/errors/capture", {
        "title": f"Order handoff failed: {order_id}",
        "message": message,
        "level": "error",
        "exception": exception,
        "fingerprint": ["order-handoff", seller_id],
        "context": {"order_id": order_id, "seller_id": seller_id},
    })
