# Forecast-credit and graviton-realization audit

This revision fixes a present-authority overcredit seam rather than adding a new route.

## What was wrong

Some discriminator forecasts were describing conditional future records while their `current_maximum_credit` exceeded the route's current authority state. The most consequential cases were the lab graviton-counting forecasts: single-graviton absorption and graviton-counting tomography are now serious proposal corridors, but no detector-local acquired public click/count record exists in this cube. The causal-set dynamics forecast had a similar smaller mismatch: it preserved a conditional S2 future target while the route remains current S1 until native quantum dynamics, matter coupling, continuum recovery, computability, and replay are public.

## Repair

`rev0322` makes the distinction executable. `tools/forecast_credit_policy.py` now rejects:

1. discriminator forecasts with no explicit `source_refs`;
2. any forecast whose `current_maximum_credit` exceeds the current `authority_state` of its route;
3. any `forecast-public-record` evidence unit whose `maximum_credit` exceeds the current route state.

The repair demotes current graviton-counting evidence and forecast credit to S2, keeps only a conditional S3 pocket after a future detector-local acquired public record, and demotes the current causal-set dynamics forecast credit to S1 while preserving conditional S2 language for a future replayable dynamics/matter/continuum artifact.

## Substantive posture

Single-graviton and graviton-counting work is no longer an impossibility story, but the live public state is still proposal/design/statistics pressure. The route should be treated as important because it names a possible acquired-record path, not because the record already exists. Likewise, causal-set quantum dynamics remains a live route pressure point because the obstruction is now more exact, not because route identity has been achieved.

No route is promoted.
