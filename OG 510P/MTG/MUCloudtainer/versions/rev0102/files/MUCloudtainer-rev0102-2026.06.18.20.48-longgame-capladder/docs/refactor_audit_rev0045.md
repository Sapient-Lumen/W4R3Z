# rev0045 refactor/audit notes

## Refactor

`src/muc5/action_margin_compare.py` separates queue comparison from the branch-racing machinery:

```text
select_hard_screen_snapshots(...)
collect_margin_vs_hard_queue_comparison(...)
```

The new code reuses rev0044's `_race_selected_snapshots(...)` helper, so matched selector comparisons do not duplicate branch rollout, allocation, or C++ shadow-check code.

## Audit focus

rev0045 audits that:

```text
hard-screen and margin-screen see the same public candidate pool
both select 10 situations
only the union of selected situations is branched
both methods are scored from the same branch outcomes
branch truncations are zero
C++ shadow transition mismatches are zero
C++ skipped events are zero
```

## Result

The margin queue and hard queue overlapped on 5 of 10 selected frames. The margin queue did not beat the hard queue on decisive-label density in this smoke run. That result is archived rather than hidden because negative selector results are valuable at this stage.
