# C++ core plan through rev0038

The doctrine remains unchanged:

```text
Python = semantic reference, hidden-information boundary, replay/gates, analytics
C++    = stable hot kernels, batched/segment acceleration, future rollout core only after parity proof
```

rev0038 did not add a new C++ kernel.  Instead, it pushed a new branch-label workload and a new public payoff workload through existing C++ parity gates:

```text
disagreement branch collection: 23,401 checked transitions, 0 mismatches
ranker payoff shadow:           40,141 checked transitions, 0 mismatches
```

That matters because new policy traffic often exposes transition bugs that old traffic never touched.  The correct long-haul path is not "rewrite the simulator in C++".  It is:

```text
1. keep Python authoritative
2. build C++ seams for stable hot paths
3. differential-check every seam against Python state signatures
4. only then let C++ handle larger live chunks
```

Next C++ priority remains no-choice segment execution under pre/post `SIGv2` gates.  Action-counterfactual branch collection is becoming expensive enough that segment acceleration may become valuable soon, but it must stay shadowed until parity is routine.
