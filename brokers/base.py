from abc import ABC, abstractmethod

class BrokerAdapter(ABC):
    @abstractmethod
    def execute(self, signal, quantity: int) -> dict:
        """Place or simulate an order. Return a result dict."""
        ...
