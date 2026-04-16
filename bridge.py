#!/usr/bin/env python3
"""
tradehook — community bridge for TradeMAV signals
Run with: python bridge.py [--dry-run] [--config config.json]
"""
import argparse, json, sys, os, datetime

LOG_FILE = os.path.join(os.path.dirname(__file__), "tradehook.log")
_log_handle = None

def _open_log():
    global _log_handle
    if _log_handle is None:
        _log_handle = open(LOG_FILE, "a", buffering=1, encoding="utf-8")

def log(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    line = f"{ts} {msg}"
    print(line)
    _open_log()
    _log_handle.write(line + "\n")

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
        log("[tradehook] DRY RUN mode — no orders will be placed")

    broker = load_broker(cfg)

    mode = cfg.get("ingest_mode", "sqlite")
    if mode == "sqlite":
        ingest = SQLiteReader(cfg)
    elif mode == "ntfy":
        ingest = NtfyListener(cfg)
    else:
        log(f"Unknown ingest_mode: {mode}")
        sys.exit(1)

    log(f"[tradehook] Listening via {mode} | broker={cfg.get('broker','webhook')} | dry_run={dry_run}")

    for raw in ingest.poll():
        sig = parse(raw, cfg)
        if not sig:
            continue
        if should_fire(sig, cfg):
            qty = cfg.get("quantities", {}).get(sig.ticker, cfg.get("default_qty", 1))
            log(f"[SIGNAL] {sig.ticker} {sig.direction} | strength={sig.strength:.2f} | aligned={sig.signals_aligned}")
            if dry_run:
                log(f"[DRY RUN] Would place: {sig.direction} {qty}x {sig.ticker}")
            else:
                result = broker.execute(sig, qty)
                log(f"[ORDER] {result}")

if __name__ == "__main__":
    main()
