# CMB-S4 forecast-realization and empirical-delta route-pressure audit — rev0319

## Scope

This audit targets a substantive failure mode, not a new registry: forecast and empirical-pressure rows can remain internally valid while their live public-record path has changed. The highest-risk instance in this pass is the primordial-tensor / B-mode lane, because older CMB-S4 design forecasts can be mistaken for a pending acquired record after the project-status surface changed.

## Failure mode found

The cube already separated forecast from evidence, but `rev0318` still let empirical deltas sit one step away from route authority. A route could have forecast and decision pressure while the empirical/source-pressure delta that actually constrains its state was not a route-facing edge in the authority graph.

The risk is sharper for `R-OQ0057-PRIMORDIAL-TENSOR-BMODES`: CMB-S4 design forecasts remain scientifically useful as target sensitivity and decision-planning pressure, but CMB-S4-specific rows can no longer be phrased as if a CMB-S4 public map/likelihood release is simply pending. The correct state is historical design forecast plus successor/limited-upgrade watchlist until a named acquired public record exists.

## Repair implemented

`rev0319` makes empirical deltas route-facing in the source-replayed authority graph with `empirical-delta-route-condition` edges. Lint now rejects missing empirical-delta→route edges and rejects S2-or-higher route rows that lack at least one empirical-delta/source-pressure row.

The revision also adds four missing empirical/source-pressure deltas so route coverage is complete:

- `ED-0012-FAMILYC-LEARNED-INVERSE-OOD-CUTOFF-PRESSURE`
- `ED-0013-AS-AMPLITUDE-REGULATOR-PORTABILITY-PRESSURE`
- `ED-0014-CAUSAL-SET-QSG-DYNAMICS-PRESSURE`
- `ED-0015-FAMILYB-THERMO-LOCAL-LAW-SCOPE-PRESSURE`

For CMB-S4 specifically, `REF-0633` is now the live project-status anchor on the carrier, protocol, evidence unit, empirical delta, decision experiment, severity, measurement, systematic, calibration, credit, and independence rows that spend primordial-tensor forecast language. `FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json` includes `FSF-0004-CMBS4-SHUTDOWN-CLOSEOUT-CUSTODY` so future source-custody drift is executable rather than remembered only in prose.

## What changed scientifically

No route is promoted. The substantive change is that CMB-S4 project non-realization is treated as route pressure of the right kind: it is a forecast-realization/custody constraint, not a tensor null result and not evidence against inflationary tensors. A future successor experiment can still create a strong empirical delta, but it must enter as a named public map/likelihood record with foreground, delensing, calibration, sky-mask, and null-channel disclosure.

## Route-state effect

- `R-OQ0057-PRIMORDIAL-TENSOR-BMODES` stays `S2`.
- `ED-0010-CMB-S4-PRIMORDIAL-TENSOR-FORECAST-CORRIDOR` is now a historical-design / successor-record corridor, not a pending CMB-S4 acquired-record corridor.
- `DX-0005-CMB-PRIMORDIAL-TENSOR-BMODE` now includes a `project-realization-failed-or-superseded` outcome class.
- Any future wording that treats CMB-S4 design forecasts as acquired public evidence should fail the freshness and route-pressure audits.

## Non-promotion rule

A live project-status repair can make a route more honest and less stale. It cannot increase candidate authority. Promotion still requires a realized empirical delta, public-record carrier, acquisition protocol, severe negative controls, observed-sector recovery, and the normal route-state gates.
