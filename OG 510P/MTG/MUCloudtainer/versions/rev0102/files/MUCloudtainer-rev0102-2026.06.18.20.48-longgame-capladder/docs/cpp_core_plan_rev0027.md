# C++ core plan through rev0027

The long-haul direction remains:

```text
Python = semantic reference, hidden-information boundary, replay/gates, analytics
C++    = stable hot kernels and eventual high-throughput core after differential proof
```

rev0027 does not add a new C++ kernel.  Instead, the new outcome-mulligan traffic is routed through the existing replay and batched C++ trace checker:

```text
8 replay traces
2,112 C++-checked transition events
0 skipped events
0 mismatches
```

That is the right cutover discipline.  The C++ layer should not become authoritative merely because it is faster.  It earns authority by matching Python fingerprints on representative public traffic.

## Current C++ seams

```text
rev0015: deck probability probe kernel
rev0016: legal-menu differential harness
rev0017: transition microkernel initial cases
rev0018: stack/choice transition expansion
rev0019: recorded-trace checker
rev0020: Jace ultimate explicit shuffle transport
rev0021: batched trace checker
rev0026: live shadow rollout seam
rev0027: new learned-mulligan traffic checked through existing C++ trace gate
```

## Next C++ target

The next C++ target should still be **no-choice segment batching**, not a full tournament core.

A no-choice segment is the run of deterministic engine transitions between two public DecisionFrames.  Batching those segments may accelerate rollouts while keeping Python responsible for observations, agent calls, reward gates, replay, and hidden-information boundaries.
