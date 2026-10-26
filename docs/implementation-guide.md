# Implementation guide (for adopters)

## Lift these as-is

- **Authorizer pattern.** Install the authorizer after schema setup,
  and keep the rule "a read is allowed only if its source names an
  allowed view". Port it to any database by replacing the SQLite
  callback with the equivalent row/view permission layer — but keep
  the denial tests, ported too.
- **Memo shape.** DRAFT by default, dissent and failures as sections,
  finalisation as a separate, approval-consuming step. If your memo
  format drops either section, you have dropped the feature.
- **Gate + approval split.** Keep the two checkpoints separate: the
  gate checks the consent record, the approval checks the person,
  scope, and expiry. Merging them into one boolean is how stale
  approvals finalise new memos.

## Replace deliberately

- **Rule engines → models.** Keep the Finding schema and the tool
  lists; put the model behind `Agent.run`. Then add what this
  scaffold cannot test: output-schema validation with repair-then-
  escalate, prompt-injection tests, and an eval set with human labels.
  Do not keep the rule engines as a "fallback" that silently answers
  when the model fails — that reintroduces silent evidence.
- **In-memory SQLite → real store.** Views become real database
  views or an API layer with the same least-privilege shape. Re-run
  the denial tests against the real boundary; a test that only passed
  on SQLite proves nothing about Postgres permissions.
- **Name strings → identity.** Approvals must bind to a verified
  identity (SSO subject, not a typed name) and finalisations must land
  in an append-only audit log before the memo flips to FINAL.

## Do not do

- Do not `LIMIT`-rewrite agent SQL to enforce row caps; cap at fetch
  time, as here, so the executed query stays auditable.
- Do not clamp negative costs to zero; reject them, as here, so a
  broken estimate is visible.
- Do not email from defaults. Keep dry-run the default in every
  environment except an explicitly configured production one, and keep
  the CI refusal.
