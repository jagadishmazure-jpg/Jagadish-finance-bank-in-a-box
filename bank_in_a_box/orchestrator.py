"""Orchestrator: divide, delegate, collect, resolve — without poisoning.

Responsibilities, in order:

1. Divide the proposal into one task per specialist agent.
2. Delegate, detecting delegation conflicts: the same task assigned to
   two different agents is a conflict, recorded and raised — the second
   assignment never silently overwrites the first.
3. Detect loops: the same agent re-run on the same task more than
   ``MAX_RERUNS`` times is quarantined as a loop failure.
4. Contain cascading errors: one agent's exception becomes a recorded
   failure in the memo; the other agents' findings still stand, the memo
   is flagged partial, and the failure reason is visible — never silent.
5. Resolve conflicts with a documented rule — the compliance veto:
   a compliance BLOCK caps the recommendation at REJECT no matter how
   enthusiastic the investment agent is. The overridden enthusiasm is
   kept in the dissent section, not deleted.
6. Refuse to finalise without the human checkpoints (approval + gate);
   those live in memo.finalise, which the orchestrator calls, never
   bypasses.
"""

from .agents import ComplianceAgent, InvestmentAgent, RiskAgent
from .memo import DecisionMemo

MAX_RERUNS = 2


class DelegationConflict(Exception):
    """The same task was assigned to two different agents."""


class LoopDetected(Exception):
    """An agent was re-run on the same task beyond MAX_RERUNS."""


class Orchestrator:
    def __init__(self, conn):
        self.conn = conn
        self.agents = {
            "investment": InvestmentAgent(),
            "risk": RiskAgent(),
            "compliance": ComplianceAgent(),
        }
        self._assignments = {}  # task_id -> agent name
        self._run_counts = {}  # (agent, task_id) -> runs
        self.conflicts = []

    def delegate(self, task_id, agent_name):
        """Record an assignment, or raise on a conflicting reassignment."""
        previous = self._assignments.get(task_id)
        if previous is not None and previous != agent_name:
            note = (
                f"task {task_id} already assigned to {previous}; "
                f"refused reassignment to {agent_name}"
            )
            self.conflicts.append(note)
            raise DelegationConflict(note)
        self._assignments[task_id] = agent_name
        return agent_name

    def run_agent(self, task_id, agent_name, customer_id):
        """Run one agent with loop detection; returns a Finding or raises."""
        key = (agent_name, task_id)
        self._run_counts[key] = self._run_counts.get(key, 0) + 1
        if self._run_counts[key] > MAX_RERUNS:
            raise LoopDetected(
                f"{agent_name} re-ran task {task_id} "
                f"{self._run_counts[key]} times (max {MAX_RERUNS})"
            )
        return self.agents[agent_name].run(self.conn, customer_id)

    def build_memo(self, memo_id, customer_id):
        """Run all three agents and assemble a DRAFT memo."""
        findings, failures = [], []
        plan = [
            ("task-investment", "investment"),
            ("task-risk", "risk"),
            ("task-compliance", "compliance"),
        ]
        for task_id, agent_name in plan:
            self.delegate(task_id, agent_name)
            try:
                findings.append(self.run_agent(task_id, agent_name, customer_id))
            except Exception as exc:  # contained: never poisons the memo
                failures.append((agent_name, f"{type(exc).__name__}: {exc}"))
        recommendation = self._resolve(findings)
        veto = any(f.stance == "BLOCK" for f in findings)
        return DecisionMemo(
            memo_id=memo_id,
            customer_id=customer_id,
            recommendation=recommendation,
            findings=findings,
            failures=failures,
            conflicts=list(self.conflicts),
            veto_applied=veto,
            partial=bool(failures),
        )

    @staticmethod
    def _resolve(findings):
        """Conflict rule: compliance BLOCK beats investment enthusiasm.

        Precedence: BLOCK -> REJECT; any REJECT -> REJECT; any
        CONDITIONAL -> CONDITIONAL; otherwise APPROVE. The losing views
        survive in the memo's dissent section.
        """
        stances = [f.stance for f in findings]
        if "BLOCK" in stances:
            return "REJECT"
        if "REJECT" in stances:
            return "REJECT"
        if "CONDITIONAL" in stances:
            return "CONDITIONAL"
        return "APPROVE"
