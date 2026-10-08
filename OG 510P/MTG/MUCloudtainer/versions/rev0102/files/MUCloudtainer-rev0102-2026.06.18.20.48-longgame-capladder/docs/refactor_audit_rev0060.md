# rev0060 refactor and audit note

rev0060 made two code-level changes while keeping gameplay card semantics unchanged.

## New reusable forensic layer

Added:

```text
src/muc5/trajectory_forensics.py
scripts/run_rev0060_life20_forensics.py
tests/test_rev0060_trajectory_forensics.py
```

The new module reruns public-agent games with the same seeds and agent RNG convention as the C++ shadow rollout path, but emits compact explanatory features instead of full transition CSVs.  The intent is to make future claim explanations cheap enough to run routinely without adding raw evidence ballast.

Representative features:

```text
final/min library by role
library-buffer final
Jace zero / plus / ultimate counts
Counterspell and Force counts
Overlord cast/attack/discard counts
life-total and library-out terminal roles
```

## Decision-count audit and fix

The forensic validation found a longstanding reporting bug: historical terminal rollout rows counted one extra decision after terminal games.  The terminal action was applied correctly, but the loop variable advanced once more before the row was recorded.

Confirmed in rev0060:

```text
forensic games checked: 168
stored decision exact matches: 0
stored decision = applied + 1: 168
winner/score/loss-reason mismatches: 0
```

Changed forward code:

```text
src/muc5/agents.py
src/muc5/cpp_rollout.py
```

Both now count only applied decisions in live results.  rev0060 forensics also carries `legacy_terminal_row_decisions` so older artifacts can be reproduced and audited without hiding the defect.

## Why this matters

The bug does not change winners, scores, terminal mechanisms, or legal-action semantics.  It does slightly inflate historical mean/median decision counts for terminal games by one.  Any claim using decision pace should prefer rev0060+ `applied_decisions` or corrected reruns.

## Ballast control

rev0060 did not ship full raw transition traces.  It ships 168 compact forensic rows plus summaries and case tables.  This continues the rev0058/rev0059 policy of retaining enough evidence to inspect the mechanism while avoiding another tens-of-MiB transition CSV.
