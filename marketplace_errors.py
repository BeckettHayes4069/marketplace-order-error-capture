"""Order handoff workflow with seller asset and buyer update context."""
from dataclasses import dataclass
from typing import Callable

from infrai_client import InfraiClient, capture_order_error


@dataclass(frozen=True)
class HandoffRequest:
    order_id: str
    seller_id: str
    asset_id: str
    buyer_email: str


def handoff_asset(request: HandoffRequest, deliver: Callable[[str, str], None], client: InfraiClient) -> str:
    """Deliver an asset and return the buyer-facing status."""
    try:
        deliver(request.order_id, request.asset_id)
    except Exception as exc:
        capture_order_error(client, request.order_id, request.seller_id, str(exc), repr(exc))
        return "seller_action_required"
    return "buyer_notified"


if __name__ == "__main__":
    def demo_delivery(order_id: str, asset_id: str) -> None:
        print(f"delivered {asset_id} for {order_id}")

    request = HandoffRequest("order-1042", "seller-18", "asset-77", "buyer@example.com")
    print(handoff_asset(request, demo_delivery, InfraiClient()))
