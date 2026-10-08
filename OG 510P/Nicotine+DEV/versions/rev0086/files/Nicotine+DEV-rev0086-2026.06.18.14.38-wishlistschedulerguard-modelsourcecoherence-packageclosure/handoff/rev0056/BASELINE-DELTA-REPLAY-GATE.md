# rev0056 baseline-delta replay gate

This handoff addendum answers the reviewer question: did the fixed regressions actually fail on the uploaded unpatched source before passing under the selected stack?

Yes.

```text
source input: Nicotine-source(1).zip extracted source-trees
lanes: github-tag-3.3.10, github-branch-3.3.x, github-branch-master
current witnesses: 9/9 pass
unpatched fixed regressions: 21/21 expected nonzero
selected-stack fixed regressions: 21/21 pass
```

Use these files:

```text
data/rev0056_baseline_delta_matrix.csv
  current witness and unpatched fixed-regression before-state rows

data/rev0056_before_after_delta_gate.csv
  one joined before/after row per strict packet per lane

evidence/rev0056-baseline-delta-rerun/
  captured stdout/stderr for the before-state replay runs
```

The after-state is the rev0055 source-bundle selected-stack rerun:

```text
data/rev0055_source_bundle_stack_rerun_matrix.csv
```

Boundary: this remains archived-source replay evidence. It is not a live-current checkout result.
