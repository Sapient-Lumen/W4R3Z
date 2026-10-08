---
status: active_bridge
claim_kind: program_protocol
route_role: score_mediated_exclusion_core
canonical_anchor: false
route_refs:
- score_mediated_exclusion_core
- case_calibration_core
supersedes: null
depends_on:
- verdict-engine-and-certification-gates.md
- scoreboard-schema.json
source_refresh_due: 2026-12-31
case_pressure: rev0315_score_mediated_exclusion
---


# Score-mediated exclusion evidence pack

A case needs this pack before a comfort verdict if Gate 17 is active.

## Market inventory

- Which reports, scores, vendors, and model systems are used?
- Which decisions do they affect: credit, rent, job, insurance, account, benefit, utility, price, refund, or fraud hold?
- Are systems public, private, hybrid, or vendor-operated?

## Outcome inventory

- denial rate;
- price spread;
- adverse-action reasons;
- dispute rate;
- correction rate;
- time to correction;
- transaction lost before correction;
- subgroup incidence;
- human override rate;
- vendor audit findings;
- complaint and enforcement outcomes.

## Data quality inventory

- source data family;
- update frequency;
- stale-record suppression;
- sealed/expunged/dismissed record treatment;
- medical-debt/collection treatment;
- identity-theft suppression;
- model drift and proxy testing;
- records matched by name, SSN, address, biometrics, device, phone, or probabilistic linkage.

## Burden assignment

Evidence debt belongs to the institution using the score, not only to the claimant. If a vendor or agency cannot explain the score or prove correction speed, the case receives at least a hard proof-debt warning.
