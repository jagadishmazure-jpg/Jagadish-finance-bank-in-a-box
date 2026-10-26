# Real code excerpts and their real output

Excerpts below are copied from the code in this repo; outputs are from
actual runs (system `python3`, stdlib only).

## The veto rule

```python
# bank_in_a_box/orchestrator.py — _resolve
stances = [f.stance for f in findings]
if "BLOCK" in stances:
    return "REJECT"
if "REJECT" in stances:
    return "REJECT"
if "CONDITIONAL" in stances:
    return "CONDITIONAL"
return "APPROVE"
```

## The authorizer rule

```python
# bank_in_a_box/authorizer.py — inside make_authorizer()
if action == sqlite3.SQLITE_READ:
    # arg1 = table being read; source = view the read goes through
    if arg1 in ALLOWED_VIEWS or source in ALLOWED_VIEWS:
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY
```

## Demo run (actual output)

Command: `python3 -m bank_in_a_box.demo`

```
DECISION MEMO MEMO-001 — customer CUST-001
Status: DRAFT
Recommendation: APPROVE

Findings:
 - [investment] APPROVE: Portfolio value 200000.00 against cost 182000.00; net 18000.00.
 - [risk] APPROVE: No concentration flag: largest holding 60% of portfolio value.
 - [compliance] APPROVE: All screened transactions clear; no disclosure gaps found in the synthetic record.
```

Finalised run (`python3 -m bank_in_a_box.demo --finalise --approver "Ada Reviewer"`)
renders the same memo with `Status: FINAL`. A veto-scenario run (see
`test_compliance_veto_beats_investment_enthusiasm`) renders
`Recommendation: REJECT` with `Compliance veto applied` and the
investment APPROVE preserved under Dissent.

## Test run (actual output)

Command: `python3 -m pytest tests/ -q`

```
53 passed in 0.12s
```

Sample size note: 53 tests is the full suite of this scaffold, not a
quality claim about any production system — it is a regression suite
over deterministic rule engines and enforcement boundaries.
