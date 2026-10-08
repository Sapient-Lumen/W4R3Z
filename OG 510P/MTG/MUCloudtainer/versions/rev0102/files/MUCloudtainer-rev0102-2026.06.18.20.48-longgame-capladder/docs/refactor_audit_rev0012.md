# rev0012 refactor/audit notes

## Refactor performed

Added a hidden-information-safe public-agent factory:

```text
src/muc5/public_agents.py
```

The new public agents use only DecisionFrame observation + legal actions. This isolates payoff/promotion experiments from trusted-state debugging agents.

Added promotion gate utilities:

```text
src/muc5/promotion.py
```

The gate audits payoff-row provenance, reward convention, truncation rate, and replay samples.

Added oracle seeding utilities:

```text
src/muc5/oracle_seed.py
```

The oracle seed is a small candidate generator for future response-oracle work.

## Audit added

The cube audit now checks rev0012 public payoff rows, promotion-gate summary, replay-sample pass count, oracle candidate count, oracle game count, required new files, and live public-agent smoke behavior.

## Known debt

```text
Public scoring duplicates some heuristic scoring logic.
Promotion gate is provenance-focused, not statistically rigorous.
Oracle candidate prior is static and hand-shaped.
No Alpha-Rank adapter yet.
No action-feature encoder for neural policies yet.
```
