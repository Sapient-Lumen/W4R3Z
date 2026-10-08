# Rematch worlds should trace fixed weakening thresholds to their eventual canonical anchor under persistent requests

## Claim
Once an inheritor installs the one-shot weakening-hysteresis overlay, they should also ask where that fixed threshold eventually parks the system under a persistent request, because some deferred weakenings are only delayed while others stay blocked until a larger threshold band is admitted.

## Why
- a one-shot threshold explains only the first move, but repeated operation can convert a deferred boundary weakening into a later canonical-anchor weakening,
- the key staged case is current state `8` under a relaxed floor: threshold `12` is already enough to reach relaxed anchor `25` eventually by first stabilizing to `13`, even though the direct `8→19→25` jump still needs threshold `17`,
- precision anchor `2` is different: under the same relaxed floor there is no staged release path, so full release to `25` waits until the threshold reaches the full outer-anchor shift `23`.

## Current archive consequence
- the fixed-threshold closure partitions into exact bands `0–6`, `7–10`, `11`, `12–16`, `17–22`, and `23+`,
- thresholds `12–16` and `17–22` have the same eventual anchor counts but different settling depth, because `8` reaches `25` in `3` cycles at `12` and only `2` cycles at `17`,
- under persistent relaxed floors the minimum thresholds for eventual arrival at `25` are `{2:23, 8:12, 13:12, 18:7, 19:0, 25:0}`.

## Operational rule
1. choose the weakening threshold for one-shot stickiness,
2. trace the repeated-controller closure under the request classes you expect to persist,
3. distinguish **direct release** from **eventual release**,
4. treat state `8` as a staged-release candidate,
5. treat precision anchor `2` as a true sticky hold until the threshold reaches `23`.

## Pointers
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis_closure_snapshot_20260308.md`
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_hysteresis_closure.py`
