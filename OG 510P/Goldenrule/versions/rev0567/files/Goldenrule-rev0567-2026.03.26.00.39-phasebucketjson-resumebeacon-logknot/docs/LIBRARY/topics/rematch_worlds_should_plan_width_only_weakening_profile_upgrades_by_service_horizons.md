# Rematch worlds should plan width-only weakening profile upgrades by service horizons

The recent portfolio passes already compressed width-only weakening SLA planning down to a tiny two-breakpoint rule at each width.

A natural remaining nuisance was the inverse question:

> for a target service share `s`, how far can each non-dual profile scale before an upgrade is forced?

The new service-horizon law answers that directly.

For any target service share `s`, define two exact support horizons:

- exact-only horizon: the largest width `w` with `C(6,w)/C(15,w) >= s`
- suffix-only horizon: the largest width `w` with `C(11,w)/C(15,w) >= s`

Those two integers completely determine the upgrade schedule under the current staircase:

- use `exact_only` on widths `1..E(s)`
- then `suffix_hitchhike_only` on widths `E(s)+1..S(s)`
- then `any_single_axis_hitchhike` beyond `S(s)`

So width growth never induces a messy frontier walk. It induces a monotone three-band chain with at most two upgrades.

Examples:

- target `0.50` → no exact-only phase, suffix-only through width `2`, dual-axis from width `3`
- target `0.10` → exact-only through width `2`, suffix-only through width `5`, dual-axis from width `6`
- target `0.01` → exact-only through width `4`, suffix-only through width `9`, dual-axis from width `10`

This is the inverse planning card the inheritor was still missing: choose an SLA target once, then read the future upgrade widths directly instead of consulting the width table repeatedly.

Future redesign signal: if width growth ever creates re-entry, more than two profile upgrades, or any horizon schedule that disagrees with the exact-width or width-cap selectors, then the current weakening portfolio geometry has substantively changed.
