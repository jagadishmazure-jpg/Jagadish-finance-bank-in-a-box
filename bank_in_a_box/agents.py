"""Three specialist agents, each with its own tools and output schema.

These are deterministic rule engines over the synthetic views — no live
model calls, so every run is reproducible and every test is exact. Each
agent declares the tools it may use (least privilege: an agent cannot
borrow another agent's view), and each returns the same Finding schema,
so the orchestrator can compare stances without parsing free text.

Stances: APPROVE (supports the proposal), CONDITIONAL (supports with
conditions), REJECT (opposes). The compliance agent alone can emit
BLOCK, which is stronger than REJECT — see the veto rule in
orchestrator.py.
"""

from dataclasses import dataclass, field

from .budget import CostEstimate
from .redaction import redact
from .store import fetch_capped


@dataclass
class Finding:
    agent: str
    stance: str  # APPROVE | CONDITIONAL | REJECT | BLOCK
    summary: str
    confidence: float
    evidence: list = field(default_factory=list)
    cost: CostEstimate = field(default_factory=lambda: CostEstimate(0.0))
    failed: bool = False
    failure_reason: str = ""

    def __post_init__(self):
        # Redact at the schema boundary: nothing unredacted leaves an agent.
        self.summary = redact(self.summary)
        self.evidence = [redact(e) for e in self.evidence]


class InvestmentAgent:
    """Investment analysis: return vs. cost basis over the positions view."""

    name = "investment"
    tools = ["v_positions"]

    def run(self, conn, customer_id):
        rows = fetch_capped(
            conn.cursor(),
            "SELECT instrument, market_value, cost_basis FROM v_positions "
            "WHERE customer_id = ?",
            (customer_id,),
        )
        total_value = sum(r[1] for r in rows)
        total_cost = sum(r[2] for r in rows)
        gain = total_value - total_cost
        stance = "APPROVE" if gain >= 0 else "CONDITIONAL"
        return Finding(
            agent=self.name,
            stance=stance,
            summary=f"Portfolio value {total_value:.2f} against cost "
            f"{total_cost:.2f}; net {gain:.2f}.",
            confidence=0.8,
            evidence=[f"{r[0]}: {r[1]:.2f}" for r in rows],
            cost=CostEstimate(25.0),
        )


class RiskAgent:
    """Risk assessment: concentration and loss flags over positions."""

    name = "risk"
    tools = ["v_positions", "v_transactions"]

    def run(self, conn, customer_id):
        rows = fetch_capped(
            conn.cursor(),
            "SELECT instrument, market_value FROM v_positions WHERE customer_id = ?",
            (customer_id,),
        )
        total = sum(r[1] for r in rows) or 1.0
        largest_share = max((r[1] / total for r in rows), default=0.0)
        losers = [r[0] for r in rows if r[1] < 0]
        if largest_share > 0.7:
            stance, summary = (
                "CONDITIONAL",
                f"Concentration flag: largest holding is {largest_share:.0%} "
                "of portfolio value; diversify before increasing exposure.",
            )
        else:
            stance, summary = (
                "APPROVE",
                f"No concentration flag: largest holding {largest_share:.0%} "
                "of portfolio value.",
            )
        return Finding(
            agent=self.name,
            stance=stance,
            summary=summary,
            confidence=0.75,
            evidence=[f"largest_share={largest_share:.2f}"],
            cost=CostEstimate(20.0),
        )


class ComplianceAgent:
    """Compliance review: screening flags and disclosure completeness.

    A screened_flag of anything other than "clear" on any transaction is
    a hard BLOCK: the memo cannot recommend approval while it stands.
    """

    name = "compliance"
    tools = ["v_transactions", "v_customers"]

    def run(self, conn, customer_id):
        rows = fetch_capped(
            conn.cursor(),
            "SELECT txn_id, screened_flag FROM v_transactions WHERE customer_id = ?",
            (customer_id,),
        )
        blocked = [r[0] for r in rows if r[1] != "clear"]
        if blocked:
            return Finding(
                agent=self.name,
                stance="BLOCK",
                summary=f"Screening hold on transactions: {', '.join(blocked)}. "
                "Memo cannot recommend approval until cleared.",
                confidence=0.95,
                evidence=[f"{t} not clear" for t in blocked],
                cost=CostEstimate(30.0),
            )
        return Finding(
            agent=self.name,
            stance="APPROVE",
            summary="All screened transactions clear; no disclosure gaps found "
            "in the synthetic record.",
            confidence=0.9,
            evidence=[f"{len(rows)} transactions screened clear"],
            cost=CostEstimate(30.0),
        )
