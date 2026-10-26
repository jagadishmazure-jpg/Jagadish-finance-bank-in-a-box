# Guardrails and security controls

Every claim below names the test that proves it. If a control has no
named test, it is not claimed as enforced — see
`docs/built-vs-planned.md`.

| Control | Proof test(s) |
|---|---|
| View-only reads; base tables denied | `test_direct_base_table_read_denied`, `test_direct_positions_table_read_denied`, `test_view_read_allowed` |
| `sqlite_master` unreadable | `test_sqlite_master_read_denied` |
| Writes denied (insert/update/delete, via views too) | `test_insert_denied`, `test_update_and_delete_denied`, `test_write_via_view_denied` |
| PRAGMA / ATTACH / load_extension denied | `test_pragma_denied`, `test_attach_denied`, `test_load_extension_function_denied` |
| Authorizer tests assert behaviour, never message text | suite convention; see `tests/test_authorizer.py` header |
| Gate: bypass blocked (no evaluated gate) | `test_finalise_without_gate_raises_not_evaluated` |
| Gate: recorded refusal blocked | `test_gate_rejects_explicit_no`, `test_finalise_bypass_without_approval_raises` |
| Gate: absent consent blocked | `test_gate_absent_consent_denied` |
| Gate: low confidence blocked | `test_gate_low_confidence_denied` |
| Gate: self-contradicting consent blocked | `test_gate_self_contradicting_consent_denied`, `test_gate_yes_but_no_denied` |
| Approvals: named, single-use, scoped, expiring | `test_approval_anonymous_rejected`, `test_approval_single_use`, `test_approval_wrong_scope_rejected`, `test_approval_expired_rejected` |
| PII redaction: cards + emails + phones + SSN | `test_redact_card_number`, `test_redact_email_address`, `test_redact_phone_and_ssn` |
| Row cap at fetch time (`fetchmany(MAX+1)`, no `LIMIT` rewrite, no `fetchall`) | `test_row_cap_exceeded`, `test_row_cap_boundary_ok`, `test_no_fetchall_in_package_source` |
| Negative / non-finite costs rejected | `test_negative_cost_rejected`, `test_zero_cost_ok_and_nan_rejected` |
| Brand blocklist non-empty + detecting | `test_brand_blocklist_non_empty`, `test_brand_blocklist_detects_blocked_phrase` |
| Email dry-run default; refused in CI; opt-in needs transport | `test_email_dry_run_by_default`, `test_email_refused_in_ci`, `test_email_opt_in_without_transport_refused` |
| Loop detection | `test_loop_detection_quarantines_agent` |
| Delegation-conflict detection | `test_delegation_conflict_detected` |
| Cascade containment | `test_cascading_error_contained_not_poisoning` |
| Compliance veto beats investment enthusiasm | `test_compliance_veto_beats_investment_enthusiasm` |
| Dissent recorded, failures visible | `test_dissent_recorded_not_hidden`, `test_rendered_memo_contains_no_pii` |
| Human checkpoint before FINAL | `test_checkpoint_blocks_finalise_without_human`, `test_finalise_with_gate_and_named_approval` |
