# Rematch worlds should publish positive-service commitment semantics as a world contract

The current geometric-arrival passes already show that a positive-service promise can mean at least three materially different institutions:

- **blind commit** to a timeout budget,
- **live reoptimization** that accepts local drift,
- or **stateful control** that carries explicit slack accounting.

These should not be treated as interchangeable implementation details.
The time-consistency law already says that finite promises survive live reoptimization without drift only when the minimum blind-commit timeout is one tick.
So two worlds can advertise the same target margin and nominal deadline while implementing different institutions.

Recent external work sharpens why this belongs in the world contract rather than in hidden controller code.
Voluntary-commitment negotiation changes outcomes precisely because commitment mode is explicit and enforceable (`RS-GR-040`).
For Concord, the same lesson applies in smaller form: a writer must say whether a service promise is merely proposed, blindly committed, or recomputed at each checkpoint.

## Minimum contract

When a rematch world exposes positive-service promises, publish at least:

1. the **commitment mode** (`blind_commit`, `live_reoptimization_accepts_drift`, or richer stateful/slack-tracking control),
2. the **checkpoint rule** (when reoptimization is allowed),
3. the **preserved quantity** (same-horizon value, original margin floor, or a weaker live approximation),
4. and the **repair rule** if deadline inflation or slack state is used to restore a blind-commit promise.

## Implementor consequence

Do not compare promise ladders across worlds unless these four fields match.
If they do not match, treat the difference as an institutional/world-contract change rather than as a mere policy-quality comparison.
