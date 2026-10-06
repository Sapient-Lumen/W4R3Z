# Runtime dreambank 032 — BrowserRT as overload-governance kernel

Current revision: rev0055

BrowserRT's ambitious endgame is not merely to schedule tasks. It should eventually govern work under pressure:

- admit or reject work by priority, size, and provider health;
- shed or degrade before queues explode;
- isolate failure domains with bulkheads;
- open circuits when a provider is unhealthy;
- spend retry credits deliberately;
- make critical bypass explicit and traced;
- prove rejected work did not mutate providers;
- replay histories to understand why a gate said no.

The one-to-rule-them-all dream is a browser userspace kernel where every expensive lane has this governance vocabulary:

```txt
lane provider -> admission -> scheduler -> resilience gate -> retry budget -> persistence/mutation -> trace -> model oracle
```

Rev0037 earns only a small rung: `StorageLaneOverloadGovernanceModelOracle` observes composed fake-provider storage histories and checks model-level invariants. It is intentionally not adaptive, not wall-clock, not OPFS, not browser Worker, and not a production algorithm.

## Required future discipline

Any future overload-governance claim must say:

1. which gate made the decision;
2. whether provider mutation happened;
3. which leases were acquired and released;
4. which trace events prove the decision;
5. whether the proof was fake-provider, browser, OPFS, generated-history, or production-like;
6. which non-claims remain.
