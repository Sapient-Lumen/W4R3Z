---
revision: rev0376
base_revision: rev0375
generated_at: 2026-06-18T19:35:00Z
codename: ma-equity-disaggregation-and-beneficiary-experience-join
status: active_release_report
---

# rev0376 — MA equity-disaggregation and beneficiary-experience join

## What changed

Rev0376 adds the next required bridge for the Medicare Advantage claim-security case: aggregate denial, appeal, contractor, resident, audit, enforcement, and quality surfaces cannot certify the case unless the row also preserves subgroup denominators and beneficiary experience.

New source routes: `S600-S604`. New locator-bound evidence records: `VCEDGE-rev0376-0202`-`VCEDGE-rev0376-0209`. New mechanical route rows: **10**. Certified current cases remain **0**.

## Substantive rule

No aggregate-subgroup, Star Rating, survey-only, MMD-context-only, privacy-suppressed, or HEI/EHO4All-existence proof can certify MA claim security. The next row must join denial/remedy with dual/LIS, disability-entitlement, race/ethnicity, geography, beneficiary-experience, contractor/resident, audit/enforcement, RADV/payment, and suppression/method fields.

## Current blocker

The case still lacks one service-specific contract-month row with subgroup denominator fields, denial/appeal/remedy fields, contractor/resident fields, beneficiary-experience evidence, MMD context, Star Ratings/EHO4All status, audit/enforcement, RADV/payment context, and restoration outcome.


Certification status remains **not certified current**.
