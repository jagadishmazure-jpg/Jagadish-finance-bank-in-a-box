# Limitations and known failures (kept visible)

These are not buried. Each one is a real gap in this scaffold, and the
ones that can be tested are tested as behaviour, not wished away.

1. **Rule engines, not models.** Agents compute from fixed rules, so
   they cannot read free-text evidence, weigh nuance, or surprise you
   — in either direction. Any claim about "agent judgement" here means
   rule output, nothing more.
2. **Tiny synthetic data.** Two customers, three positions, three
   transactions. Concentration and gain maths are correct on this
   data and unproven on anything larger; the row-cap test uses a
   separate 150-row table precisely because the seed never exercises
   the cap on its own.
3. **In-memory SQLite only.** No persistence, no concurrency story,
   no migration path. Two orchestrators sharing one connection would
   share assignment state in confusing ways (each `Orchestrator`
   instance owns its own assignment map; that is a scaffold seam, not
   a feature).
4. **Gate confidence is caller-supplied.** `evaluate_consent` checks
   the number it is given; it cannot tell whether that number was
   honestly measured. A caller passing 0.9 for a mumbled "yes" defeats
   the low-confidence check. This is a known trust boundary, recorded
   here rather than papered over.
5. **Redaction is pattern-based.** Formatted card numbers, standard
   emails, phones, and SSN shapes are caught; unusual layouts, account
   numbers without separators, and names themselves are not. The
   `contains_pii` helper is a regression check, not a guarantee.
6. **Brand check is a tripwire, not a legal review.** It hashes 1–4
   word n-grams against a short digest list. New real names, near
   spellings, and names inside images are out of scope.
7. **No authentication or audit log.** Approver names are strings,
   not verified identities, and finalisations are not written to an
   append-only log. A production version needs both before any memo
   carries weight.
8. **Email "send" is a stub.** Even opted-in with a transport, this
   scaffold sends through whatever the adopter injects — nothing here
   verifies delivery, and nothing here should be mistaken for a
   notification system.
