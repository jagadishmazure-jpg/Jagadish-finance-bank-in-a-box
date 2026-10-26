# Threat model (STRIDE + LLM-flavoured risks)

| Threat | Where | Mitigation in this scaffold | Residual |
|---|---|---|---|
| Spoofed approver (a typed name finalises a memo) | `approvals.py` | Named approver required; scope + expiry + single-use | Names are not verified identity — see limitations |
| Tampered memo (agents edit each other's findings) | `orchestrator.py` | Agents never message each other; orchestrator is sole writer | Orchestrator itself is trusted; no signed findings |
| Repudiation (nobody can prove who finalised) | — | None yet | No audit log — planned, not claimed |
| Information disclosure (contact/PII in outputs) | `redaction.py`, views | Masked views + two-layer redaction + authorizer | Pattern-based only; unusual layouts escape |
| Denial of service (runaway agent loops, giant reads) | `orchestrator.py`, `store.py` | Loop cap, row cap via `fetchmany(MAX+1)` | Per-instance caps only; no global budget |
| Elevation of privilege (agent reads base tables) | `authorizer.py` | View-only reads, writes/PRAGMA/ATTACH denied, tested | SQLite-only proof; real DB needs re-proof |
| Prompt injection / untrusted tool output | — | No model, no free-text parsing | Returns the moment a model is added — planned evals |
| Confused consent ("yes, wait, no" counted as yes) | `gates.py` | Contradiction + low-confidence + absent-path denials | Confidence is caller-supplied |
| Silent evidence loss (failed agent dropped) | `orchestrator.py`, `memo.py` | Failures section + partial stamp | Reviewer must still read the memo |
| Accidental real send in CI | `notify.py` | Dry-run default, CI refusal, transport injection | Adopter's transport is their responsibility |

## ADRs

### ADR-1: Views + authorizer, not views alone

Views hide columns but do not stop a curious query against the base
table. The authorizer is the enforcement; the views are the
convenience. Decision: both, with the authorizer installed after setup.

### ADR-2: Veto precedence over voting

Three agents voting would let two enthusiasts outvote compliance.
Financial decisions with a rules blocker are not elections. Decision:
precedence rule (BLOCK > REJECT > CONDITIONAL > APPROVE), dissent kept.

### ADR-3: Deterministic agents for the scaffold

A live model would make every test approximate and every demo run
different. Decision: rules now, model behind the same schema later,
with evals as the price of admission.

### ADR-4: Reject, don't clamp

Negative costs and contradictory consent are rejected, not repaired
into something plausible. A repaired value looks like a real value;
a rejection looks like what it is — a broken input that needs a human.
