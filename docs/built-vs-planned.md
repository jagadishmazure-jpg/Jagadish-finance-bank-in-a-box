# Built vs planned

| Item | Status |
|---|---|
| Three specialist agents (investment, risk, compliance) with own tools + Finding schema | Built |
| Orchestrator: divide, delegate, collect, veto resolution | Built |
| Loop detection, delegation-conflict detection, cascade containment | Built |
| Decision memo with dissent + failures sections | Built |
| Human checkpoints (gate + named approval) before FINAL | Built |
| View-aware SQLite authorizer + denial tests | Built |
| PII redaction (cards, emails, phones, SSN) | Built |
| Row cap via `fetchmany(MAX+1)` | Built |
| Negative-cost rejection | Built |
| Hashed brand blocklist + non-empty test | Built |
| Email dry-run default, CI refusal | Built |
| Offline demo + full test suite (53 tests) | Built |
| `knowledge/` distilled notes + Mermaid docs | Built |
| Live-model agents behind the Finding schema | Written-not-run (design in `docs/implementation-guide.md`; no provider wired) |
| Persistent database + audit log for finalisations | Planned |
| Verified-identity approvals (not bare name strings) | Planned |
| CI workflow, CodeQL, Dependabot, branch rulesets | Planned (at push time; deliberately no `.github/` in this scaffold) |
| Deployment / hosted service / package release | Planned — none claimed |
