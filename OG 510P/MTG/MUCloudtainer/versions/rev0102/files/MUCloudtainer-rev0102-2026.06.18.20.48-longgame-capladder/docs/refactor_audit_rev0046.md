# rev0046 refactor and audit notes

rev0046 adds:

```text
src/muc5/action_yield_screen.py
scripts/run_rev0046_yield_match_queue.py
tests/test_rev0046_yield_screen.py
```

The new module intentionally keeps three concerns separate:

```text
historical yield-row aggregation
public yield-screen model training/selection
matched hard/margin/yield queue comparison
```

The matched comparison reuses the existing online branch-racing and C++ transition shadow machinery instead of introducing a separate rollout path.

## Audit target

The cube audit now checks that:

```text
rev0046 summary/model/method files exist
all three methods are present
branch truncations are zero
C++ skipped transitions are zero
C++ mismatches are zero
yield screen selected 10 situations
yield method has at least one decisive label
```

No gameplay policy is promoted in rev0046.
