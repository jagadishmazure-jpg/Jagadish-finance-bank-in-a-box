# Recruiter summary

- **Problem:** a single agent writing a financial decision memo blends
  return-chasing, risk worry, and rule-checking into one voice — and a
  failed agent silently disappears from the evidence.
- **Approach:** three specialist agents (investment, risk, compliance)
  with least-privilege database views, an orchestrator that resolves
  conflicts with a documented veto rule, and human checkpoints before
  any memo goes final.
- **Proof (real runs, this repo):** 53 tests green with system
  `python3 -m pytest` (no virtualenv, stdlib only); every enforcement
  claim in the README names the test that proves it; the demo memo for
  synthetic customer CUST-001 renders three findings and an APPROVE
  recommendation (see `docs/code-excerpts.md` for the exact output).
