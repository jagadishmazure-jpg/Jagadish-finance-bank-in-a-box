"""Decision memo: all three views, dissent recorded, failures visible.

A memo is born DRAFT and becomes FINAL only through
:meth:`DecisionMemo.finalise`, which requires a consumed human approval
and an approved confirmation gate. Nothing in this module can mark a
memo final on its own.

Dissent is a first-class section, not a footnote: any agent whose stance
differs from the final recommendation is listed by name with its stance
and summary. Agent failures get their own section too — a memo that
silently dropped a failed agent would be a lie about its own evidence.
"""

from dataclasses import dataclass, field

from .approvals import ApprovalError
from .gates import GateDenied, GateNotEvaluated
from .redaction import redact


@dataclass
class DecisionMemo:
    memo_id: str
    customer_id: str
    recommendation: str  # APPROVE | CONDITIONAL | REJECT
    findings: list = field(default_factory=list)
    failures: list = field(default_factory=list)  # (agent, reason)
    conflicts: list = field(default_factory=list)  # human-readable notes
    veto_applied: bool = False
    partial: bool = False
    status: str = "DRAFT"

    def dissent(self):
        """Findings whose stance disagrees with the recommendation."""
        return [
            f for f in self.findings
            if f.stance != self.recommendation and f.stance != "BLOCK"
        ] + [f for f in self.findings if f.stance == "BLOCK" and self.recommendation != "REJECT"]

    def finalise(self, approval, gate_result):
        """Mark FINAL. Requires a valid approval and an approved gate."""
        if gate_result is None:
            raise GateNotEvaluated("no confirmation gate was evaluated")
        if gate_result != "approved":
            raise GateDenied(f"gate did not approve: {gate_result!r}")
        try:
            approval.use(f"finalise-memo:{self.memo_id}")
        except ApprovalError as exc:
            raise ApprovalError(f"cannot finalise {self.memo_id}: {exc}") from exc
        self.status = "FINAL"
        return self

    def render(self):
        """Plain-text memo. Redacted again at render time (defence in depth)."""
        lines = [
            f"DECISION MEMO {self.memo_id} — customer {self.customer_id}",
            f"Status: {self.status}",
            f"Recommendation: {self.recommendation}",
        ]
        if self.veto_applied:
            lines.append("Compliance veto applied: recommendation capped at REJECT.")
        if self.partial:
            lines.append("PARTIAL MEMO: one or more agents failed; see Failures.")
        lines.append("")
        lines.append("Findings:")
        for f in self.findings:
            lines.append(f" - [{f.agent}] {f.stance}: {f.summary}")
        dissent = self.dissent()
        if dissent:
            lines.append("")
            lines.append("Dissent (recorded, not hidden):")
            for f in dissent:
                lines.append(f" - [{f.agent}] {f.stance}: {f.summary}")
        if self.failures:
            lines.append("")
            lines.append("Failures (contained, not silently dropped):")
            for agent, reason in self.failures:
                lines.append(f" - [{agent}] {reason}")
        if self.conflicts:
            lines.append("")
            lines.append("Conflicts resolved:")
            for note in self.conflicts:
                lines.append(f" - {note}")
        return redact("\n".join(lines))
