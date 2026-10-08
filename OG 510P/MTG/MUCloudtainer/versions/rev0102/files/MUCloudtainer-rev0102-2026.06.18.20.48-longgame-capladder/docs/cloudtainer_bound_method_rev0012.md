# rev0012 cloudtainer-bound method note

This archive is meant to be opened by future sandpeople inside similar cloudtainers. The method should therefore stay modest, portable, and inspectable.

## Office constraints

```text
Python-first
CPU-first
small memory budget
no assumption of GPU
no assumption of internet inside execution runtime
no heavy new dependency unless the archive records why
```

The rev0009 tool audit found useful scientific Python tools in this cloudtainer, including NumPy, pandas, SciPy, PyTorch CPU, JAX, Numba, Cython, XGBoost, and LightGBM. That does not mean we should use all of them. The current best path is structural Python optimization first:

```text
DecisionFrame avoids duplicate legal-action recomputation
record_log=False for rollouts
public agents avoid omniscient state
payoff rows carry provenance
fuzz/replay before learning
```

## Why limited resources are useful

The limited office forces experiments to be:

```text
small enough to replay
small enough to inspect
small enough to compare by exhaustive or semi-exhaustive methods
small enough that weird failures can be understood
```

That constraint is not merely a handicap. It is why MUC-5 is interesting: a five-card Magic universe can be more scientifically useful here than a larger but opaque game.
