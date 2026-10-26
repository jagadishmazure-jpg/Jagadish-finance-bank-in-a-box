"""Cost / budget inputs: negatives are rejected, never clamped silently.

Clamping a negative cost to zero would hide a broken estimate and let a
bad agent look cheap. Rejecting forces the caller to fix the input, and
the rejection is recorded in the memo's failure section when it happens
inside an agent run (see orchestrator cascade containment).
"""

import math
from dataclasses import dataclass


class NegativeCostError(ValueError):
    """A cost or budget input was negative (or not a finite number)."""


@dataclass(frozen=True)
class CostEstimate:
    amount: float
    currency: str = "USD"

    def __post_init__(self):
        if not isinstance(self.amount, (int, float)) or isinstance(self.amount, bool):
            raise NegativeCostError("cost must be a number")
        if math.isnan(self.amount) or math.isinf(self.amount):
            raise NegativeCostError("cost must be a finite number")
        if self.amount < 0:
            raise NegativeCostError(f"negative cost rejected: {self.amount}")
