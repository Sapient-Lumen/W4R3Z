---
status: program
claim_kind: router
route_role: temporal_currentness_core
canonical_anchor: true
route_refs:
- temporal_currentness_core
- source_governance_core
- case_calibration_core
- legal_durability_core
supersedes: rev0322
depends_on:
- ../00-meta/currentness-ledger.json
- scoreboard-schema.json
source_refresh_due: 2027-03-31
revision_current: rev0371
generated_at: 2026-06-18T16:58:56Z
---

# Temporal currentness and recertification router — rev0357

Use this router when a case relies on a fact that can become false because of a new statute, rule, guidance page, court order, data release, inflation adjustment, administrative deadline, or dataset revision.

## Rule

A case cannot certify on a stale legal or statistical premise. Currentness must be treated as evidence, not housekeeping.

## Required questions

1. What is the `current_law_snapshot_date`?
2. Which source controls if public pages disagree?
3. Is the claim statutory, regulatory, administrative, dataset-based, litigated, or proxy-based?
4. What event reopens the case automatically?
5. Does the currentness problem affect the verdict, only confidence, or only proof debt?

## Failure modes

- citing pre-amendment law after effective-date change;
- using an old dataset while a newer table changes denominator or coverage;
- treating proposed regulations as final;
- treating a rulemaking rollback as if the prior rule remains in force;
- ignoring inflation-adjusted thresholds;
- leaving legal volatility in prose rather than scoreboard fields.

## Output

Every currentness-sensitive case should have at least one of these fields: `temporal_currentness_gate`, `current_law_snapshot_date`, `source_staleness_risk`, `law_effective_date_stability`, `litigation_or_rulemaking_volatility`, `data_release_lag_risk`, or `source_refresh_cadence_quality`.
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


> rev0347 current-surface note: retained as a current release surface after the front-door reality audit and changelog repair.

<!-- current_release: rev0368; rev0368 visibility marker for release-surface validation. -->


Current release visibility: rev0369.


Current release marker: rev0370.
