# Policy-action audit report — rev0290

Policy-action profiles: 154

## Purpose

Rev0290 audits whether the cube can distinguish an instrument label from the policy action it is allowed to perform. The audit blocks fee-tax laundering, priced permission for non-compensable harm, mandate-disguised-as-tax errors, public-option erasure, and compensation-to-remitter errors.

## Action-family counts

- administrative_access_or_contest: 2
- classification_review_or_safe_harbor: 51
- information_reporting_or_recordkeeping: 3
- mandate_standard_or_duty: 8
- penalty_liability_or_enforcement: 19
- prohibition_no_go_or_veto: 3
- public_option_or_fallback_channel: 23
- rebate_credit_or_compensation: 18
- risk_prefunding_or_insurance_pool: 10
- source_release_integrity: 4
- subsidy_procurement_or_public_upside: 5
- tax_revenue_or_rent_capture: 7
- user_fee_or_service_charge: 1

## Specific audit findings

- Every cube route record has one policy-action profile.
- Every policy-action profile points back to a remedy profile for the same route.
- Fee-primary profiles require a benefit/cost/special-benefit nexus statement.
- Source-currentness refs are mirrored into the policy-action profile when present.
- The new instrument-choice route is explicitly classified as a classification/safe-harbor review action rather than a fee or tax merely because those labels appear in the instrument axis.

## Fee-primary route sample

- `informal_economy_presumptive_tax`
