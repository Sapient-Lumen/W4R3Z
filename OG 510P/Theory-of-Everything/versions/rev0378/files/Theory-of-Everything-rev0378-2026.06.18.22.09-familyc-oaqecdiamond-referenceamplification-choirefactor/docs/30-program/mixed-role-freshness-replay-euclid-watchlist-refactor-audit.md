# rev0354 mixed-role freshness replay / Euclid watchlist refactor audit

## Scope

This revision closes the high-risk freshness replay gap deliberately left open in rev0353: `FSF-0022-COSMO-DESI-LYA-EUCLID-SOURCE-STAGING` mixed three different source roles in one assertion:

- DESI DR2 public chain/posterior custody (`REF-0688`) can be retained as existing public-record/acquired-support custody on the rows that already own the DESI BAO likelihood surface.
- Lyman-alpha, interpretation-caveat, and DESI-portal/String-M records (`REF-0689`, `REF-0690`, `REF-0675`) are denominator pressure or route-local handoff only.
- Euclid release-timeline custody (`REF-0637`) is future runway, not realized Euclid cosmology evidence.

A single broad `typed_event_replay_policy` would have hidden this distinction. rev0354 therefore adds row-scoped `typed_event_replay_policies` to the assertion instead of creating a new registry layer.

## Executable changes

- `FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json` is now schema version `1.8` and revision `rev0354`.
- `FSF-0022-COSMO-DESI-LYA-EUCLID-SOURCE-STAGING` now has three row-scoped replay policies:
  - `FSF-0022-DESI-DR2-ACQUIRED-PUBLIC-CUSTODY`
  - `FSF-0022-LYA-INTERPRETATION-DENOMINATOR-PRESSURE`
  - `FSF-0022-EUCLID-RELEASE-TIMELINE-FORECAST-RUNWAY`
- Added five source snapshot receipts to FSF-0022, including the previously undercounted `REF-0675` DESI-portal/String-M denominator record.
- Added six `forecast_runway` / `retained_as_forecast_runway` source-role events for `REF-0637` on the DESI/Lyman-alpha/Euclid staging rows that already carry Euclid release-timeline custody.
- `FSF-0003-EUCLID-CERN-WATCHLIST-BOUNDARY` now has a `watchlist_zero_route_placement_policy` for `REF-0627` and `REF-0628`.
- `tools/frontier_source_freshness.py` now validates both one-role replay policies and row-scoped mixed-role policies, and it replays watchlist zero-placement against the source-custody isolation evaluator.
- `tools/source_role_negative_replay_tests.py` now runs 10 compact mutation cases, including row-scoped mixed-role event removal and watchlist route-placement injection.
- `tools/lint_archive.py` now requires FSF-0022 to retain acquired-support, denominator-pressure, and forecast-runway replay roles, and requires FSF-0003 to retain zero-placement watchlist enforcement.

## Current replay state

After this repair, frontier freshness evaluates:

- Freshness assertions: `31`
- Typed replay-enabled assertions: `30`
- Required source-carrying rows checked: `547`
- Typed replay rows checked: `547`
- FSF-0022 row-scoped policy checks: `19`
- Watchlist zero-placement refs checked: `2`
- Watchlist route-bearing placements: `0`
- Freshness failures: `0`

The archive now contains `741` row-level `source_role_events` across `94` ledgers. The increase in this pass is intentionally small: six new Euclid forecast-runway retention events, not a broad ledger migration.

## Why this was risky

The mixed DESI/Lyman-alpha/Euclid assertion sat exactly at a high-salience public-record seam. DESI public chains are real public custody, but Lyman-alpha/interpretation papers and Euclid release timing are not the same kind of source. Treating all of them as acquired support would overpromote; treating all of them as denominator pressure would underdescribe the existing DESI BAO public record; treating all of them as forecast runway would blur a current public DESI product with a future Euclid release.

The fix is row-role-specific replay: a freshness assertion passes only when the row still carries the typed event that says how that source ref may be read.

## Watchlist correction

`FSF-0003-EUCLID-CERN-WATCHLIST-BOUNDARY` has no required source-carrying rows by design. That is safe only if zero placement is executable, not just prose. rev0354 makes the zero-route-placement rule an explicit freshness policy tied to `tools/frontier_source_policy.py`. Injecting `REF-0627` into a route-bearing row now fails the negative replay test.

## Non-promotion boundary

No route score, authority state, promotion ceiling, evidence-unit score, empirical-delta authority, forecast realization, decision-experiment outcome, observed-sector recovery state, or current-head ordering changed. The revision only sharpens source custody, replay semantics, and watchlist isolation.

## Followthrough

The next useful work is not more source-role vocabulary. It is narrower:

- audit `no-new-credit` wording so users do not mistake it for denial of the underlying acquired-support row;
- add retained forecast-runway / operational-status mutation coverage in the shared helper if a distinct failure class appears;
- continue compressing generated audits only where row scans remain complete;
- consider a small report that lists freshness assertions by replay mode: one-role, row-scoped mixed-role, zero-placement watchlist.
