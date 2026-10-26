# Purpose and who it is for

This repo is a portfolio demonstration of a multi-agent "bank in a
box": collaborating agents that produce a comprehensive financial
decision memo for a fictional firm, Merrowgate Financial, from
synthetic data.

It is for:

- **Recruiters and hiring managers** reading the portfolio: the memo,
  the veto rule, and the failure handling are the point — read
  `docs/how-it-works.md`, then the proof tests named in the README.
- **Engineers adopting the pattern:** `docs/implementation-guide.md`
  explains how to lift the orchestrator, authorizer, and gate into a
  real system (with a real model and a real database) without lifting
  the demo's shortcuts.
- **Interviewers:** `docs/interview-points.md` lists the decisions
  worth probing, including the ones this scaffold gets wrong on purpose
  (see `docs/limitations.md`).

It is **not** for real financial decisions. Every number is invented,
every agent is a deterministic rule engine, and no memo here is advice
for any real person. The fictional firm name was checked against public
search results before use; a suggested name that turned out to sit
close to a real advisory practice was discarded in favour of
Merrowgate Financial.
