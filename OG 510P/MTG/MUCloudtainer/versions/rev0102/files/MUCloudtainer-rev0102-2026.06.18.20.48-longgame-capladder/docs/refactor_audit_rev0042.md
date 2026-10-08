# rev0042 refactor/audit notes

New code:

```text
src/muc5/action_race_audit.py
tests/test_rev0042_hard_racing.py
scripts/run_rev0042_hardframe_racing_audit.py
```

The refactor is intentionally narrow.  The hard-frame collector remains responsible for selecting public frames and generating branch rollouts.  The new racing module consumes branch rows and compares label-allocation methods over the same generated branch matrix.

This separation keeps the seam auditable:

```text
action_hard_frame.py  -> creates expensive branch evidence
action_race_audit.py  -> compares how a labeler would spend/interpret that evidence
```

Audit checks added:

```text
rev0042_hard_racing_outputs
rev0042_label_race_audit
required_files_present_through_rev0042
```

Validation status archived in `data/rev0042_audit.json`.
