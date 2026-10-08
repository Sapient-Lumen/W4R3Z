# rev0048 refactor audit

## New code

```text
src/muc5/truncation_rescue.py
scripts/run_rev0048_truncation_rescue.py
tests/test_rev0048_truncation_rescue.py
```

`truncation_rescue.py` separates truncation accounting from payoff generation. It provides:

```text
annotate_rescued_rows(...)
summarize_rescue(...)
truncation_by_strategy(...)
truncation_by_pair(...)
```

## Why this refactor belongs in core code

Truncation handling is a fairness concern, not merely a CSV cleanup step. If it lives only inside one script, future policy panels can accidentally return to draw-half-heavy comparisons. A core helper makes the intended protocol reusable.

## Audit checks

The cube audit now verifies:

```text
rev0048 game rows = 144
rev0047 baseline truncations = 30
rev0048 final truncations = 0
all baseline truncations resolved
promotion and statistical gates passed
C++ shadow and replay-trace checks have zero skipped events and zero mismatches
required rev0048 docs/scripts/tests/data exist
```
