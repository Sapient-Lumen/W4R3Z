# C++ core plan through rev0028

The long-haul direction remains:

```text
Python = semantic reference, hidden-information boundary, replay/gates, analytics
C++    = stable hot kernels and eventual high-throughput core after differential proof
```

rev0028 does not add a new C++ kernel.  It routes the new counterfactual mulligan branch traffic through the existing transition microkernel and batched C++ signature checker.

## C++ result this revision

```text
counterfactual branch games: 144
C++ transition events:       36,342
supported events:            36,342
skipped events:              0
mismatches:                  0
```

That is valuable because counterfactual branch games start from explicit pregame states rather than the normal `start_game(...)` path.  C++ parity still holds over the resulting gameplay transitions.

## Completed C++ seams

```text
rev0015: deck probability probe kernel
rev0016: legal-menu differential harness
rev0017: transition microkernel initial cases
rev0018: stack/choice transition expansion
rev0019: recorded-trace checker
rev0020: Jace ultimate explicit shuffle transport
rev0021: batched trace checker
rev0026: live shadow rollout seam
rev0028: explicit-pregame counterfactual traffic checked through C++ transition parity
```

## Next C++ target

The next useful C++ target is still **no-choice segment batching**.

A no-choice segment is the deterministic run between public DecisionFrames.  Python can keep responsibility for hidden-information observations, agent calls, replay, reward gates, and analytics, while C++ accelerates deterministic transition segments after parity checks are established.
