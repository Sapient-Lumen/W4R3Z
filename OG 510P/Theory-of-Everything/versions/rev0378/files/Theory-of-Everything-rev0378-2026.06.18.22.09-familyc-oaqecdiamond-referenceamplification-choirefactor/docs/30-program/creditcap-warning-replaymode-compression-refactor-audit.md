# rev0355 credit-cap warning / replay-mode / compression refactor audit

## Scope

rev0355 focuses on three remaining failure-prone seams after the mixed-role freshness replay pass:

1. Human warning surfaces still carried stale freshness replay metrics even though the generated audit had moved to 31 assertions and 547 event rows.
2. `no-new-credit` was still semantically overloaded: some historical route-pressure mirror events used it where the safer meaning was simply S0/no-new-route-credit.
3. `route-condition-ceiling-audit.generated.md` still risked becoming restart exhaust if it printed broad all-pass file coverage instead of compact counts and failures.

The pass deliberately avoids a new registry. The changes are local lint, replay, generated-audit, and helper repairs.

## Executable changes

- Added `tools/source_role_credit_cap_policy.py` and generated `docs/30-program/source-role-credit-cap-audit.generated.md`.
- The credit-cap policy scans all row-level and ledger-level `source_role_events`; current generated count is 741 events across 94 ledgers.
- `no-new-credit` is now reserved for `acquired_support` events with `source_ref_disposition: retained_as_acquired_support`, `credit_cap_scope: freshness_event_no_incremental_route_credit`, and explicit public source refs.
- Forecast-runway and operational-status retained custody events must be S0 with `credit_cap_scope: source_role_event_no_new_route_credit`.
- Normalized 14 ambiguous historical events to S0 source-custody/no-route-credit semantics while preserving their prior row-context cap in `row_context_credit_cap_before_rev0355`.
- Expanded `tools/source_role_negative_replay_tests.py` to 13 mutation cases, including credit-cap drift and acquired-support/forecast/status source-ref removal.
- `tools/frontier_source_freshness.py` now renders replay-mode counts for one-role typed replay, row-scoped mixed-role replay, zero-placement watchlist, and row-refs-only modes.
- `tools/lint_archive.py` now rejects stale human warning metrics when typed frontier freshness replay counts change.
- `tools/route_condition_ceiling_policy.py` now keeps compact route, authority-field, and top-file summaries instead of a full all-pass file table.

## Current replay and cap state

- Frontier freshness assertions: `31`
- Typed event rows replayed: `547`
- Replay modes: `29` one-role typed, `1` row-scoped mixed-role, `1` zero-placement watchlist, `0` row-refs-only
- Source-role events checked by credit-cap audit: `741`
- Retained acquired-support freshness custody events: `36`
- Retained forecast/status custody events: `26`
- Credit-cap semantic failures: `0`
- Negative replay mutation cases: `13`
- Route-condition authority checks retained: `3455`

## Why this was risky

The stale warning text was a restart-surface bug: an operator reading `START_HERE.md`, `context-pack.json`, or `SURFACE-STATUS.json` would see old 394-row replay coverage even though the executable generated audit had already advanced to 547 rows. That is not a scientific promotion error, but it is an operator-control error: it makes the restart surface less trustworthy.

The credit-cap issue was subtler. `no-new-credit` should mean: this freshness replay event retains an already-acquired public source but adds no incremental route authority. It should not be used as a vague synonym for S0. Rev0355 makes that distinction executable.

## Compression result

`route-condition-ceiling-audit.generated.md` still evaluates every route-local and multi-route authority ceiling check. It now displays compact route/field/top-file summaries and any failures, not a broad all-pass file table. Lint caps the generated surface so it cannot silently regrow into audit exhaust.

## Non-promotion boundary

No route score, authority state, promotion ceiling, empirical-delta authority, forecast realization, decision outcome, evidence-unit score, or observed-sector recovery state is promoted by rev0355; this revision only repairs source-role credit-cap semantics, warning-metric drift, replay-mode visibility, and generated audit compression.

## Followthrough

The next work should stay narrow:

- compress only generated audit surfaces that still show empty/pass rows;
- add credit-cap scope only where live replay semantics require it;
- factor helper duplication only where repeated mutation/replay logic already exists;
- keep warning-metric mirrors tied to generated audit counts.
