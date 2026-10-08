# rev0353 core freshness replay / public-custody refactor audit

## Purpose

rev0353 targets the highest-risk remaining public-source seam after rev0352: freshness checks could still pass for core public records by finding row-level `source_refs` even when the typed `source_role_event` explaining how those refs may be spent was missing, weakened, or mis-capped.

## Changes

- Extended `typed_event_replay_policy` coverage from 15 to 29 frontier-source assertions.
- Increased replayed typed source-role event row checks from 394 to 536.
- Added `retained_as_acquired_support`, `retained_as_forecast_runway`, and `retained_as_operational_status` source-ref dispositions.
- Added or repaired 139 `source_role_events` across core public-record, measurement, systematic, calibration, severity, forecast, decision, delta, route, and theory-pressure rows.
- Expanded negative replay from seven to eight compact mutation tests by adding a retained acquired-support ref-removal case.

## Why this is substantive

The new dispositions separate source custody from promotion authority. A DESI, GWTC, SPT, CMB-S4, LISA, BMV/GIE, amplitudes, asymptotic-safety, learned-inverse, causal-set, GW-test, or B-mode public record can now stay in the row where it belongs, but freshness cannot silently convert the record into new route credit or survive after its typed event coverage is removed.

## Deliberate non-move

`FSF-0022-COSMO-DESI-LYA-EUCLID-SOURCE-STAGING` remains not replay-enabled because it mixes acquired DESI carrier/evidence custody, denominator-pressure interpretation rows, and Euclid future-runway timing in one assertion. A later revision should split it into row-role-specific policies or add explicit mixed-role replay semantics rather than forcing it through one broad role/cap rule. `FSF-0003-EUCLID-CERN-WATCHLIST-BOUNDARY` remains a zero-row watchlist boundary.

## Validation target

The expected generated freshness audit after this pass is:

- Freshness assertions: `31`
- Typed replay-enabled assertions: `29`
- Typed source-role event rows replayed: `536`
- Typed source-role event replay failures: `0`
- Freshness failures: `0`

## Non-promotion boundary

No route score, authority state, promotion ceiling, empirical-delta authority, forecast realization, decision outcome, evidence-unit score, observed-sector recovery state, or current-head ordering changes in rev0353.
