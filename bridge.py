#!/usr/bin/env python3
"""
tradehook — community bridge for TradeMAV signals
Run with: python bridge.py [--dry-run] [--config config.json]
"""
import argparse, json, sys
from ingest.sqlite_reader import SQLiteReader
from ingest.ntfy_listener import NtfyListener
from core.signal_parser import parse
from core.threshold_engine import should_fire

def load_broker(cfg):
    b = cfg.get("broker", "webhook")
    if b == "alpaca":
        from brokers.alpaca import AlpacaAdapter
        return AlpacaAdapter(cfg)
    elif b == "ollama":
        from brokers.ollama_confirm import OllamaAdapter
        return OllamaAdapter(cfg)
    elif b == "webhook":
        from brokers.webhook import WebhookAdapter
        return WebhookAdapter(cfg)
    elif b == "zerodha":
        from brokers.zerodha_kite import ZerodhaAdapter
        return ZerodhaAdapter(cfg)
    else:
        raise ValueError(f"Unknown broker: {b}. Check config.json.")

def main():
    parser = argparse.ArgumentParser(description="tradehook")
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cfg = json.load(open(args.config))
    dry_run = args.dry_run or cfg.get("dry_run", True)

    if dry_run:
        print("[tradehook] DRY RUN mode — no orders will be placed")

    broker = load_broker(cfg)

    mode = cfg.get("ingest_mode", "sqlite")
    if mode == "sqlite":
        ingest = SQLiteReader(cfg)
    elif mode == "ntfy":
        ingest = NtfyListener(cfg)
    else:
        print(f"Unknown ingest_mode: {mode}")
        sys.exit(1)

    print(f"[tradehook] Listening via {mode}...")

    for raw in ingest.poll():
        sig = parse(raw, cfg)
        if not sig:
            continue
        if should_fire(sig, cfg):
            qty = cfg.get("quantities", {}).get(sig.ticker, cfg.get("default_qty", 1))
            print(f"[SIGNAL] {sig.ticker} {sig.direction} | strength={sig.strength:.2f} | aligned={sig.signals_aligned}")
            if dry_run:
                print(f"[DRY RUN] Would place: {sig.direction} {qty}x {sig.ticker}")
            else:
                result = broker.execute(sig, qty)
                print(f"[ORDER] {result}")

if __name__ == "__main__":
    main()
