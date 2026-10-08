# Social-floor/public-service accountability refactor — rev0299

## Why this pass mattered

After rev0298, the largest remaining family with both beneficiary placeholders and generic benefit-trace evidence was `social_floor_public_services`. The risk was not merely cosmetic. These routes decide who bears essential-service fees, who captures exemption value, whether charity claims displace direct duties, how tribal fiscal sovereignty is respected, and whether mission-form surplus becomes visible service, member, worker, or local repair.

## What was specialized

Rev0299 rewrites all 8 social-floor/public-service actor-accountability profiles:

- `health_addiction_harmful_consumption_tax`
- `nonprofit_exemption_public_benefit`
- `user_fee_service_charge_utility_public_access_toll`
- `agriculture_food_support_nutrition_rural_floor`
- `municipal_bond_tax_exemption_public_infrastructure_finance`
- `tribal_indigenous_fiscal_sovereignty_tax_parity_consultation`
- `charitable_public_benefit_transfer_and_retained_surplus`
- `public_service_member_relief_and_local_repair`

Each profile now names the accountable actor, the benefit or rent recipient, the bottleneck or channel actor, protected burden bearers, non-responsible actors, default liability/remedy move, fallback public duty, route-specific evidence, and review triggers.

## Accountability clusters

### 1. Health harm, addiction, and treatment proceeds

The visible payer is often the consumer, but responsibility should track product design, potency, marketing, youth targeting, excise design, pass-through, and treatment/prevention proceeds. Addicted users, youth, patients, and floor households are protected burden bearers, not the primary revenue source.

### 2. Exemption, charity, and community benefit

Tax exemption and charitable-transfer claims are not self-proving. Responsibility follows the board, donor controller, foundation or DAF sponsor, related-party contract, payout ledger, retained-surplus record, and exemption authority. Rev0299 separates genuine public benefit from donor recapture, halo laundering, endowment lockup, and substitution against prior duties.

### 3. Essential fees and public-service access

A user fee or service charge is not morally ordinary just because a bill exists. The accountable actor is the utility, public body, regulator, billing vendor, or service provider controlling cost records, affordability, disconnection, reconnection, waiver, and appeal. Low-income users and ratepayers are not the default residual backstop.

### 4. Food, rural, and nutrition floors

Agriculture and nutrition support must separate producer, landowner, processor, input-supplier, retailer, small-farmer, food-consumer, and rural-household incidence. Subsidy capture and nutrition-floor failure now require recipient-size, pass-through, benefit-delivery, supply-shock, and rural-transition evidence.

### 5. Municipal finance and tribal fiscal sovereignty

Municipal-bond accountability follows official statements, private use, arbitrage, continuing disclosure, conduit records, debt service, and ratepayer/local taxpayer incidence. Tribal fiscal accountability follows government-to-government consultation, parity, compact/revenue-share records, general-welfare treatment, member access, and sovereignty-preserving nonreclassification.

## Cube-axis refactor

Two routes had the worst inherited cube templates:

- `charitable_public_benefit_transfer_and_retained_surplus` still looked like a generic low-income rebate route.
- `public_service_member_relief_and_local_repair` still looked like a generic essential-service access route.

Rev0299 gives them route-specific axes for retained surplus, donor control, charitable deduction, community benefit, member/rate relief, worker transition, local repair, service quality, reserves, affiliate/vendor extraction, and public-service access.

## Regression rule

`tools/audit_actor_accountability_profiles.py` now rejects any social-floor/public-service profile that keeps generic beneficiaries, generic benefit-trace evidence, public-channel-only bottlenecks, too-thin responsibility bases, or missing route-specific evidence for addiction, exemption, user fees, nutrition, municipal bonds, tribal consultation, charitable surplus, or member/local repair.
