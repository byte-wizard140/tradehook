import requests, json

class NtfyListener:
    """
    Subscribes to your TradeMAV ntfy topic via SSE stream.
    Pairs with: https://github.com/byte-wizard140/ntfy-signal-relay
    """
    def __init__(self, cfg):
        self.url = cfg["ntfy_topic_url"].rstrip("/") + "/sse"
        self.headers = {}
        if cfg.get("ntfy_token"):
            self.headers["Authorization"] = f"Bearer {cfg['ntfy_token']}"

    def poll(self):
        print(f"[NtfyListener] Connecting to {self.url}")
        while True:
            try:
                with requests.get(self.url, stream=True,
                                  headers=self.headers, timeout=90) as r:
                    for line in r.iter_lines():
                        if not line:
                            continue
                        line = line.decode("utf-8")
                        if line.startswith("data:"):
                            try:
                                payload = json.loads(line[5:].strip())
                                # ntfy message body should be JSON from TradeMAV
                                # e.g. {"ticker":"AAPL","direction":"BUY","strength":0.82}
                                msg = payload.get("message", "")
                                if isinstance(msg, str):
                                    msg = json.loads(msg)
                                if isinstance(msg, dict):
                                    yield msg
                            except (json.JSONDecodeError, KeyError):
                                pass  # non-signal ntfy message, skip
            except Exception as e:
                print(f"[NtfyListener] Reconnecting after error: {e}")
                import time; time.sleep(5)
