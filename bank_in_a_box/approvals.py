"""Human approvals: named person, single use, scoped, expiring.

An approval is not a boolean. It names who approved, what exact action it
covers, and when it stops being valid — and it is consumed the first time
it is used, so one approval can never finalise two memos.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone


class ApprovalError(Exception):
    """Approval missing, expired, mis-scoped, reused, or anonymous."""


@dataclass
class Approval:
    approver: str  # a named person, never a role label or empty string
    scope: str  # e.g. "finalise-memo:MEMO-001"
    expires_at: datetime
    _used: bool = field(default=False, repr=False)

    def use(self, scope):
        """Consume this approval for *scope*, or raise ApprovalError."""
        if not self.approver or not self.approver.strip():
            raise ApprovalError("approval has no named approver")
        if self._used:
            raise ApprovalError("approval already used (single-use)")
        if self.scope != scope:
            raise ApprovalError(
                f"approval scoped to {self.scope!r}, not {scope!r}"
            )
        if datetime.now(timezone.utc) >= self.expires_at:
            raise ApprovalError("approval expired")
        self._used = True
        return True


def make_approval(approver, scope, minutes_valid=60):
    """Convenience constructor: approval valid for *minutes_valid* minutes."""
    return Approval(
        approver=approver,
        scope=scope,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=minutes_valid),
    )
