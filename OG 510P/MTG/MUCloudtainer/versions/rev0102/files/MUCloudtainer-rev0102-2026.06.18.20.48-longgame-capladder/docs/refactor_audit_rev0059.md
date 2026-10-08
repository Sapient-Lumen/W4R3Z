# Refactor/audit — rev0059

## Refactor performed

rev0059 moves reusable decomposition helpers out of `scripts/run_rev0058_decomposition.py` and into `src/muc5/terminal_decomposition.py`:

```text
compare_decomposition_by_life()
decomposition_gate_report()
sample_transition_rows()
summary_by_arm_life()
score_from_summary_row()
library_share_from_summary_row()
```

This matters because the next claim runs need to compare A/B/C/D arms, gate cleanliness, and ship compact C++ evidence without copy-pasted script-local logic.

## New artifact audit seam

rev0059 also adds:

```text
src/muc5/revision_artifacts.py
scripts/run_rev0059_artifact_audit.py
```

The new seam checks the live revision’s own artifact contract separately from the inherited monolithic `scripts/audit_cube.py`.  The first use guards against the specific waste pattern identified in rev0057: accidentally shipping full raw C++ transition CSVs when compact samples are enough.

## Waste avoided

rev0059 generated and checked:

```text
47,323 C++ chosen transitions in the A-D run
27,500 C++ chosen transitions in the life-20 stress run
74,823 total checked transitions
```

It ships compact samples rather than full transition tables.
