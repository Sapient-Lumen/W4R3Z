# Priority reconsideration — rev0026

Previous priority was:

```text
C++ batch rollout sketch under Python fingerprint gates
```

rev0026 implements that as a shadow rollout seam rather than a premature C++ tournament engine.  That was the right compromise: it gives us bulk-game C++ parity checks while keeping Python as the semantic authority.

## Updated priority order

1. **Outcome-based mulligan improvement.** The current mulligan ranker is pseudo-oracle seeded. It needs terminal-outcome data, but should be improved carefully because mulligans affect every later policy result.
2. **Larger MAP-Elites races with shadow C++ gate attached.** Static archive cells should be evaluated under real public games and C++ parity checks.
3. **Meta-rank over denser nontruncated tables.** rev0017's meta-rank adapter needs cleaner, larger payoff tables.
4. **C++ no-choice segment batching.** Identify stretches where the next transition is deterministic after a legal action and prototype batched application without handing C++ hidden-information authority.
5. **Counterfactual/search targets.** Outcome-weighted cloning cannot value unchosen alternatives; the next learning target should use search, rollouts, or controlled response oracles.

## Pushback

The C++ path is important, but full C++ authority is still premature.  The most useful C++ work is not more code volume; it is better cutover evidence.
