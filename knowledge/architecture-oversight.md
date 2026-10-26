# Knowledge — human oversight architecture

```mermaid
flowchart TD
    MEMO[DRAFT memo] --> GATE[Confirmation gate<br/>consent recorded?<br/>unambiguous yes?<br/>confidence >= 0.6?]
    GATE -->|any check fails| STAY[Stays DRAFT]
    GATE -->|passes| APP[Named approval<br/>single-use, scoped<br/>to this memo, expiring]
    APP -->|missing / reused / expired / wrong scope| STAY
    APP -->|consumed| FINAL[FINAL memo]
    FINAL --> MAIL[Email channel<br/>dry run by default<br/>opt-in + non-CI only]
```

## Why two checkpoints instead of one

The gate answers "did a human actually say yes, clearly, just now?"
The approval answers "who said it, for this exact memo, and is it
still valid?" A gate without an approval is anonymous; an approval
without a gate could be a stale signature waved at a new memo. Both
must pass, in that order, and the approval is consumed — one approval,
one finalisation, ever.
