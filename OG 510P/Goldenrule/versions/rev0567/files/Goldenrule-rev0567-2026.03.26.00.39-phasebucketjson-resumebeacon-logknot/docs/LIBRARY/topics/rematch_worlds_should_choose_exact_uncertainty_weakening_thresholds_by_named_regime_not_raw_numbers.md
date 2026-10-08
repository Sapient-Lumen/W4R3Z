# Rematch worlds should choose exact uncertainty weakening thresholds by named regime, not raw numbers

## Claim
Once the archive already exposes one-shot weakening shifts and persistent-threshold closure, the inheritor should choose weakening hysteresis by a small named regime normal form rather than by memorizing raw threshold integers.

## Why
- the same numeric threshold can matter for very different reasons: `11` is a special case that unlocks only the middle-band precision→neutral release and does **not** enlarge the relaxed-floor basin,
- thresholds `12` and `17` eventually park the same stronger-tier states at relaxed anchor `25`, but `12` does so only through the staged `8→13→25` path while `17` allows the direct `8→25` jump,
- threshold `23` is qualitatively different again because it is the first regime that can discharge precision anchor `2` directly under relaxed floors.

## Current archive consequence
- the weakening overlay now compresses to six exact regimes: `0–6`, `7–10`, `11`, `12–16`, `17–22`, and `23+`,
- only one regime is off-axis with respect to relaxed-floor behavior: threshold `11` changes middle-band behavior without changing relaxed-floor release reach,
- thresholds `12–16` and `17–22` have the same eventual anchor counts `{"2": 7, "13": 6, "25": 5}` but different settling depth (`3` versus `2` cycles).

## Operational rule
1. first decide whether you want full stickiness, suffix-only relaxed release, middle-only precision relief, staged relaxed release, direct entry release, or full release,
2. then choose any numeric threshold inside the corresponding regime band,
3. treat threshold `11` as a middle-band knob, not as a relaxed-floor knob,
4. use threshold `12` when staged release from boundary `8` is acceptable,
5. use threshold `17` only when the direct `8→25` jump itself is operationally important.

## Pointers
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_regime_normal_form_snapshot_20260308.md`
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_regime_normal_form.py`
