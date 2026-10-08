# rev0021 priority reconsideration

Previous priority:

```text
C++ batch-transition benchmark over recorded traces
  -> freeze/evaluate an action-ranker public policy wrapper
```

rev0021 completes both as smoke-grade infrastructure.

## New priority order

1. **C++ batch rollout prototype over replayable public traces.**
   The batch checker proves that C++ can process recorded transitions in bulk.  The next step is to explore whether a C++ loop can consume a compact state record for many games without giving up Python replay checks.

2. **Sequential racing with ranker/code/public populations.**
   Now that ranker policies can enter public payoff tables, use sequential racing to avoid spending full budgets on obviously weak candidates.

3. **MAP-Elites + ranker policy cells.**
   Evaluate whether the ranker is useful only with certain deck descriptors: high land count, Force-heavy, Jace-only, Overlord pressure, 20-life versus 40-life.

4. **Neural/listwise policy only after the frozen linear ranker survives gates.**
   A tiny MLP or gradient-boosted ranker is appealing, but it should use the same public features and promotion/replay/statistical gates.

5. **Full C++ rollout core remains later.**
   The C++ path is promising, but authority must be earned by parity tests, not assumed.
