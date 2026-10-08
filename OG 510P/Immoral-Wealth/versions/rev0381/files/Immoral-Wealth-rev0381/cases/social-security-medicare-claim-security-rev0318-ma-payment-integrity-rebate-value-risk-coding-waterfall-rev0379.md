---
revision_current: rev0379
generated_at: 2026-06-18T21:36:00Z
title: MA payment-integrity, rebate-value, risk-coding, and public-cost waterfall
status: not_certified_current
---

# MA payment-integrity, rebate-value, risk-coding, and public-cost waterfall — rev0379

Rev0379 closes a payment-side false-completion seam. A Medicare Advantage row can prove denial, appeal, network access, medical necessity, and restoration and still be incomplete if the same contract-year cannot explain how the plan was paid, whether diagnoses were supported and linked to care, whether RADV recovered unsupported payment, whether rebates produced realized beneficiary value, and who bore the public cost.

## Required row contract

At least one current MA contract-year/request/payment row must join denial/access/remedy fields with risk score, diagnosis-source/service-record linkage, HRA/chart-review flags, RADV audit/recovery status, county benchmark/ratebook, bid/rebate/supplemental-benefit value and use, Part B premium/taxpayer incidence, and FFS counterfactual spending before certification.

## False-pass blocks

- No rebate-value pass: rebate or supplemental-benefit availability is not proof of realized beneficiary value or offsetting care denial.
- No risk-score pass: risk-adjusted payment does not prove diagnosis validity, care follow-up, or medical-record support.
- No HRA/chart-review pass: HRA-only, chart-review-only, or unlinked-CRR diagnoses must preserve service-record linkage before payment accuracy claims.
- No ratebook pass: benchmark/ratebook/base-rate context is not a contract-level claim-security outcome.
- No bid pass: plan bid and rebate assumptions are pricing inputs, not observed care or remedy.
- No RADV-existence pass: RADV authority or audited-contract publication does not prove recovery for the claim row under review.
- No rate-announcement pass: aggregate CMS payment updates cannot certify taxpayer neutrality or beneficiary claim security.
- No QBP/Star pass: quality bonuses and Stars do not substitute for denial correctness, active access, or remedy effectuation.
- No encounter-completeness pass: incomplete or unlinked encounter/payment data cannot prove both overpayment recovery and denied-care restoration.
- No public-cost pass: the row must allocate public cost to taxpayers, Part B premium payers, beneficiaries, and plans before certification.

## Source ids

New sources: S615, S616, S617, S618, S619, S620. Reused existing sources: S580, S581, S588, S589.

Certification remains **not certified current**. This revision makes the required certifying row more concrete; it does not supply that row.
