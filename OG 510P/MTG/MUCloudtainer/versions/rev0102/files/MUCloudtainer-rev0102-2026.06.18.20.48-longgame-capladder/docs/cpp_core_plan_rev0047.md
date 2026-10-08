# rev0047 C++ Core Plan

No new C++ kernel was added in rev0047.

The new yield-screened branch traffic and payoff traffic were routed through the existing C++ transition shadow path:

```text
branch collection C++ transitions: 24,673 checked, 0 skipped, 0 mismatches
payoff C++ transitions:            41,437 checked, 0 skipped, 0 mismatches
```

The doctrine remains:

```text
Python = semantic reference, hidden-information boundary, replay/gates, analytics
C++    = stable hot kernels, segment/batch acceleration, future rollout core after parity proof
```

The next C++ work should be driven by a measured bottleneck. At this point, label quality and truncation behavior still look more important than adding another kernel.

