# rev0010 simulator performance

rev0010 keeps the same performance thesis as rev0009: stay cloudtainer-bound and optimize Python structure first.

## Current profile

```text
trusted fast path decisions/sec: 75307.68
trusted validated decisions/sec: 62399.10
public DecisionFrame decisions/sec: 59047.86
```

The public DecisionFrame path is slower than handing omniscient `GameState` to a scripted agent, but it blocks the more dangerous hidden-information leak. That is the right tradeoff for learned/search/evolutionary agents.

## Optimization target order

1. Keep `record_log=False` for rollouts.
2. Keep action application indexed from a fresh DecisionFrame to avoid duplicate legality enumeration.
3. Reduce repeated observation dictionary construction.
4. Consider compact typed feature/action encodings for batch rollouts.
5. Only after profiling stabilizes, consider Numba/Cython-style acceleration available in the cloudtainer.

The office remains cloudtainer-bound: future sandpeople should assume Python-first, CPU-only, modest-memory work unless a fresh office audit proves otherwise.
