---
status: active_map
claim_kind: source_governance
route_role: source_governance_core
canonical_anchor: false
route_refs:
- source_governance_core
- case_calibration_core
- remedy_operability_core
supersedes: rev0322
source_refresh_due: 2027-03-31
---

# Source function map and coverage gaps — rev0355

rev0321 source coverage expands into remedy operability and route governance.

## New source families

- `S402-S403`: SSA processing-time and hearing-wait surfaces for disability appeal latency.
- `S404-S408`: UI fraud, identity verification, NIDVO/Login.gov, NIST identity guidance, and GAO fraud-control evidence.
- `S409-S413`: arbitration, collective-redress, private enforcement, and legal-authority sources.

## Refactor consequence

The evidence graph from rev0320 remains intact, but route strings are now governed by `docs/00-meta/route-registry.json`. A source can be evidence for a claim while the claim is routed through a canonical operator path. Do not use source tags as route tags.

## Coverage gaps

The main missing evidence is claimant-outcome data: false-positive identity-proofing rates, appeal survival windows, abandonment under arbitration/class waivers, restoration after wrongful denial, and subgroup incidence.


## rev0323 addendum — temporal currentness and dynastic opacity

rev0323 adds currentness governance and dynastic-opacity/charitable-vehicle stress cases. New cases: estate-gift-gst-exemption-currentness-rev0323, dynasty-trust-perpetuity-gst-lock-in-rev0323, beneficial-ownership-trust-entity-visibility-rollback-rev0323, donor-advised-fund-private-foundation-public-subsidy-rev0323. New router surfaces: `temporal_currentness_core` and `dynastic_opacity_core`.
