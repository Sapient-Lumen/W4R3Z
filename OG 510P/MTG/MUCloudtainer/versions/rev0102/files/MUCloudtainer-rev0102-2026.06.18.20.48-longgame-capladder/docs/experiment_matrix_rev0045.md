# rev0045 experiment matrix

| Experiment | Purpose | Status |
|---|---|---|
| Hard-screen queue | Baseline public hard-frame selector | Compared |
| Margin-screen queue | rev0044 learned public queueing model | Compared |
| Matched union branching | Prevent rollout noise from deciding selector comparison | Implemented |
| C++ transition shadow | Ensure branch traffic still matches C++ microkernel | Passed |
| Gameplay policy promotion | Add new policy to population | Not done |

## Key result

```text
margin_minus_hard_decisive_per_100 = -0.05168
margin_minus_hard_mean_margin      = -0.06667
```

The margin screen is not promoted as a better selector. It remains a queueing hypothesis.
