# Security policy

This is a portfolio scaffold with synthetic data only. It is not a
production financial system and must not be used for real financial
decisions or real customer data.

## What is protected here

- Database access is view-only for agents (see
  `bank_in_a_box/authorizer.py`); writes, PRAGMA, ATTACH, and
  `load_extension()` are denied and tested.
- Agent outputs and rendered memos pass through PII redaction (cards,
  emails, phones, SSN-shaped strings).
- Memos cannot become FINAL without a confirmation gate pass and a
  named, single-use, scoped, unexpired approval.
- Email sends dry-run by default and are refused in CI.

## Known gaps (not vulnerabilities to "fix" in this scaffold)

See `docs/limitations.md`: approver names are not verified identity,
there is no audit log, redaction is pattern-based, and gate confidence
is caller-supplied. A production adoption must close those first
(`docs/implementation-guide.md`).

## Reporting

If you find a security issue in this scaffold, please report it via the
repository's private vulnerability reporting (once pushed) rather than
opening a public issue. Do not include real personal data in any report.
There are no credentials, secrets, or live endpoints in this repo to
rotate — if you find something that looks like one, it is synthetic
test data; report it anyway so it can be checked.
