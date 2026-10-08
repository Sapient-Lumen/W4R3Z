# Baseline-delta replay gate — rev0056

rev0056 continues the rev0055 source-use correction by adding the missing reviewer-friendly before/after replay layer.

## Decision

No new private packet is promoted. The seven strict/front packets remain frozen.

The uploaded `Nicotine-source(1).zip` is used as the archived-source baseline in three separate ways:

```text
1. current-behavior witnesses pass on the unpatched uploaded source
2. selected fixed-behavior regressions fail on the unpatched uploaded source
3. the same fixed-behavior regressions pass after the selected patch stack is applied
```

## Replay matrix

```text
current-behavior witness rows: 9/9 pass
unpatched fixed-regression rows: 21/21 expected nonzero
selected-stack patched rows: 21/21 pass
joined before/after delta rows: 21/21 pass
source lanes: github-tag-3.3.10, github-branch-3.3.x, github-branch-master
```

The new before-state evidence is stored in:

```text
data/rev0056_baseline_delta_matrix.csv
evidence/rev0056-baseline-delta-rerun/
```

The joined before/after gate is stored in:

```text
data/rev0056_before_after_delta_gate.csv
```

## Why this matters

rev0055 proved that the uploaded source bundle was used and that the selected integrated patch stack passes on extracted source lanes. rev0056 adds the counterpart baseline: the fixed regressions fail on the same unpatched source lanes, while the historical current-behavior witnesses still pass.

That makes the handoff evidence easier to audit:

```text
current witness: proves archived behavior is still reproduced
fixed regression before patch: proves the regression is not vacuous
fixed regression after selected stack: proves the selected fix shape closes the gate
```

## Boundary retained

This is archived-source replay proof, not live-current filing proof. A fresh current checkout or current tarball with commit/hash/date remains the separate external filing gate.
