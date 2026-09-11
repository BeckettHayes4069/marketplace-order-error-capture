from marketplace_errors import HandoffRequest, handoff_asset


class FakeClient:
    def __init__(self):
        self.calls = []

    def call(self, method, path, payload):
        self.calls.append((method, path, payload))
        return {"event_id": "evt-1"}


def test_failed_delivery_is_actionable_and_grouped_by_seller():
    client = FakeClient()
    request = HandoffRequest("order-7", "seller-2", "asset-9", "buyer@example.com")

    def delivery(_, __):
        raise ValueError("warehouse asset missing")

    result = handoff_asset(request, delivery, client)

    assert result == "seller_action_required"
    method, path, payload = client.calls[0]
    assert (method, path) == ("POST", "/v1/errors/capture")
    assert payload["fingerprint"] == ["order-handoff", "seller-2"]
    assert payload["context"]["order_id"] == "order-7"
