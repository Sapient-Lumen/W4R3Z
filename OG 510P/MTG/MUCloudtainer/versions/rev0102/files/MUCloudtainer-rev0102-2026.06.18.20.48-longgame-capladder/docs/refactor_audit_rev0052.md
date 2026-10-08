# rev0052 refactor/audit note

New module:

```text
src/muc5/terminal_matchup.py
```

It separates target/life matchup logic from the previous broad deep-claim module:

```text
terminal_deep.py
  broad claim-ledger target selection and field-focused deep reps

terminal_matchup.py
  target/opponent life-split agenda selection, focused specs, target-perspective rows, and life-flip gate
```

This prevents future matchup/life audits from copying script-local aggregation logic.

New audit checks verify:

```text
rev0052 game count and zero truncations
promotion/statistical/life-flip gates pass
C++ shadow and replay checks have zero skipped/mismatched events
selected matchup / cell / retest artifact shapes are correct
required rev0052 docs/scripts/tests/data exist
```
