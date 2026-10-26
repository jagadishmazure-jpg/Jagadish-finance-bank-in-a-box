# How to run (offline first)

Requirements: Python 3.11+ and `pytest`. No third-party packages, no
network, no credentials, no virtualenv inside the repo.

```bash
# Demo memo (stays DRAFT)
python3 -m bank_in_a_box.demo

# Demo memo, finalised by a named approver
python3 -m bank_in_a_box.demo --finalise --approver "Ada Reviewer"

# Full test suite
python3 -m pytest tests/ -q

# 8-word overlap check against a source text file (source never committed)
python3 scripts/check_overlap.py /path/to/source.txt
```

Optional cloud / live-model use is **not** part of this scaffold: there
is no deployment target, no hosted endpoint, and no model provider
wiring. Adding a model means replacing the rule engines in
`bank_in_a_box/agents.py` behind the same Finding schema — see
`docs/implementation-guide.md` and the Planned table in
`docs/built-vs-planned.md`.
