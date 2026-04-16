from .base import BrokerAdapter

class ZerodhaAdapter(BrokerAdapter):
    """
    STUB — needs implementation.
    
    Install: pip install kiteconnect
    Docs: https://kite.trade/docs/pykiteconnect/v4/
    
    The access_token refreshes daily — you'll need to handle that
    (kiteconnect has a login flow). See their docs for the token flow.
    
    Implement execute() using:
      self.kite.place_order(
          tradingsymbol=signal.ticker,
          exchange="NSE",
          transaction_type="BUY" or "SELL",
          quantity=quantity,
          order_type="MARKET",
          product="CNC",
          variety="regular"
      )
    """
    def __init__(self, cfg):
        raise NotImplementedError(
            "Zerodha adapter not yet implemented. "
            "See CONTRIBUTING.md — this is the #1 wanted contribution."
        )

    def execute(self, signal, quantity: int) -> dict:
        raise NotImplementedError
