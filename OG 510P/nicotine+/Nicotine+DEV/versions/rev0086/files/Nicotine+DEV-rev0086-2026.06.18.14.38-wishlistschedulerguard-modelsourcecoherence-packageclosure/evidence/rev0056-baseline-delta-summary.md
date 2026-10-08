# rev0056 baseline-delta replay summary

Input: uploaded `Nicotine-source(1).zip` extracted as the archived rev0003 source bundle.

rev0056 adds the missing explicit before-state replay layer:

```text
current-behavior witnesses on unpatched uploaded source: 9/9 pass
fixed-behavior regressions on unpatched uploaded source: 21/21 expected nonzero
selected-stack fixed-behavior regressions after patch: 21/21 pass (inherited from rev0055 source-bundle stack rerun)
before/after joined lane-packet deltas: 21/21 pass
```

Interpretation: the uploaded source bundle is not only used for source anchors and patched pass checks; it is also used as the unpatched baseline proving that the selected fixed regressions are meaningful against the archived source lanes.

Boundary: this remains archived-source replay proof. A fresh current checkout/tarball is still required before filing against live upstream head.
