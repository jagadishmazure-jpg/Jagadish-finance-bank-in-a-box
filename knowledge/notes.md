# Knowledge notes — distilled patterns (own words)

These notes distil the *patterns* behind a multi-agent finance design:
what each pattern is for, where it breaks, and how this scaffold answers
it. They paraphrase ideas; they quote nothing and name no source
programme. All examples use the fictional firm Merrowgate Financial and
synthetic data.

## Pattern 1 — Split the judgement, don't just split the work

A single agent asked to "decide" will blend return-chasing, risk worry,
and rule-checking into one mushy paragraph. Splitting the judgement
across three lenses — return, risk, rules — forces each concern to state
its own stance in the open. The memo is then an assembly of stances,
not a single voice pretending to be unanimous.

Failure mode this answers: enthusiasm swamping caution. The scaffold's
answer is a precedence rule, not a vibe: a rules BLOCK caps the outcome
at REJECT (see `docs/architecture.md`).

## Pattern 2 — Ground every claim in a view, not in the raw tables

Agents that can read anything will eventually read something they
shouldn't — a contact field, a full customer record — and paste it into
an output. The fix has two layers: views that expose only what the
agent needs, and an authorizer that denies everything else at the
database boundary, including direct base-table reads.

Failure mode this answers: quiet over-collection. The scaffold proves
the boundary with denial tests, not with a policy paragraph.

## Pattern 3 — A failed agent is evidence, not an absence

When one specialist fails, the tempting move is to build the memo from
the survivors and say nothing. That produces a confident-looking memo
resting on partial evidence. The honest move is a memo that says, in
its own text, which agent failed, why, and that it is partial.

Failure mode this answers: cascading silence. The scaffold contains
each failure, keeps the surviving findings, and stamps the memo
partial.

## Pattern 4 — Dissent is part of the record

If the final recommendation is REJECT because rules blocked it, the
investment case for APPROVE does not stop being true as analysis — it
stops being the decision. Deleting it would hide a real disagreement a
human reviewer deserves to see. So dissent gets its own memo section.

## Pattern 5 — Humans approve the decision, not the draft

A memo that agents can mark final is a memo nobody owns. Finalisation
needs two separate human facts: a named, single-use, scoped, expiring
approval, and a confirmation gate that passed on an unambiguous,
confident "yes". Either one missing means DRAFT, full stop.

## Pattern 6 — Synthetic data must still obey the privacy rules

"Just fake data" is how real-looking contact details end up in demos,
screenshots, and test fixtures. This scaffold redacts card numbers,
emails, phones, and SSN-shaped strings even though every row is
invented, and seeds contact fields only in the base tables the agents
can never read.

## What this scaffold deliberately does not do

- No live model calls: agents are deterministic rules, so runs are
  reproducible and tests are exact. Swapping in a model is a planned
  step (see `docs/built-vs-planned.md`), not a hidden one.
- No real advice: memos are portfolio-construction exercises over
  invented numbers, not recommendations for any real person.
- No deployment, no hosted service, no package release. It runs
  offline on a laptop with the standard library.
