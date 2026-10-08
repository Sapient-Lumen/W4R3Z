# rev0043 refactor / audit

## New module

```text
src/muc5/action_hard_racing.py
```

This separates online hard-frame adaptive collection from:

```text
action_hard_frame.py     fixed-matrix hard-frame selector audits
action_race_audit.py     offline fixed-vs-adaptive label comparison
action_racing.py         generic adaptive action-counterfactual helpers
```

The new module intentionally reuses the existing branch rollout and C++ transition finalization helpers instead of inventing a parallel labeler.

## New audit checks

The cube audit now checks:

```text
rev0043 summary revision and codename
selected hard situations >= 8
all selected frames are high-action
branch truncations == 0
C++ skipped transitions == 0
C++ mismatches == 0
C++ checked transitions >= 8,000
allocation rows == branch rows
adaptive allocation rows > 0
decisive situations >= 1
required rev0043 files exist
```

## Negative-result guard

No gameplay policy is promoted in rev0043. The archive records label-quality metrics, not a claim that the current labels are enough to train a strong policy.
