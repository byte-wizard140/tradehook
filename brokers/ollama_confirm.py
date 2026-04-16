import requests
from .base import BrokerAdapter

class OllamaAdapter(BrokerAdapter):
    """
    Sends the signal to a local Ollama instance for confirmation
    before forwarding to the next broker in chain.
    Useful as a sanity-check layer — configure a downstream broker
    in config under "ollama_then_broker".
    """
    def __init__(self, cfg):
        self.url     = cfg.get("ollama_url", "http://localhost:11434")
        self.model   = cfg.get("ollama_model", "llama3")
        self.tmpl    = cfg.get(
            "ollama_prompt_template",
            "TradeMAV signal: {ticker} {direction} strength={strength:.2f} "
            "aligned={signals_aligned} signals. Should I act on this? Reply YES or NO first."
        )
        self._downstream = None
        downstream = cfg.get("ollama_then_broker")
        if downstream:
            self._downstream = self._load_downstream(downstream, cfg)

    def _load_downstream(self, name, cfg):
        if name == "alpaca":
            from .alpaca import AlpacaAdapter
            return AlpacaAdapter(cfg)
        elif name == "webhook":
            from .webhook import WebhookAdapter
            return WebhookAdapter(cfg)
        elif name == "zerodha":
            from .zerodha_kite import ZerodhaAdapter
            return ZerodhaAdapter(cfg)
        return None

    def execute(self, signal, quantity: int) -> dict:
        prompt = self.tmpl.format(
            ticker=signal.ticker,
            direction=signal.direction,
            strength=signal.strength,
            signals_aligned=signal.signals_aligned
        )
        try:
            r = requests.post(
                f"{self.url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=30
            )
            response_text = r.json().get("response", "").strip()
            print(f"[Ollama] {self.model} says: {response_text[:120]}")
            confirmed = response_text.upper().startswith("YES")
        except Exception as e:
            print(f"[Ollama] Request failed: {e} — skipping signal")
            return {"status": "ollama_error", "ticker": signal.ticker}

        if confirmed and self._downstream:
            return self._downstream.execute(signal, quantity)
        elif confirmed:
            return {"status": "ollama_confirmed_no_downstream", "ticker": signal.ticker}
        else:
            return {"status": "ollama_rejected", "ticker": signal.ticker}
