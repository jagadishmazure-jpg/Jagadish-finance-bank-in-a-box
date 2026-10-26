# How it works, step by step

1. **Build the store.** `build_database()` creates base tables, seeds
   synthetic rows, creates the three masked views, and only then
   installs the authorizer. Setup writes are never confused with agent
   reads.
2. **Divide.** The orchestrator plans three tasks — one per specialist
   — and delegates each, recording the assignment.
3. **Run each agent through its views.** The investment agent reads
   positions; the risk agent reads positions and transactions; the
   compliance agent reads transactions and the masked customer view.
   Any direct base-table read raises at the database boundary.
4. **Contain failures.** If an agent throws, the orchestrator records
   `(agent, reason)` in the memo's failure list, keeps the surviving
   findings, and stamps the memo partial. Nothing is silently dropped.
5. **Resolve.** Stances are combined by the precedence rule
   (BLOCK → REJECT → CONDITIONAL → APPROVE). Dissenting findings are
   kept in their own memo section.
6. **Checkpoint.** The memo is DRAFT. Finalisation needs an evaluated
   gate (unambiguous, confident "yes") and a named, single-use, scoped,
   unexpired approval consumed for exactly this memo.
7. **Notify (or not).** The email channel dry-runs by default. A real
   send needs explicit opt-in, a non-CI environment, and an injected
   transport — this scaffold ships none.
