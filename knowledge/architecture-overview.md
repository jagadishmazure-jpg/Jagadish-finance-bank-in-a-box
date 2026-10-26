# Knowledge — architecture overview

```mermaid
flowchart TD
    U[Human reviewer] --> O[Orchestrator]
    O --> I[Investment agent<br/>tools: v_positions]
    O --> R[Risk agent<br/>tools: v_positions, v_transactions]
    O --> C[Compliance agent<br/>tools: v_transactions, v_customers]
    I --> A[SQLite authorizer<br/>views only, writes denied]
    R --> A
    C --> A
    A --> V[(Views: v_positions<br/>v_customers, v_transactions)]
    V --> B[(Base tables<br/>never directly readable)]
    I --> M[Decision memo<br/>DRAFT]
    R --> M
    C --> M
    M --> G[Confirmation gate<br/>+ named approval]
    G --> F[FINAL memo]
```

## Why this shape

- One orchestrator, three lenses: the division mirrors the decision,
  not the org chart. Each agent owns exactly one question.
- Views as the contract: an agent's tools list names views, and the
  authorizer enforces the list at the database boundary.
- Memo as the only shared artefact: agents never message each other
  directly, so a failure in one cannot corrupt another's output — the
  orchestrator is the only writer, and it records failures verbatim.
