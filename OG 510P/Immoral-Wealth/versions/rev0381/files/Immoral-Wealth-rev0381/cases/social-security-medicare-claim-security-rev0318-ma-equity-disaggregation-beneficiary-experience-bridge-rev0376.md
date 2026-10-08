---
revision_current: rev0376
generated_at: 2026-06-18T19:35:00Z
status: active_equity_join_bridge_not_certified_current
case_id: social-security-medicare-claim-security-rev0318
---

# MA equity-disaggregation and beneficiary-experience join bridge — rev0376

This bridge blocks a new false pass: an MA contract can now have aggregate denial, appeal, contractor, resident, audit, enforcement, quality, and RADV routes while still hiding which beneficiary groups absorbed the burden.

## Required correction

A certifying row must preserve subgroup denominator and experience fields alongside the existing denial/remedy row: dual eligible status, LIS or low-income cost-sharing status, reason for entitlement/disability, race/ethnicity method, age, sex, county/place, contractor/delegated entity, nursing-home or post-hospital status, denial/appeal/overturn/unappealed denial, time-to-care, restoration, CAHPS or MCBS experience context, MMD place/subgroup context, Star Ratings/EHO4All status, RADV/payment integrity, and suppression/method notes.

## Source roles

- `S600` supplies beneficiary denominator and subgroup join variables.
- `S601` supplies disparity/place context only.
- `S602` supplies beneficiary-reported access/risk/outcome route.
- `S603` supplies contract-level plan-experience context.
- `S604` qualifies Star Ratings by showing that the CY2027 EHO4All/Health Equity Index reward is not being implemented.

## False-pass blockers

- No aggregate-subgroup pass: overall contract denial or appeal rates cannot certify claim security without dual/LIS/disability/race/geography denominators.
- No Star Rating pass: high contract quality ratings or CAHPS scores cannot offset service-level denied medically necessary care.
- No MMD-context pass: disparity context can target scrutiny but is not denial, remedy, contractor, or payment-integrity proof.
- No survey-only pass: MCBS/CAHPS experience evidence must be joined to administrative denial/remedy rows before certification.
- No HEI/EHO4All pass: CY2027 nonimplementation means the archive cannot rely on that reward as an active corrective instrument.
- No privacy-suppressed pass: cell suppression, LDS limits, or missing subgroup denominators are blockers, not proof of equity.
- No resident-only vulnerability pass: nursing-home status is necessary but not sufficient; dual/LIS/disability/race/geography must remain visible where data permit.
- No average-remedy pass: restoration must be measured for the same subgroup/service/contract row, not merely for the aggregate contract.

## Minimum viable next row

One SNF or other service-specific contract-month row with subgroup denominator fields from MBSF or equivalent, denial/appeal/overturn/remedy fields from Part C/LDS or public rows, contractor/resident fields from rev0375, beneficiary-experience context from MCBS/CAHPS where linkable, MMD/place context, Star Ratings/EHO4All status, audit/enforcement, RADV/payment-integrity, and explicit suppression/method notes.

Certification remains **not certified current**. This bridge adds row requirements and source routes; it does not acquire the subgroup-level row.
