from .base import BrokerAdapter

class AlpacaAdapter(BrokerAdapter):
    def __init__(self, cfg):
        try:
            import alpaca_trade_api as tradeapi
            self.api = tradeapi.REST(
                cfg["alpaca_api_key"],
                cfg["alpaca_secret_key"],
                base_url=cfg.get("alpaca_base_url", "https://paper-api.alpaca.markets")
            )
        except ImportError:
            raise ImportError("pip install alpaca-trade-api")

    def execute(self, signal, quantity: int) -> dict:
        side = "buy" if signal.direction == "BUY" else "sell"
        order = self.api.submit_order(
            symbol=signal.ticker,
            qty=quantity,
            side=side,
            type="market",
            time_in_force="gtc"
        )
        return {"id": order.id, "status": order.status, "ticker": signal.ticker}
