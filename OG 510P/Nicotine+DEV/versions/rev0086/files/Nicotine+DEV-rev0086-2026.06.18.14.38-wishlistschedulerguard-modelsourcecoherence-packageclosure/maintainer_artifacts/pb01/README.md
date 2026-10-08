# PB-01 classified research harness — rev0074

Current disposition: `docs/PB01-CURRENT-DISPOSITION-REV0074.md`.

The active surface centralizes the former duplicated fixture and separates four roles:

```text
pb01_harness.py                              shared infrastructure
test_pb01_current_behavior_witness.py        observations, not desired behavior
test_pb01_race_compatibility_controls.py     behavior experiments must preserve
test_pb01_rev0038_split_counterexample.py    why the old blanket guard is unsafe
test_pb01_origin_aware_experiment.py         narrower unselected hypothesis
```

The original two large test files are preserved byte-for-byte under `docs/archive/rev0073-active-pb01/`.

Neither the rev0038 patch nor the rev0074 origin-aware experiment is selected for upstream use; both are not selected. Everything here is research-only and must not be copied into a contribution.
