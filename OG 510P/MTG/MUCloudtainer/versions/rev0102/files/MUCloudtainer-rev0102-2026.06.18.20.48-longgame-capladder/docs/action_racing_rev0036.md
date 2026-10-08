# action_racing.py

`src/muc5/action_racing.py` contains the adaptive branch allocator for gameplay action counterfactuals.

The allocation heuristic is intentionally simple:

```text
1. Run a base rollout for each selected action.
2. Sort actions by empirical actor score.
3. Identify current best and second-best.
4. If their gap is large enough, stop early.
5. Otherwise allocate another rollout to the less-sampled top contender.
6. Repeat until confidence or budget stops the race.
```

The design goal is transparency, not optimal multi-armed-bandit theory.  The emitted rows contain enough metadata to audit where branch budget went.
