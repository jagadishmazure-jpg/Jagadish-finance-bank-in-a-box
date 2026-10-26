# Interview points

- **"Why three agents instead of one with three prompts?"** Because
  the failure modes differ: a single voice can blend enthusiasm into
  caution without leaving a trace. Separate findings force each lens
  to commit to a stance, which makes disagreement — and the veto —
  observable and testable.
- **"Why does the authorizer check the view name, not just the table
  name?"** A view and its base table are different doors to the same
  rows. Checking only the table would either block legitimate view
  reads or allow direct base-table reads; the source argument is what
  distinguishes them, and the tests prove both directions.
- **"What breaks first at real scale?"** The gate confidence number:
  it is caller-supplied, so a careless caller defeats the
  low-confidence check. That is named in `docs/limitations.md` on
  purpose — ask me how I would fix it (measured confidence from the
  consent channel, plus re-prompting, never a hardcoded 0.9).
- **"Why is dissent a section, not a log line?"** Because the human
  reviewer is the audience. A log line is for machines; a dissent
  section is a reviewer reading "the investment case was strong and
  we still said no, because compliance blocked it" in the memo itself.
- **"Why no live model?"** Reproducibility. Every test in this repo
  is exact because the agents are rules. A model belongs behind the
  same schema — that is the planned step, and it comes with its own
  eval burden rather than free-text hope.
- **"What would you not claim from 53 tests?"** Quality, coverage of
  real-world finance, or production readiness. It is a regression
  suite over deterministic code and enforcement boundaries — honest
  proof of the boundaries, not of the business.
