---
status: active_bridge
claim_kind: program_protocol
route_role: intergenerational_transfer_core
canonical_anchor: false
route_refs:
- intergenerational_transfer_core
- case_calibration_core
supersedes: null
depends_on:
- verdict-engine-and-certification-gates.md
- scoreboard-schema.json
source_refresh_due: 2026-12-31
case_pressure: rev0317_intergenerational_transfer
---

# Medicaid estate recovery and long-term-care home-equity router

Use this router when late-life care, Medicaid LTSS, HCBS, nursing-facility care, or estate recovery affects modest home equity.

## Diagnostic sequence

1. Identify whether care costs force spenddown before eligibility.
2. Identify whether estate recovery applies after age 55, institutionalization, HCBS, related hospital/prescription services, or broader state-chosen services.[S332][S334]
3. Determine whether the claim reaches probate estate only or expanded estate interests.
4. Check notice quality before care election and at death.
5. Check hardship waivers, caregiver-child protections, surviving spouse/disabled-child protections, and sibling equity protections.[S333]
6. Check interaction with heirs property and title documentation.
7. Compare treatment of modest home equity with high-end trust/planning avoidance.

## Routing choices

- **Narrow scope:** recover only federally required categories.
- **Hardship protection:** automatic or assisted waivers for low-income heirs and caregiver residents.
- **Home-equity bridge:** protect modest primary-residence equity where it is the main intergenerational foothold.
- **Notice and planning equity:** provide clear, early notice and legal aid before care decisions.
- **Data:** publish recovery claims, collections, waivers, demographics, home loss, and administrative costs.

## Certification rule

Do not count Medicaid LTSS as a clean public floor if the program's financing architecture converts low-income home equity into estate claims while wealthier households avoid spenddown through private insurance, trusts, gifting, or exempt planning.
