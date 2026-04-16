def should_fire(sig, cfg: dict) -> bool:
    if sig.ticker in cfg.get("excluded_tickers", []):
        return False
    if sig.strength < cfg.get("min_strength", 0.70):
        return False
    if sig.signals_aligned < cfg.get("min_aligned", 14):
        return False
    return True
