"""Agents, orchestrator failure handling, veto rule, dissent, checkpoints."""

import sqlite3

import pytest

from bank_in_a_box.agents import ComplianceAgent, InvestmentAgent, RiskAgent
from bank_in_a_box.approvals import make_approval
from bank_in_a_box.gates import evaluate_consent
from bank_in_a_box.memo import DecisionMemo
from bank_in_a_box.orchestrator import (
    DelegationConflict,
    LoopDetected,
    Orchestrator,
)
from bank_in_a_box.store import build_database


@pytest.fixture()
def conn():
    return build_database()


def test_each_agent_has_own_tools_and_schema(conn):
    agents = [InvestmentAgent(), RiskAgent(), ComplianceAgent()]
    names = {a.name for a in agents}
    assert names == {"investment", "risk", "compliance"}
    for agent in agents:
        finding = agent.run(conn, "CUST-001")
        assert finding.agent == agent.name
        assert finding.stance in {"APPROVE", "CONDITIONAL", "REJECT", "BLOCK"}
        assert finding.summary and finding.confidence > 0


def test_agent_tools_are_least_privilege():
    assert InvestmentAgent().tools == ["v_positions"]
    assert "v_customers" not in InvestmentAgent().tools
    assert ComplianceAgent().tools == ["v_transactions", "v_customers"]


def test_demo_customer_memo_is_draft_with_three_findings(conn):
    memo = Orchestrator(conn).build_memo("MEMO-001", "CUST-001")
    assert memo.status == "DRAFT"
    assert len(memo.findings) == 3
    assert memo.recommendation in {"APPROVE", "CONDITIONAL", "REJECT"}
    assert not memo.partial and not memo.failures


def test_compliance_veto_beats_investment_enthusiasm(conn):
    # Seed a non-clear screening flag through a pre-authorizer connection:
    # build a second database with a blocked transaction instead.
    raw = sqlite3.connect(":memory:")
    raw.executescript(
        "CREATE TABLE customers (customer_id TEXT, full_name TEXT, email TEXT,"
        " ssn TEXT, segment TEXT);"
        "CREATE TABLE positions (position_id TEXT, customer_id TEXT,"
        " instrument TEXT, market_value REAL, cost_basis REAL);"
        "CREATE TABLE transactions (txn_id TEXT, customer_id TEXT, amount REAL,"
        " kind TEXT, screened_flag TEXT);"
        "CREATE VIEW v_customers AS SELECT customer_id, segment FROM customers;"
        "CREATE VIEW v_positions AS SELECT position_id, customer_id, instrument,"
        " market_value, cost_basis FROM positions;"
        "CREATE VIEW v_transactions AS SELECT txn_id, customer_id, amount, kind,"
        " screened_flag FROM transactions;"
    )
    raw.execute("INSERT INTO customers VALUES ('CUST-9','X','x@x.invalid','000-00-0009','growth')")
    raw.execute("INSERT INTO positions VALUES ('P1','CUST-9','FUND (FICTIONAL)',100.0,50.0)")
    raw.execute("INSERT INTO transactions VALUES ('T1','CUST-9',10.0,'transfer','hold')")
    raw.commit()
    from bank_in_a_box.authorizer import attach_authorizer

    attach_authorizer(raw)
    memo = Orchestrator(raw).build_memo("MEMO-VETO", "CUST-9")
    stances = {f.agent: f.stance for f in memo.findings}
    assert stances["investment"] == "APPROVE"
    assert stances["compliance"] == "BLOCK"
    assert memo.recommendation == "REJECT"
    assert memo.veto_applied is True
    assert any(f.agent == "investment" for f in memo.dissent())


def test_dissent_recorded_not_hidden(conn):
    memo = DecisionMemo(
        memo_id="M", customer_id="CUST-001", recommendation="REJECT",
        findings=[
            type("F", (), {"agent": "investment", "stance": "APPROVE",
                           "summary": "looks good"})(),
        ],
    )
    rendered = memo.render()
    assert "Dissent" in rendered and "investment" in rendered


def test_delegation_conflict_detected():
    orch = Orchestrator(build_database())
    orch.delegate("task-x", "investment")
    with pytest.raises(DelegationConflict):
        orch.delegate("task-x", "risk")
    assert orch.conflicts  # conflict recorded, not swallowed


def test_loop_detection_quarantines_agent():
    orch = Orchestrator(build_database())
    orch.delegate("task-loop", "investment")
    for _ in range(2):
        orch.run_agent("task-loop", "investment", "CUST-001")
    with pytest.raises(LoopDetected):
        orch.run_agent("task-loop", "investment", "CUST-001")


def test_cascading_error_contained_not_poisoning(conn):
    orch = Orchestrator(conn)
    original = orch.agents["risk"].run

    def boom(*_a, **_k):
        raise RuntimeError("risk engine exploded")

    orch.agents["risk"].run = boom
    memo = orch.build_memo("MEMO-CASCADE", "CUST-001")
    assert memo.partial is True
    assert len(memo.findings) == 2  # investment + compliance still stand
    assert any(agent == "risk" for agent, _ in memo.failures)
    assert "risk engine exploded" in memo.render()
    orch.agents["risk"].run = original


def test_checkpoint_blocks_finalise_without_human():
    memo = Orchestrator(build_database()).build_memo("MEMO-001", "CUST-001")
    with pytest.raises(Exception):
        memo.finalise(make_approval("Ada Reviewer", "finalise-memo:MEMO-001"), None)
    assert memo.status == "DRAFT"


def test_finalise_with_gate_and_named_approval():
    memo = Orchestrator(build_database()).build_memo("MEMO-001", "CUST-001")
    gate = evaluate_consent("yes", 0.9)
    memo.finalise(make_approval("Ada Reviewer", "finalise-memo:MEMO-001"), gate)
    assert memo.status == "FINAL"
    assert "Status: FINAL" in memo.render()


def test_rendered_memo_contains_no_pii(conn):
    from bank_in_a_box.redaction import contains_pii

    memo = Orchestrator(conn).build_memo("MEMO-001", "CUST-001")
    assert not contains_pii(memo.render())
