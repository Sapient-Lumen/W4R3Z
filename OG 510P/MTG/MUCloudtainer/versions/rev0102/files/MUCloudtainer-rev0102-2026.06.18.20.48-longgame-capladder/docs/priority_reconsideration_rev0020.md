# rev0020 priority reconsideration

## What changed

The highest-priority C++ coverage debt from rev0019 is closed: Jace ultimate is now C++-checkable through explicit shuffle transport.

That changes the next priority from "finish this obvious C++ hole" to "decide which C++ seam should become authoritative first."

## Current priority order

1. **C++ transition-batch runner over recorded traces**
   - We can already check traces. The next step is to run batches of transported transitions faster and measure overhead.

2. **C++ state-transition microcases for any remaining rare legality branches**
   - The trace checker found no unsupported events in rev0020, but directed cases should keep growing.

3. **Action-ranker imitation seed**
   - Now started. Next step is to turn the logistic smoke model into a public agent wrapper, but only for evaluation against baselines, not promotion yet.

4. **Sequential racing over MAP-Elites candidates with statistical gates**
   - Candidate pruning matters once evaluations get bigger.

5. **Meta-rank / Alpha-Rank-style population analysis over denser tables**
   - Useful after payoff tables have more reps and fewer smoke artifacts.

6. **Full C++ rollout core**
   - Still delayed. Fast wrong rollouts would poison every learning method.

## Why not jump to full C++ now?

C++ is valuable where the seam is stable. The current Python engine still carries the clearer hidden-information boundary, replay machinery, promotion gates, and debug ergonomics. The long-haul plan remains:

```text
Python proves semantics
C++ mirrors a seam
C++ passes directed + sampled + trace checks
only then consider using that seam for bulk evaluation
```

## Next recommended build

The next best revision should either:

```text
A. turn the action-ranker smoke model into a frozen public policy and evaluate it through promotion/stat gates
```

or

```text
B. add a C++ batch-transition benchmark that consumes rev0020 trace records and measures real bridge overhead
```

My leaning is B first, then A.
