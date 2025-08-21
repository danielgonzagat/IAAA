import time, random
from typing import List, Dict, Any

def propose(n: int = 1) -> List[Dict[str, Any]]:
    out = []
    for i in range(n):
        out.append({
            "arch_id": f"cand-{int(time.time()*1000)}-{i}",
            "layers": [{"type": "conv", "k": 3, "c": 32}, {"type": "attn", "h": 4}],
            "fitness": round(random.uniform(0.7, 0.95), 4),
        })
    return out
