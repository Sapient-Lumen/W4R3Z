# rev0029 no-choice segment audit

rev0029 adds a small measurement layer for a future C++ batching target.

A **forced frame** is a `DecisionFrame` with exactly one legal action. A **pass-only frame** is a forced frame whose sole legal action is `PASS`.

This does not yet make C++ authoritative. It asks a simpler question:

```text
How many current public-game decisions are really choices,
and how many are forced ceremonial steps?
```

## Smoke measurement

The rev0029 audit ran 24 public games and found:

```text
decisions:                    4,022
choice frames:                 1,401
forced frames:                 2,597
forced runs:                     773
max forced run:                   23
mean forced run:                3.36
pass-only frame rate:           ~0.645
estimated compression ratio:    ~1.85x
truncations:                       0
```

Interpretation: a future no-choice segment kernel could reduce Python loop overhead by grouping forced runs, but it must preserve the current hidden-information and replay contracts.

## Why this is not a C++ rollout yet

A forced frame can still have semantic content: stack resolution, pending choices, combat cleanup, state-based loss, or turn advancement. So the next C++ target should be:

```text
record no-choice segment
apply segment in C++ under explicit pre/post SIGv2 checkpoints
compare to Python
only then batch live rollouts
```

The audit is a map of likely speedup, not permission to skip semantic tests.
