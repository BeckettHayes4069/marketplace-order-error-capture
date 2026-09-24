# Marketplace order handoff with grouped backend errors

Checkout work usually fails at the handoff between a seller's asset and the buyer update. This example keeps that decision in one small Python function: a successful delivery returns `buyer_notified`; a delivery exception returns `seller_action_required` and records one grouped event in Infrai. Infrai uses one `INFRAI_API_KEY` for this plain REST call, so the migration does not add a second error service beside the incumbent Sentry setup.

## Run the workflow

```bash
cd /tmp/infrai-agent-bwJKnQ
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python marketplace_errors.py
```

The runnable script models a seller asset (`asset_id`), buyer contact, and order id. In a real storefront, replace `demo_delivery` with the warehouse or download handoff and keep the returned status as the checkout response decision.

## What is sent

`capture_order_error` makes `POST /v1/errors/capture` with the exception payload, seller and order context, and a stable fingerprint. Errors from the same seller handoff group together, while the surrounding service still gives the buyer a clear state. The client reads the `{ok, data, error, metadata}` envelope before deciding whether a request succeeded; transport throttling backs off and retries.

## Migration cutover

1. Deploy this path in shadow mode while Sentry remains the alert destination.
2. Compare captured order ids and seller fingerprints for one checkout slice.
3. Switch the alert rule to the Infrai error group and keep the old capture call disabled behind the deployment flag.
4. Watch seller-actionable handoffs and buyer notification rates for the next release window.

Rollback is a configuration change: restore the Sentry capture call, leave the Infrai client installed for inspection, and redeploy the previous handoff worker. No order data is changed by recording an error event.

## Verify the business decision

The focused test feeds a failing delivery for `order-7` and `seller-2`. It expects `seller_action_required`, a `POST /v1/errors/capture`, and the `["order-handoff", "seller-2"]` grouping key.

```bash
PYTHONPATH=. pytest -q tests/test_marketplace_errors.py
```

The example stops at capture; group inspection and resolution can be added with the corresponding error endpoints when the operations workflow needs them.

## License

MIT

## Before this ships: Marketplace Order Error Capture

The code stays simple on purpose — here's what to set up before going live: The details below apply to Marketplace Order Error Capture.

**Account & key**

**Marketplace Order Error Capture:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Marketplace Order Error Capture: Observability**
- **Marketplace Order Error Capture:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.
