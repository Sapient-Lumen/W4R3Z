# rev0018 priority reconsideration

The priority order changed after the coverage probe.

Before rev0018, the planned next C++ work was broadly:

```text
stack resolution
choice transitions
more edge cases
```

The coverage probe showed that Jace Brainstorm activation was the most obvious missing live transition. So rev0018 added:

```text
ACTIVATE_JACE plus2
ACTIVATE_JACE zero
ordered-library transition signatures
choice transitions
stack pass/resolution
```

## Current priority order

```text
1. Build a C++ batch transition harness over recorded DecisionFrame traces.
2. Add deterministic C++ replay-check helpers for whole short traces, not only one-action rows.
3. Keep Jace ultimate out of C++ until RNG/shuffle transport is explicit.
4. Start a tiny action-feature imitation/ranker only after C++ trace checks stay green.
5. Delay full C++ tournament core until hidden-information DecisionFrame emission has an equivalent audit boundary.
```

## Why not full C++ next?

Because the engine is not just state mutation. It is also:

```text
hidden information
legal-action menus
public observations
mulligan agency
reward/truncation labels
replay determinism
promotion/statistical gates
```

C++ should accelerate the stable core, not silently bypass the safety shell.
