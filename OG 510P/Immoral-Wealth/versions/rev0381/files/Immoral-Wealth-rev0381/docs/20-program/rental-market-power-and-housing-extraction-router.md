---
status: program_tool
claim_kind: router
route_role: housing_land_core
canonical_anchor: false
route_refs:
- housing_land_core
- anti_monopoly_core
- household_market_extraction_core
- measurement_uncertainty_core
- enforcement_remedy_core
supersedes: null
depends_on:
- docs/10-framework/housing-market-power-renter-seniority.md
- docs/00-meta/field-registry.json
- docs/00-meta/field-use-ledger.json
source_refresh_due: 2027-03-31
revision_current: rev0371
generated_at: 2026-06-18T16:58:56Z
---

# Rental market power and housing extraction router — rev0357

Use this router when a case involves ordinary shelter costs but the active mechanism is not only supply shortage, tenant screening, eviction, public finance, or climate risk. The router is triggered when housing costs or housing wealth are mediated by **private coordination, owner concentration, fee/repair systems, land-lease control, or mobility lock-in**.

## Trigger questions

- Does a pricing tool use nonpublic competitor data or generate rent recommendations across competing landlords?[S414][S415][S416]
- Is the relevant market local enough that national ownership shares hide neighborhood or school-catchment power?[S417][S418]
- Are advertised rents separated from mandatory fees, repair charges, deposit rules, or move-out penalties?[S419][S420]
- Does the resident own the structure but rent the land, making exit or resale practically infeasible?[S421][S422][S423][S424][S425]
- Does a public or private remedy restore the household, or merely impose prospective conduct rules?

## Minimum evidence pack

1. owner and beneficial-owner map by parcel, building, or community;
2. pricing vendor, data-source, and recommendation-adoption evidence;
3. all-in monthly housing cost, including fees, utilities, maintenance charges, lot rent, and finance cost;
4. exit/mobility costs and asset-forfeiture risk;
5. complaint, refund, repair, deposit, and resident-purchase remedy outcomes;
6. subgroup incidence by income, race, age, disability, family status, tenure type, and place.

## Field bundle

The rev0322 field bundle is registered in `docs/00-meta/field-registry.json` and includes `rental_market_power_gate`, `algorithmic_rent_setting_coordination`, `institutional_single_family_rental_concentration`, `corporate_landlord_fee_stack`, `manufactured_housing_land_lease_split`, `manufactured_home_mobility_lock_in`, `manufactured_lot_rent_escalation`, and `housing_market_power_remedy_access`.


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
