# rev0015 priority reconsideration

The user clarified that C++ should be part of the long-haul core engine when valuable. rev0015 changes the priority stack accordingly.

## New architecture stance

```text
Python = research shell, reference semantics, agents, analytics, docs
C++    = stable hot kernels and eventually the high-throughput referee core
```

The bridge must stay cloudtainer-bound. No external build system is assumed. A future opener should be able to unzip, run tests, compile local C++ with `g++`, and fall back to Python if needed.

## Current best next build

The next high-value implementation is probably not full C++ state transition yet. It is a **differential legal-menu harness**:

```text
Python state → legal DecisionFrame menu
C++ candidate menu → compare canonical action strings
```

That gives us a safe route toward C++ legal-action enumeration.

## After that

```text
C++ compact rollout state
Python wrapper for public agents
replay-compatible C++ transition traces
sequential racing for constructor candidates
Alpha-Rank/meta-rank over promoted payoff tables
tiny imitation model over action features
```

## Standing warning

The project should not trade trust for speed. A faster simulator that leaks hidden state or mishandles truncation is worse than a slower one. rev0015 therefore adds both a C++ benchmark and a stall adversary in the same revision.
