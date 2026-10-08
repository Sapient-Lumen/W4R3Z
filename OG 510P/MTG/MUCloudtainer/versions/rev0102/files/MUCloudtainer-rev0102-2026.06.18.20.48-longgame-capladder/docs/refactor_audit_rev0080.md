# rev0080 refactor audit

## Concrete refactor

rev0080 adds `src/muc5/population_power.py` so sample-allocation math no longer lives inside one-off audit prose or spreadsheet-style reasoning.  The new module centralizes:

- familywise Hoeffding full-width math;
- required game counts for a target width;
- complete-panel games contributed per hierarchy context;
- pre/post population power ladders using the same aggregation and gate code as promotion.

This avoids a recurring failure mode in the cube: a gate says `precision_target_not_met`, then the next revision hand-waves the amount of evidence needed.  The ladder now computes exact complete-panel reps required before a follow-up run.

## Sampling-frame refactor

`src/muc5/population_sampling.py` now treats `rev0080` as a broad complete population panel.  Unknown revisions remain fail-closed and are excluded from broad pooled gates until explicitly classified.

## Trim discipline

rev0080 ships outcome rows because they are small and directly audit the new run.  It does not ship the full generated C++ transition trace.  The artifact audit caps the raw game table at 720 rows and the C++ sample at 180 rows.

## Checks

- 720 outcome rows, terminal-clean.
- 15,000 sampled C++ transitions, zero mismatches.
- Post-run hierarchical rows: 12.
- Post-run power ladder rows: 12.
- No `rev0080*_transition_rows.csv`, full `rev0080*_cpp_transitions.csv`, or replay JSONL ballast.
