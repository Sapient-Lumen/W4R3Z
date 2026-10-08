---
revision_current: rev0373
generated_at: 2026-06-18T18:20:00Z
title: Medicare Advantage row-contract claim-security workbench
status: active_row_contract_not_certified_current
---

# Medicare Advantage row-contract claim-security workbench — rev0373

This file turns the rev0372 acquisition spine into an enforceable row contract. The case remains **not certified current**.

## Minimum viable pilot

One contract-year/service-category row must join denominator, denial, appeal, overturn, criteria/delegation, delay/harm, notice/remedy, quality/performance, and RADV/payment-integrity fields.

## Required route groups

- Denominator and public plan identity: [S587][S594]
- Denial numerator and reconsideration: [S584][S585][S586][S591]
- Appeal and remedy chain: [S592][S593][S596]
- UM criteria and delegation: [S590]
- Payment integrity and public recovery: [S588][S589]
- Future PA metrics/API implementation route: [S595]

## Required columns

`contract_id, plan_id, segment_id, parent_organization, organization_name, report_year, data_period, state, county, service_area_key, monthly_enrollment, service_category ... automatic_approval_or_reprocessing, cms_enforcement_action, cap_or_sanction_id, contrary_clinical_review, source_ids, source_locator, data_use_restriction, last_refreshed`

Full column contract is in `cases/social-security-medicare-claim-security-rev0318-ma-contract-claim-security-workbench-rev0373.json`.

## False-pass blocks

Aggregate solvency, source-route availability, Star Ratings, appeal overturns, UM criteria submission, RADV audit routes, and denial notice forms are not certification by themselves. Certification requires the joined row and contrary evidence review.
