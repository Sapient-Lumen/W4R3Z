---
status: active_doctrine
claim_kind: certification_gate
route_role: certification_core
canonical_anchor: true
route_refs:
- certification_core
- policy_pathway_core
supersedes: null
depends_on:
- verdict-engine-and-certification-gates.md
- scoreboard-schema.json
- ../10-framework/claim-conversion-and-delivery-rails.md
source_refresh_due: 2026-11-30
case_pressure: rev0307_conversion_case_layer
---

# Conversion rail certification gate

rev0307 adds a ninth certification gate: **conversion rails**. This gate asks whether paper claims become usable claimant-controlled wealth at the moment they are needed.

A case cannot receive `acceptable` or `near_ideal` certification by pointing to a benefit, account, credit, dividend, social fund, housing right, disaster program, inheritance rule, or tax credit unless the conversion route also passes.

## Gate question

> Can the intended person find, claim, receive, retain, and use the wealth claim without expert help, family rescue, avoidable fees, discretionary gatekeepers, or exclusionary documentation?

## Required screens

### 1. Take-up and awareness

Record take-up, non-take-up, and outreach. Where the exact rate is missing, use evidence debt rather than assuming full use. EITC participation and social-protection modernization sources are good U.S. and OECD examples of why eligibility is not receipt.[S122][S123][S139]

### 2. Documentation and identity

Score civil registration, legal identity, address proof, household proof, disability/care proof, immigration/citizenship proof, title proof, and name-matching. Use ID4D and UNICEF-style identity data where direct program data are absent.[S124][S125]

### 3. Payment rail

Score safe account, mobile wallet, card, cash-out, bank, postal, or assisted-payment access. Use Findex, FDIC, G2Px, and local payment-rail sources where relevant.[S120][S263][S126][S135][S136]

### 4. Timeliness

Score whether the payment arrives before the threshold moment fails. A claim that arrives after eviction, default, medical debt, repair loss, or school exclusion is not equivalent to a live asset.

### 5. Leakage and protection

Score fees, offsets, garnishment, clawbacks, account penalties, and paid intermediary extraction. Use CFPB/FDIC-style evidence for fee leakage where relevant.[S263][S262][S129]

### 6. Renewal stability

Score recertification, periodic review, proof churn, app/portal changes, lost passwords, notice failures, and benefit interruption. Paperwork churn can convert a floor into a recurring cliff.[S140]

### 7. Appeal and error correction

Score whether claimants can contest denial, mismatch, fraud flag, identity error, benefit calculation, account lock, or title problem without lawyers, fees, or long delays.

### 8. Person-level control

Score whether the intended person can control the claim. Household delivery, custodial accounts, spousal accounts, guardian accounts, institutional accounts, or landlord-mediated benefits require extra scrutiny.

## Gate statuses

- `passed`: direct evidence shows high take-up, low friction, safe rails, low leakage, renewal stability, and person-level control.
- `watch`: claim conversion is mostly functional, but one subgroup, rail, fee, or renewal issue needs monitoring.
- `blocked`: claims exist but major eligible populations cannot reliably convert them.
- `missing`: conversion data are absent; this blocks comfort when the case relies on the claim for certification.
- `open`: not central to the case but should be checked if the case later relies on public/common claims.

## Verdict effects

A blocked conversion gate can downgrade:

- `near_ideal` to `acceptable_but_vulnerable` when the issue is narrow and reparable;
- `acceptable` to `correction_required` when the failed claim is central to the floor or threshold moments;
- `correction_required` to `emergency_repair` when failed conversion produces eviction, hunger, medical debt, default, lost title, or disaster non-repair at scale.

## JSON fields

rev0307 adds explicit scoreboard fields for:

- `claim_conversion_friction`;
- `legal_identity_documentation_access`;
- `bank_account_payment_rail_access`;
- `benefit_take_up_gap`;
- `intermediation_fee_leakage`;
- `title_probate_finality`;
- `starter_asset_claim_finality`;
- `digital_public_infrastructure_exclusion`;
- `auto_enrollment_and_renewal_stability`;
- `offset_clawback_or_seizure_risk`;
- `appeal_and_error_correction_access`;
- `offline_multichannel_access`.

These fields are not a new index. They tell the operator whether a promised asset is real enough to count.
