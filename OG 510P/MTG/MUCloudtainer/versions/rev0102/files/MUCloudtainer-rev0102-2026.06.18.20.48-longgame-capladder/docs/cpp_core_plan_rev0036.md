# C++ core plan after rev0036

The C++ doctrine is unchanged:

```text
Python = semantic reference, hidden-information boundary, replay/gates, analytics
C++    = stable hot kernels, segment/batch acceleration, future rollout core after parity proof
```

rev0036 does not add a new C++ kernel.  Instead, it pushes the new adaptive action-counterfactual traffic through the existing C++ shadow transition checker.

Results:

```text
branch-label transitions checked: 13,135
payoff-shadow transitions:        18,599
skipped C++ events:                    0
C++ mismatches:                        0
```

The next C++ target should not be a full game engine.  It should be either:

1. no-choice segment execution benchmark under Python pre/post SIGv2 gates, or
2. a batched branch-rollout helper for the adaptive labeler, still using Python to decide observations, legality, RNG transport, and final audit.

C++ should continue to earn authority one differential-tested seam at a time.
