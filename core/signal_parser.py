from dataclasses import dataclass
from typing import Optional

@dataclass
class Signal:
    ticker: str
    direction: str        # BUY | SELL | HOLD
    strength: float       # 0.0–1.0
    signals_aligned: int
    timestamp: str
    raw: dict

def parse(raw: dict, cfg: dict = None) -> Optional[Signal]:
    try:
        direction = str(raw.get("direction", "")).upper().strip()
        if direction not in ("BUY", "SELL"):
            return None
        return Signal(
            ticker          = str(raw.get("ticker", "")).upper().strip(),
            direction       = direction,
            strength        = float(raw.get("strength") or 0),
            signals_aligned = int(raw.get("signals_aligned") or 0),
            timestamp       = str(raw.get("timestamp") or raw.get("updated_at") or ""),
            raw             = raw
        )
    except Exception as e:
        print(f"[parser] Skipping malformed signal: {e} | raw={raw}")
        return None
