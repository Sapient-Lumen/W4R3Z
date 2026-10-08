# rev0030 experiment matrix additions

| Axis | rev0030 status | Why it matters |
|---|---:|---|
| Repeated opening counterfactuals | built | Reduces single-rollout mulligan label noise |
| Repeated counterfactual mulligan agent | built | Makes averaged counterfactual labels enter strategy bundles |
| No-choice segment fingerprints | built | Prepares C++ segment batching |
| C++ trace/check gate | reused | Confirms new traffic stays in supported transition space |
| Same-shell mulligan panel | built | Separates mulligan policy from deck/pilot shell |

Next expansion:

```text
increase paired openings from 24 to hundreds
increase branch reps from 2 to 8+
add multiple opponent/pilot contexts per first hand
use sequential stopping when keep/mulligan branches are clearly tied
```
