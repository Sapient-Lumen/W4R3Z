# Tax-administration-access accountability refactor — rev0293

This pass attacks the riskiest unfinished surface from the prior audit: tax-administration-access routes were structurally complete but still too generic to answer who benefits from a channel toll, delay, freeze, overcollection, preparer dependency, or record asymmetry.

## Scope

Family audited: `tax_administration_access`

Routes refactored: 17

Profiles remaining in this family with `beneficiary_or_rent_recipient_to_trace`: 0

Profiles remaining in this family with generic `benefit_or_rent_trace` evidence: 0

## What changed

Each route in the family now names:

- the primary accountable actor with route context, not just `revenue_agency_or_public_channel_owner`;
- the concrete beneficiary or rent recipient, such as a tax software partner, paid preparer, identity vendor, bank, wallet, processor, court collector, reporter, setoff recipient, escrow holder, or program fund;
- the actual bottleneck or channel actor controlling eligibility, records, disbursement, correction, fee capture, identity, appeal, or timing;
- protected burden bearers rather than only `ordinary_taxpayer` where the route’s floor risk is specific;
- route-specific evidence packets replacing the inherited generic evidence bundle.

## Route cluster findings

### Filing, refund, and mandatory private rails

`public_filing_refund_floor`, `mandatory_private_tax_rail_and_bankless_fallback`, and `compliance_cost_assisted_filing_and_preparer_dependence` now separate the public claim owner from the private access-rent beneficiary. A partner product, preparer, bank, wallet, software vendor, identity vendor, or payment processor may be useful, but it cannot be treated as neutral if it controls eligibility, refund destination, fee capture, correction, account freezes, or user exit.

Default repair: restore or preserve a no-rent public or assisted route, preserve timestamps, remove tolls, and reissue or release refunds through a channel that is not the failed rail.

### Service, explanation, appeal, and representation

`administration_explanation_and_appeal_minimum` and `taxpayer_service_ombuds_appeals_representation_floor` now route responsibility to the decision owner, service owner, appeals office, taxpayer advocate, identity unit, or representation floor depending on who controls notice, explanation, reversal authority, and case access.

Default repair: assign a case owner, give a specific explanation, open or restore appeal, and escalate to advocate or representation support when ordinary channels fail.

### Reporting, record asymmetry, and official error

`official_error_prefill_and_guidance_reliance`, `third_party_reporting_correction_and_bounded_recipient_shelter`, `record_asymmetry_burden_shifting_and_adverse_inference`, and `offshore_information_reporting_expanded` now focus on the actor controlling the source record. Recipient or taxpayer fault cannot be inferred merely because a mismatch exists.

Default repair: correct the source record, shelter reasonable reliance, propagate downstream correction, and shift proof toward the superior record holder when access is asymmetric.

### Remittance, collection, contest, setoff, timing, and escrow

`collection_anchor_choice_and_remittance_chain`, `bounded_contest_issue_scoped_correction_and_period_finality`, `overcollection_return_setoff_and_refund_symmetry`, `timing_cashflow_liquidity_deferral_and_prefunding`, `reinvestment_prefunding_ring_fence_and_retained_surplus`, and `provisional_controller_filing_escrow_and_true_up` now identify who controls money, period finality, setoff, escrow, release, true-up, and cashflow timing.

Default repair: assign responsibility to the actor with control of funds or records, protect the actual burden bearer’s credit or refund, and avoid punishing conduits or taxpayers who lack notice, access, or practical control.

## New release-fatal guard

`tools/audit_actor_accountability_profiles.py` now fails any tax-administration-access profile that keeps the old beneficiary placeholder, keeps `benefit_or_rent_trace` as generic evidence, lacks multiple route-specific responsibility bases, or erases the public fallback duty.

## What remains

This pass deliberately did not rewrite all 155 actor-accountability profiles. After this revision, 116 profiles outside the tax-administration-access family still carry the generic beneficiary placeholder, and 138 still use the generic evidence bundle. The next comparable high-value pass should probably target `controller_ai` or `public_finance_core`, not add a new registry layer.
