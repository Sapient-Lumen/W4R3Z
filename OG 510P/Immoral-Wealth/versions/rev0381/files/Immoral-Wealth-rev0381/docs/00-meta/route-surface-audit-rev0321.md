---
status: audit
claim_kind: archive_refactor
route_role: archive_governance_core
canonical_anchor: false
route_refs:
- archive_governance_core
- source_governance_core
- case_calibration_core
supersedes: null
depends_on:
- route-registry.json
- route-ledger.json
source_refresh_due: 2027-03-31
case_pressure: rev0321_route_refactor
---

# Route surface audit — rev0355

## Finding

rev0320 had a strong evidence graph but a weak route graph. Scoreboards and Markdown frontmatter used dozens of near-synonyms such as `floor`, `floor_core`, `floor_screen`, `conversion_rails`, `conversion_rails_core`, `enforcement_remedy`, `enforceability_core`, `measurement_uncertainty`, `top_tail`, and `housing_land`. These were understandable in local context, but they made the cube less queryable.

rev0321 promotes routing to a governed subsystem.

## Refactor performed

- Added `docs/00-meta/route-registry.json` as the canonical route vocabulary.
- Added `docs/00-meta/route-ledger.json` as a generated route-use ledger.
- Normalized scoreboard `routes` lists to canonical `*_core` route IDs.
- Normalized Markdown `route_role` and `route_refs` frontmatter where clear aliases existed.
- Added validator checks so future route IDs must appear in the registry.
- Kept historical aliases in the registry for search and migration, but new output should emit only canonical route IDs.

## Operator rule

A route is not a label of convenience. It is a commitment about where a future operator should look first.

Use:

- `case_work_core` when the question is how to work a case;
- `case_calibration_core` when the question is where a case fits in the portfolio;
- `certification_core` when the question is whether a pass is allowed;
- `source_governance_core` when the question is evidence lineage or source refresh;
- `remedy_operability_core` when a formal right may fail because the claimant cannot actually invoke, survive, aggregate, or restore the remedy;
- `public_balance_sheet_core` when private claims may become publicly senior under stress.

## Remaining debt

The audit intentionally does not delete all `unrouted` meta surfaces. Some governance notes are stable background and do not need to be active operator routes. Future route debt is instead defined narrowly: a live case or scoreboard field should not emit an unregistered route string, and a front-door/current-release surface should not be marked `unrouted` unless it is purely archival.
