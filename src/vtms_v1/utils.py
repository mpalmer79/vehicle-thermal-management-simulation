from __future__ import annotations


def clip(value: float, low: float, high: float) -> float:
    if low > high:
        raise ValueError("low must not exceed high")
    return min(max(value, low), high)


def validate_health(name: str, value: float) -> float:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be in [0, 1], got {value}")
    return value
