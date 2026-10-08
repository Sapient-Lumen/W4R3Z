---
status: active_bridge
claim_kind: navigation_surface
route_role: direct_answer
canonical_anchor: false
route_refs:
- direct_answer
- case_work_core
- certification_core
- remedy_operability_core
- public_balance_sheet_core
supersedes: null
depends_on:
- ../00-meta/route-registry.json
- ../00-meta/route-ledger.json
source_refresh_due: 2027-03-31
case_pressure: rev0321_route_refactor
revision_current: rev0371
generated_at: 2026-06-18T16:58:56Z
---

# Operator route registry and query planner

Use this when entering the cube with an ambiguous question.

## First classify the question

- **Is this about whether a verdict/pass is allowed?** Start with `certification_core`.
- **Is this about how to write or revise a case?** Start with `case_work_core`.
- **Is this about whether a case belongs in the portfolio?** Start with `case_calibration_core`.
- **Is this about evidence, source freshness, or claim lineage?** Start with `source_governance_core`.
- **Is this about who gets rescued or who pays under stress?** Start with `public_balance_sheet_core`.
- **Is this about whether a formal right actually repairs harm?** Start with `remedy_operability_core`.

## Then follow the ledger

`docs/00-meta/route-registry.json` defines the route vocabulary. `docs/00-meta/route-ledger.json` shows which files and scoreboard claims currently use each route.

Do not invent a new route because a phrase feels useful. Add a route only when it changes operator behavior: where to start, which proof debt to demand, which gate can block certification, or which case family should absorb new evidence.


## rev0322 carry-forward note

rev0322 carries this rev0321 surface forward unchanged as an active dependency while the current audit/refactor focuses on field ontology and rental-market-power coverage.


## rev0323 compatibility note

This surface remains active in rev0323 and interoperates with temporal-currentness and dynastic-opacity routing.
<!-- current_revision: rev0324; audit overlay: semantic-currentness-invariants-and-cloudtainer-waste-map -->
<!-- current_revision: rev0325; overlay: substance-case-hardening-and-refresh-sync-refactor -->

<!-- current_revision: rev0326; codename: gate20-backstop-burndown-and-source-canonicalization -->

<!-- current_revision: rev0327; codename: compute-climate-health-minerals-backstop-burndown -->

<!-- current_revision: rev0328; codename: federal-claim-security-credit-guarantee-burndown -->

<!-- current_revision: rev0329; codename: sovereign-fiscal-contingent-liability-and-public-asset-burndown -->

<!-- current_revision: rev0330; codename: score-mediated-exclusion-rights-remedy-burndown -->

<!-- current_revision: rev0331; codename: fresh-start-family-transfer-backlog-closure-and-source-fit-refactor -->

<!-- current_revision: rev0332; codename: seed-backlog-closure-and-gate-inventory-source-refactor -->

<!-- current_revision: rev0333; codename: workplace-power-current-law-hardening-and-seedclass-refactor -->

<!-- current_revision: rev0334; codename: household-market-extraction-current-law-hardening-and-seedclass-burndown -->

<!-- current_revision: rev0335; codename: place-public-finance-service-floor-hardening-and-sourcefit-refactor -->

<!-- current_revision: rev0336; codename: jurisdictional-mobility-current-law-hardening-and-sourcefit-burndown -->

<!-- current_revision: rev0337; codename: democratic-power-and-portfolio-seedclass-closure; rollforward_marker: rev0337 -->

<!-- current_release: rev0339; rev0339 currentness/callchain repair validated -->

<!-- current_release: rev0340; memo-citation-lineage-and-source-alias-canonicalization validated -->
<!-- current_release: rev0342; case-memo-status-drift-and-stale-seed-language-repair validated -->

<!-- current_revision: rev0343; live-doc source alias canonicalization validated -->

> rev0344 release-surface note: source-use lineage and validator callchain were repaired in rev0344; this document remains an active live surface.


> rev0345 current-surface note: retained as a current release surface after the front-door reality audit and changelog repair.

<!-- current_release: rev0368; rev0368 visibility marker for release-surface validation. -->


Current release visibility: rev0369.


Current release marker: rev0370.
