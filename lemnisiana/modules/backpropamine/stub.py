from typing import Any, Dict

def train(steps: int = 10) -> Dict[str, float]:
    loss_start = 0.8
    loss_end = max(0.1, loss_start - steps*0.02)
    return {"loss_start": round(loss_start,4), "loss_end": round(loss_end,4), "stable": True}
