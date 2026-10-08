# rev0108 immediate next moves

1. On a browser-capable machine, wrap one real resumed validation or MV3 resume-proof run with `python scripts/operator-attempt.py start --output-dir validation/latest/operator-attempt --planned-command "..."` and `python scripts/operator-attempt.py finish --output-dir validation/latest/operator-attempt --outcome ...` so GlassTTY gets its first *real* before/after attempt diff instead of only the synthetic sample bundle.
2. Preserve one sequence where `attempt-diff.json` shows the primary next command changing or the readiness grade moving from `blocked-by-validation` to either `profile-lane-ready` or `live-lane-ready`.
3. Once one real operator-attempt bundle exists, decide whether `operator-handoff.py capture` should optionally copy the latest finished attempt bundle automatically or whether that should remain explicit and operator-driven.

# rev0107 immediate next moves

1. On a browser-capable machine, run `python scripts/operator-handoff.py capture --output-dir validation/latest/operator-handoff-live` immediately before and after one real live browser attempt so GlassTTY gets its first *real* operator-handoff diff instead of only synthetic sample state.
2. Preserve one sequence where the operator handoff bundle changes from `blocked-by-validation` to either `profile-lane-ready` or `live-lane-ready`, so future sessions can compare a true next-action shift instead of only a file-copy proof.
3. Once one live operator-handoff diff exists, decide whether `validate-release.py`, `e2e-fixturelab.py`, or `glasstty-profile.sh capture` should optionally refresh the operator-handoff bundle automatically at the end of successful runs or whether that freeze step should remain explicit and operator-driven.
