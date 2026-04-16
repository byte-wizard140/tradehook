import requests
from .base import BrokerAdapter

class WebhookAdapter(BrokerAdapter):
    def __init__(self, cfg):
        self.url     = cfg["webhook_url"]
        self.headers = cfg.get("webhook_headers", {"Content-Type": "application/json"})

    def execute(self, signal, quantity: int) -> dict:
        payload = {
            "ticker": signal.ticker,
            "direction": signal.direction,
            "strength": signal.strength,
            "signals_aligned": signal.signals_aligned,
            "quantity": quantity,
            "timestamp": signal.timestamp
        }
        r = requests.post(self.url, json=payload, headers=self.headers, timeout=10)
        return {"status": r.status_code, "ticker": signal.ticker}
