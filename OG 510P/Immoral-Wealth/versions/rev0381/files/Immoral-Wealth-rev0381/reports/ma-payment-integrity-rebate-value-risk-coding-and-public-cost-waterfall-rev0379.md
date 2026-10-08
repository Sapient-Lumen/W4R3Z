---
revision_current: rev0379
generated_at: 2026-06-18T21:36:00Z
title: MA payment-integrity, rebate-value, risk-coding, and public-cost waterfall
status: not_certified_current
---

# MA payment-integrity, rebate-value, risk-coding, and public-cost waterfall — rev0379

Rev0379 targets the next highest-risk unfinished seam: payment integrity can be made to look separate from claim security. It is not separate. A denied or delayed service, a ghost-network access failure, and a later payment-recovery finding all have to be joined to the same contract-year/request/payment row before the Social Security/Medicare case can be certified.

## Substantive finding

No MA row can pass from aggregate rate announcements, rebates, supplemental-benefit availability, quality bonuses, risk scores, ratebooks, bid data, or RADV authority alone. The certifying row must show claim security and payment integrity together: denial/access/remedy plus diagnosis-source validity, coding-intensity context, RADV recovery, bid/rebate value and use, Part B premium/taxpayer incidence, and FFS counterfactual spending.

## Concrete changes

- Added sources S615-S620 and reused existing sources S580, S581, S588, and S589.
- Added ten noncertifying locator-bound evidence records, including two new `contradicts` records.
- Added a payment-integrity row contract for risk score, diagnosis-source/service-record linkage, HRA/chart-review flags, RADV recovery, ratebook benchmark, bid/rebate/supplemental-benefit value and use, premium/taxpayer incidence, FFS counterfactual, and denial/access/remedy linkage.
- Refactored current surfaces so the high-risk queue now asks for one combined MA claim-security/payment-integrity row rather than another aggregate public statistic.

## Certification status

The case remains **not certified current**. The next decisive object is one current contract-year/request/payment row satisfying the row contract.

## Validation

```text
PASSED: MA payment-integrity/rebate-value/risk-coding waterfall audit
PASSED: MA access-availability/ghost-network/claim-visibility bridge audit
PASSED: MA medical-necessity/clinical-remedy guardrails audit
PASSED: MA equity-disaggregation/beneficiary-experience bridge audit
PASSED: MA contractor/resident-harm/enforcement bridge audit
PASSED: MA appeal-burden public pilot audit
PASSED: MA row-contract workbench audit
PASSED: 0 live-surface issues
PASSED: 0 errors, 0 warnings
```
