---
status: active
claim_kind: revision_report
route_role: place_public_finance_core
route_refs:
- place_public_finance_core
- source_governance_core
- certification_core
revision_current: rev0355
source_refresh_due: 2026-12-31
---

# rev0335 place-public-finance service-floor hardening and source-fit refactor

Generated: `2026-06-13T05:08:26Z`  
Codename: `place-public-finance-service-floor-hardening-and-sourcefit-refactor`

## Why this was next

After rev0334, 20 active scoreboards still carried seed calibration labels. Gate 15 was the next priority because local public services are where nominal wealth claims become real or fail: school quality, water, electricity, transport access, municipal infrastructure, disaster recovery, taxes, fees, and service continuity.

## Cases hardened

- `united-states-school-finance-property-tax-rev0313`
- `united-states-municipal-infrastructure-fiscal-capacity-rev0313`
- `united-states-utility-burden-disconnection-rev0313`
- `local-disaster-fiscal-capacity-rev0313`
- `transportation-access-and-place-affordability-rev0313`

## Substantive changes

The school-finance case now uses current Census school-system finance data as an operative anchor and requires district-level cost adjustment, property-tax dependence, facilities, subgroup exposure, and post-relief fiscal-cliff evidence.[S466]

The municipal infrastructure case now separates direct official EPA water/wastewater need evidence from NLC/ASCE fiscal-condition context. Association summaries no longer carry operative authority.[S245][S246][S247][S248][S249][S258]

The utility case now treats residential disconnections as essential-service interruption evidence. EIA final-notice, disconnection, reconnection, customer-coverage, and response-rate data must be read with energy burden, water assistance, and shutoff-protection evidence.[S250][S251][S252][S253]

The disaster-fiscal case now separates FEMA operating-bridge and Public Assistance rails from actual conversion. Disaster aid availability does not prove local liquidity, reimbursement speed, match capacity, or equitable recovery incidence.[S256][S468]

The transportation case now adds BTS transportation-cost burden as an official household-cost anchor. Cheap housing cannot pass if the household must buy expensive or unreliable mobility to reach work, school, care, food, courts, or health care.[S254][S255][S259][S467]

## Refactor

S245 and S246 were relabeled from official/direct to association-research/context. S257 was relabeled from official/direct to think-tank/context. The cube can still use them, but cannot treat them as government operative authority.

Remaining active seed-calibration labels after this pass: 15.

<!-- current_revision: rev0335; codename: place-public-finance-service-floor-hardening-and-sourcefit-refactor -->
