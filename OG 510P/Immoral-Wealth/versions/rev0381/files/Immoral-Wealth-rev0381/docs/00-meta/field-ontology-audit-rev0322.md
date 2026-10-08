---
status: audit
claim_kind: field_governance
route_role: source_governance_core
canonical_anchor: true
route_refs:
- source_governance_core
- certification_core
- case_calibration_core
supersedes: rev0321
depends_on:
- field-registry.json
- field-use-ledger.json
- ../20-program/scoreboard-schema.json
source_refresh_due: 2027-03-31
revision_current: rev0370
---

# Field ontology audit — rev0357

rev0322 audits the scoreboard field layer. The archive already had strong evidence and route ledgers, but the field layer still had two problems:

1. **Observed-but-unregistered fields.** Five fields appeared in scoreboards only because `fields.additionalProperties` allowed arbitrary keys: `intergenerational_opportunity_and_person_level_ownership, family_gatekeeper_dependence, citizenship_residency_access, pension_housing_age_hidden_wealth, ownership_visibility`. rev0322 promotes these fields into `scoreboard-schema.json`.
2. **Unowned schema inventory.** The schema contained fields with no usage but no lifecycle status. rev0322 classifies every field by family, primary gate, primary route, usage count, source coverage, and lifecycle status.

## Current counts

- Registered schema fields: **347**
- Used fields: **292**
- Registered but currently unused fields: **55**
- Legacy fields promoted to schema: **5**
- New rental-market-power fields: **16**
- Scoreboard case count: **91**

## Validation change

`scoreboard-schema.json` now sets `fields.additionalProperties` to `false`. Future releases must add a field to the schema and `field-registry.json` before a scoreboard can emit it.

The validator now enforces:

- field registry revision sync;
- exact equality between schema fields and registry rows;
- exact equality between schema fields and field-use-ledger rows;
- no unregistered field keys in scoreboards;
- usage counts in the field ledger matching actual scoreboard use;
- rev0322 rental-market-power case-family coverage.

## Why it matters

Field drift is not harmless. If a scoreboard can silently create a new key, the cube stops being comparable. If unused fields have no lifecycle status, operators cannot tell whether a field is planned, abandoned, stale, or simply waiting for a case. rev0322 turns fields into governed claims rather than loose labels.


## rev0323 compatibility note

rev0323 keeps this audit as an active reference while adding temporal currentness and dynastic-opacity fields. The active field registry now reports `367` schema fields.
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
