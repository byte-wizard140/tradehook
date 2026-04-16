# Contributing to tradehook

Thanks for being here. This is a small community project — any working PR is welcome.

## What's needed most

- [ ] `brokers/zerodha_kite.py` — full implementation (kiteconnect v4)
- [ ] `brokers/angel_one.py` — SmartAPI
- [ ] `brokers/upstox.py` — Upstox v2 API
- [ ] Daily token refresh handling for Zerodha (access_token expires at midnight)
- [ ] A simple CLI `--test-connection` flag per broker
- [ ] `tests/` — even one test for signal_parser.py would be great

## How to submit a broker adapter

1. Copy `brokers/webhook.py` as a template
2. Implement `__init__(self, cfg)` and `execute(self, signal, quantity) -> dict`
3. Add your broker's pip package to `requirements.txt` (commented out)
4. Update the broker table in README.md
5. Open a PR

## Schema compatibility

If your version of TradeMAV uses different column names, add a row to this table:

| TradeMAV version | table | ticker col | direction col | strength col | aligned col |
|---|---|---|---|---|---|
| v1.0 (USB batch 1) | notifications | ticker | direction | strength | signals_aligned |
| your version here | ? | ? | ? | ? | ? |

All configurable via config.json — no code changes needed.
