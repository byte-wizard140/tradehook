# tradehook 🔌

A community-built bridge that reads TradeMAV signals and forwards them to brokers, 
webhooks, or a local AI for confirmation.

**This is not an official TradeMAV product.** It's an independent open-source tool 
built by TradeMAV users, for TradeMAV users. Zero modifications to your USB required.

---

## What it does

TradeMAV runs on your machine. This bridge sits next to it, watches for signals, 
and acts on them — placing orders, firing webhooks, or asking a local LLM whether 
to proceed. You configure everything. Nothing happens without you setting it up.

```
[TradeMAV USB] ──signals──> [tradehook] ──orders──> [Zerodha / Alpaca / webhook]
                                   └──────> [Local Ollama AI confirm]
```

---

## How it reads signals (pick one)

### Option A — SQLite direct (same machine, most reliable)
Reads `trademav.db` directly. Read-only, zero interference with TradeMAV.
Open your DB with [DB Browser for SQLite](https://sqlitebrowser.org/) to confirm 
your table/column names, then set them in `config.json`.

### Option B — ntfy listener (works remotely too)
If TradeMAV pushes notifications to an ntfy topic, the bridge subscribes to the 
same topic. Pairs naturally with the 
[ntfy-signal-relay](https://github.com/byte-wizard140/ntfy-signal-relay) 
if you're already using that.

---

## Quick start

```bash
git clone https://github.com/byte-wizard140/tradehook
cd tradehook
pip install -r requirements.txt
cp config.example.json config.json
# edit config.json with your DB path, broker keys, etc.
python bridge.py --dry-run
```

`--dry-run` is on by default. It logs everything but places zero orders. 
Turn it off only when you're confident it's working.

---

## Broker support

| Broker | Status |
|---|---|
| Alpaca (US stocks/crypto) | ✅ Working |
| Webhook (generic POST) | ✅ Working |
| Ollama (local AI confirm) | ✅ Working |
| Zerodha Kite | 🚧 Stub — needs contributor |
| Angel One | 🚧 Stub — needs contributor |
| Upstox | 🚧 Stub — needs contributor |

---

## Local AI confirmation (Ollama)

Set `"broker": "ollama"` to route signals through a local Ollama instance before 
any order is placed. The bridge sends signal data to your chosen model and only 
proceeds if it responds with a clear go-ahead.

Useful if you want an extra sanity check before live execution, or if you're 
running something like a local knowledge base and want context-aware filtering.

```json
{
  "broker": "ollama",
  "ollama_url": "http://localhost:11434",
  "ollama_model": "llama3",
  "ollama_prompt_template": "TradeMAV signal: {ticker} {direction} strength={strength}. Briefly confirm if this aligns with current market conditions. Reply YES or NO first."
}
```

---

## config.json fields

```json
{
  "ingest_mode": "sqlite",            // "sqlite" or "ntfy"

  // SQLite mode
  "db_path": "D:/TradeMAV/trademav.db",
  "schema": {
    "table": "notifications",
    "col_id": "id",
    "col_ticker": "ticker",
    "col_direction": "direction",
    "col_strength": "strength",
    "col_aligned": "signals_aligned",
    "col_timestamp": "updated_at"
  },

  // ntfy mode
  "ntfy_topic_url": "https://ntfy.sh/your-topic",

  "poll_interval": 60,
  "min_strength": 0.70,
  "min_aligned": 14,
  "excluded_tickers": [],
  "dry_run": true,

  "broker": "alpaca",               // alpaca | webhook | ollama | zerodha | angel_one
  "default_qty": 1,
  "quantities": {
    "AAPL": 5,
    "RELIANCE.NS": 3
  }
}
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The biggest need right now is Zerodha Kite, 
Angel One, and Upstox broker adapters. If you've got kiteconnect experience, 
the base adapter interface is dead simple — 3 methods to implement.

---

## Disclaimer

See [DISCLAIMER.md](DISCLAIMER.md). Short version: this is a community tool, 
not financial advice, not affiliated with TradeMAV. You are fully responsible 
for any trades executed using this software. Always test with `--dry-run` first.

---

## Related

- [ntfy-signal-relay](https://github.com/byte-wizard140/ntfy-signal-relay) — 
  parse TradeMAV's ntfy notifications (companion tool, same account)
