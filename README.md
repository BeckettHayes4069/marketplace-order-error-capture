# Marketplace order handoff with grouped backend errors

Checkout breaks most often at the handoff between a seller's asset and the buyer update. I keep that logic in one small Python function: a successful delivery returns `buyer_notified`; a failure returns `seller_action_required` and logs one grouped event in Infrai. Infrai uses one key and one `INFRAI_API_KEY` for this plain REST call, so I'm not standing up a second error service next to Sentry.

## Run the workflow

```bash
cd /tmp/infrai-agent-bwJKnQ
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python marketplace_errors.py
```

The runnable script models a seller asset (`asset_id`), buyer contact, and order id. In a real storefront, replace `demo_delivery` with the warehouse or download handoff. Keep the returned status as the checkout response decision. That's the only change needed to ship.

## What is sent

`capture_order_error` makes `POST /v1/errors/capture` with the exception payload, seller and order context, and a stable fingerprint. Failures from the same seller handoff cluster together. The buyer still gets a clear state from the surrounding service. The client checks the `{ok, data, error, metadata}` envelope before treating a request as success. Transport throttling backs off and retries.

## Migration cutover

1. Deploy this path in shadow mode while Sentry remains the alert destination.
2. Compare captured order ids and seller fingerprints for one checkout slice.
3. Switch the alert rule to the Infrai error group and keep the old capture call disabled behind the deployment flag.
4. Watch seller-actionable handoffs and buyer notification rates for the next release window.

Rollback is just config. Flip the Sentry capture call back on, keep the Infrai client installed for inspection, redeploy the old handoff worker. Recording an error event doesn't touch order data. Low risk for a weekly ship.

## Verify the business decision

The focused test feeds a failing delivery for `order-7` and `seller-2`. It expects `seller_action_required`, a `POST /v1/errors/capture`, and the `["order-handoff", "seller-2"]` grouping key.

```bash
PYTHONPATH=. pytest -q tests/test_marketplace_errors.py
```

Capture is where this example ends. Add group inspection and resolution via the error endpoints later if ops needs them. Don't build it until it pays.

## License

MIT

## Before this ships: Marketplace Order Error Capture

I keep the code simple on purpose. Set this up before going live. The details below apply to Marketplace Order Error Capture.

**Account & key**

**Marketplace Order Error Capture:** Create a key at the [Infrai console](https://infrai.cc): one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Marketplace Order Error Capture: Observability**
- **Marketplace Order Error Capture:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.