# rev0057 platform cost calibration

This experiment addresses the riskiest claim left by `rev0056`: the adaptive router only beat the dense-score histogram when QK score work was assigned a large proxy weight. `rev0057` measures a narrow native CPU primitive ratio instead of leaving that weight arbitrary.

## What is measured

The native C++ probe times primitive vector operations on this CPU path:

- one QK dot vector over the router dimension (`D=8`),
- one sequential value-vector accumulation over `D=8`,
- one sparse/gather value-vector accumulation over `D=8`,
- one block-centroid bound dot over `D=8`,
- the same QK/value primitives for `D=64` as a wider reference.

The wrapper then applies the measured ratios to `REV0056_ROUTER_COST_FRONTIER.json` and asks whether the adaptive bound-gate router beats the dense-score histogram under measured CPU primitive costs.

## Claim boundary

This is not a GPU/fused attention kernel benchmark and not public/pretrained trace evidence. It is a measured CPU primitive calibration that blocks proxy-cost overpromotion.

## Result shape

The measured `D=8` QK/value ratio is far below the `rev0056` all-row break-even (`qk_weight = 12`). The adaptive router can still win on a low-support slice, but not on all rows or high-support rows. Promotion remains blocked.
