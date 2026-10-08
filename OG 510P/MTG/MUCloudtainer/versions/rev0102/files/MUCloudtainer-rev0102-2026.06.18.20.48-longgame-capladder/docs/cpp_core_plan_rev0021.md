# C++ core plan as of rev0021

The long-haul target is a high-throughput C++ core, but the migration is deliberately incremental.

## Current rule

```text
No C++ authority without Python differential/replay evidence.
```

## Stable seams so far

- Numeric deck probes.
- Legal-menu enumeration mirror.
- One-action transition microkernel.
- Stack/choice/Jace-ultimate transition checking.
- Recorded public-trace checking.
- Batched C++ transition execution over prepared trace records.

## Next C++ work

1. Reduce transition-record projection overhead in Python.
2. Explore compact binary or line-batched state/action transport.
3. Prototype batch rollout using a tiny subset of agents only after every action remains replay-checkable.
4. Keep C++ subprocess calls coarse-grained; one process per action is a trap.

## Non-goal

Do not rewrite the full simulator in C++ before the semantics stop moving.  Right now, the Python referee is still the lab notebook and oracle.
