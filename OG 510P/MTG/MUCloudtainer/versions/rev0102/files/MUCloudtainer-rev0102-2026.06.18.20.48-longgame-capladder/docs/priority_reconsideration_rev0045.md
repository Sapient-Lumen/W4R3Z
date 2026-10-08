# rev0045 priority reconsideration

The current bottleneck is still label quality, not model class and not raw simulator speed.

The rev0045 matched audit says the rev0044 margin screen is not yet a clear improvement over the older hard-frame queue. The next useful target is therefore not a new gameplay policy. It is a better label-yield objective.

## Current priority order

```text
1. Train/evaluate a label-yield screen: decisive labels per rollout, not raw margin.
2. Keep matched queue audits beside every new selector.
3. Continue online adaptive branch allocation for selected frames.
4. Attach C++ transition shadow checks to branch-heavy collectors.
5. Promote gameplay policies only after nontruncated payoff tables and replay/C++ gates stay clean.
```

## C++ posture

No new C++ kernel was added in rev0045. The right long-haul posture remains:

```text
Python = semantic reference, hidden-information boundary, replay/gates, analytics
C++    = stable hot kernels and batch/segment acceleration only after differential parity proof
```

The rev0045 branch traffic still went through the existing C++ transition shadow checker cleanly.
