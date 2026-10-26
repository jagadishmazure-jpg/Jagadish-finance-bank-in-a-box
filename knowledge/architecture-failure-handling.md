# Knowledge — failure handling architecture

```mermaid
flowchart TD
    O[Orchestrator] --> D{Delegate task}
    D -->|already assigned elsewhere| CF[Delegation conflict<br/>recorded + raised]
    D -->|first assignment| RUN[Run agent]
    RUN -->|repeat beyond max| LOOP[Loop detected<br/>agent quarantined]
    RUN -->|exception| CONTAIN[Contain: record failure<br/>keep other findings]
    RUN -->|success| FIND[Finding]
    FIND --> RES[Resolve: veto rule]
    CONTAIN --> RES
    RES --> MEMO[Memo: partial if any failure<br/>dissent + failures visible]
    MEMO --> H{Gate + approval?}
    H -->|no| DRAFT[Stays DRAFT]
    H -->|yes| FINAL[FINAL]
```

## The three failure modes, and what "handled" means here

1. **Loop** — same agent, same task, too many runs. Handled means
   stopped and named, not retried forever.
2. **Delegation conflict** — same task, two owners. Handled means the
   second assignment is refused and the clash is written into the
   memo's conflict list, not resolved by last-writer-wins.
3. **Cascade** — one agent throws. Handled means the memo still forms
   from the survivors, is stamped partial, and carries the failure
   reason in its own section. "Handled" never means "hidden".
