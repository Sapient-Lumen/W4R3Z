---
status: active_program
claim_kind: guardrail
route_role: place_public_finance_core
canonical_anchor: false
route_refs:
- place_public_finance_core
- floor_core
- liability_stack_core
- conversion_rail_core
supersedes: null
depends_on:
- ../10-framework/utility-affordability-disconnection-and-essential-service-claims.md
- liability-stack-scorecard-and-router.md
source_refresh_due: 2026-12-31
case_pressure: rev0313_place_public_finance
---

# Utility affordability and shutoff guardrails

Use this guardrail when energy, water, sewer, or telecommunications costs threaten the real floor. Utility debt is not merely monthly consumption; it can become collections, reconnection fees, unsafe housing, medical danger, missed work, and eviction pressure.[S250][S251][S252][S253]

## Minimum guardrails

1. Mandatory reporting of arrears, notices, disconnections, reconnections, and repeat shutoffs by utility and geography.
2. Percentage-of-income or affordability rates for low-income households.
3. Arrears management that does not turn old bills into permanent exclusion.
4. No shutoffs during extreme heat, cold, medical vulnerability, infancy, disability, or declared disasters.
5. Fast restoration and fee waivers for protected households.
6. Direct public payments and auto-enrollment where eligibility is known.
7. Water/sewer affordability assistance and capital grants to avoid rate shock.
8. Weatherization and efficiency investment targeted to high-burden households.[S250][S252][S253]

## Scoreboard reading

`utility_affordability_burden = fail` when a significant lower-income group must reduce food, medicine, safety, or care to maintain service. `utility_disconnection_protection = fail` when completed shutoffs are frequent, data are opaque, protections are narrow, or restoration is slow.[S251][S252]
