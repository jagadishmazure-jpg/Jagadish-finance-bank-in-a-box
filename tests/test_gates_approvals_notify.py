"""Confirmation gates, approvals, email channel."""

import os
from datetime import datetime, timedelta, timezone

import pytest

from bank_in_a_box.approvals import Approval, ApprovalError, make_approval
from bank_in_a_box.gates import (
    GateDenied,
    GateNotEvaluated,
    evaluate_consent,
)
from bank_in_a_box.memo import DecisionMemo
from bank_in_a_box.notify import (
    EmailChannel,
    NoTransportConfigured,
    RefusedInCI,
)


def test_gate_approves_clear_yes():
    assert evaluate_consent("yes", 0.9) == "approved"


def test_gate_rejects_explicit_no():
    with pytest.raises(GateDenied):
        evaluate_consent("no", 0.9)


def test_gate_absent_consent_denied():
    with pytest.raises(GateDenied):
        evaluate_consent(None, 0.9)
    with pytest.raises(GateDenied):
        evaluate_consent("   ", 0.9)


def test_gate_low_confidence_denied():
    with pytest.raises(GateDenied):
        evaluate_consent("yes", 0.3)


def test_gate_self_contradicting_consent_denied():
    with pytest.raises(GateDenied):
        evaluate_consent("yes, wait, no", 0.95)


def test_gate_yes_but_no_denied():
    with pytest.raises(GateDenied):
        evaluate_consent("yes but no, stop", 0.95)


def _memo():
    return DecisionMemo(memo_id="MEMO-T", customer_id="CUST-001",
                        recommendation="APPROVE")


def test_finalise_without_gate_raises_not_evaluated():
    with pytest.raises(GateNotEvaluated):
        _memo().finalise(make_approval("Ada Reviewer", "finalise-memo:MEMO-T"), None)


def test_finalise_bypass_without_approval_raises():
    # Gate approved, but no approval object can be smuggled past finalise:
    # passing an approval scoped to something else must fail.
    memo = _memo()
    wrong = make_approval("Ada Reviewer", "finalise-memo:OTHER")
    with pytest.raises(ApprovalError):
        memo.finalise(wrong, "approved")
    assert memo.status == "DRAFT"


def test_approval_expired_rejected():
    past = Approval("Ada Reviewer", "finalise-memo:MEMO-T",
                    datetime.now(timezone.utc) - timedelta(minutes=1))
    with pytest.raises(ApprovalError):
        past.use("finalise-memo:MEMO-T")


def test_approval_wrong_scope_rejected():
    ap = make_approval("Ada Reviewer", "finalise-memo:MEMO-T")
    with pytest.raises(ApprovalError):
        ap.use("finalise-memo:MEMO-OTHER")


def test_approval_single_use():
    ap = make_approval("Ada Reviewer", "finalise-memo:MEMO-T")
    assert ap.use("finalise-memo:MEMO-T") is True
    with pytest.raises(ApprovalError):
        ap.use("finalise-memo:MEMO-T")


def test_approval_anonymous_rejected():
    ap = make_approval("", "finalise-memo:MEMO-T")
    with pytest.raises(ApprovalError):
        ap.use("finalise-memo:MEMO-T")


def test_finalise_happy_path():
    memo = _memo()
    memo.finalise(make_approval("Ada Reviewer", "finalise-memo:MEMO-T"), "approved")
    assert memo.status == "FINAL"


def test_email_dry_run_by_default():
    rec = EmailChannel().send("a@example.invalid", "Memo ready", "body")
    assert rec.sent is False and rec.dry_run is True


def test_email_opt_in_without_transport_refused():
    with pytest.raises(NoTransportConfigured):
        EmailChannel(dry_run=False).send(
            "a@example.invalid", "Memo", "body", opt_in=True)


def test_email_refused_in_ci(monkeypatch):
    monkeypatch.setenv("CI", "true")
    sent = []
    ch = EmailChannel(dry_run=False, transport=lambda *a: sent.append(a))
    with pytest.raises(RefusedInCI):
        ch.send("a@example.invalid", "Memo", "body", opt_in=True)
    assert sent == []


def test_email_opt_in_with_transport_sends(monkeypatch):
    monkeypatch.delenv("CI", raising=False)
    sent = []
    ch = EmailChannel(dry_run=False, transport=lambda *a: sent.append(a))
    rec = ch.send("a@example.invalid", "Memo", "body", opt_in=True)
    assert rec.sent is True and len(sent) == 1
