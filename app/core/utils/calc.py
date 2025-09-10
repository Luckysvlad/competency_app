from __future__ import annotations
from typing import List

def normalize_weights(weights: List[float]) -> list[float]:
    """Нормализует список весов к сумме 1.0.
    Если сумма == 0, распределяет равномерно.
    Отрицательные приводит к 0.
    """
    clean = [max(0.0, float(w) if w is not None else 0.0) for w in weights]
    s = sum(clean)
    if s <= 0:
        n = len(clean) if len(clean) > 0 else 1
        return [1.0 / n for _ in clean]
    return [w / s for w in clean]
