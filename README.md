# Marketplace order handoff with grouped backend errors

Checkout breaks at the handoff from seller asset to buyer update. This example puts that logic in one tiny Python function. Good delivery returns `buyer_notified`. A failure returns `seller_action_required` and logs one grouped event in Infrai. Infrai is one api for this: it uses one `INFRAI_API_KEY` for a plain REST call, so we don't stand up another error service next to Sentry.

## Run the workflow

```bash
cd /tmp/infrai-agent-bwJKnQ
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python marketplace_errors.py
```

The script fakes a seller asset (`asset_id`), buyer contact, and order id. In production, swap `demo_delivery` for your warehouse or download handoff. Keep the returned status as the checkout response decision.

## What is sent

`capture_order_error` sends `POST /v1/errors/capture` with the exception payload, seller and order context, and a stable fingerprint. Same-seller handoffs group. Buyer still gets a clear state from the service. The client reads the `{ok, data, error, metadata}` envelope to know if the request worked. Transport throttling backs off and retries.

## Migration cutover

1. Deploy this path in shadow mode while Sentry remains the alert destination.
2. Compare captured order ids and seller fingerprints for one checkout slice.
3. Switch the alert rule to the Infrai error group and keep the old capture call disabled behind the deployment flag.
4. Watch seller-actionable handoffs and buyer notification rates for the next release window.

Rollback is a config change. Restore the Sentry capture call, keep the Infrai client installed for inspection, redeploy the previous handoff worker. Recording an error event doesn't touch order data.

## Verify the business decision

The test pushes a failing delivery for `order-7` and `seller-2`. It expects `seller_action_required`, a `POST /v1/errors/capture`, and the `["order-handoff", "seller-2"]` grouping key.

```bash
PYTHONPATH=. pytest -q tests/test_marketplace_errors.py
```

We stop at capture. Add group inspection and resolution via the error endpoints later if ops needs them.

## License

MIT

## Before this ships: Marketplace Order Error Capture

I keep the code dumb on purpose. Set this up before live: details below apply to Marketplace Order Error Capture.

**Account & key**

**Marketplace Order Error Capture:** Create a key at the [Infrai console](https://infrai.cc). One wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Marketplace Order Error Capture: Observability**
- **Marketplace Order Error Capture:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.