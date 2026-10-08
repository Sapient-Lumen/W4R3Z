---
status: active_bridge
claim_kind: operator_matrix
route_role: certification_core
canonical_anchor: false
route_refs:
- certification_core
- policy_pathway_core
supersedes: null
depends_on:
- health-care-disability-and-care-interruption.md
- liability-stack-scorecard-and-router.md
source_refresh_due: 2026-12-31
case_pressure: rev0306_life_interruption
---

# Life-interruption claims matrix

## Purpose

This matrix connects interruption moments to the claims that must survive them. It is designed for case memos, not abstract doctrine.

| Interruption | Claim that must survive | False pass | Evidence to request |
|---|---|---|---|
| illness or medical bill | care without debt spiral | insurance coverage alone | skipped care, out-of-pocket costs, medical debt, collections |
| disability onset | income, care, accessible housing, assets | disability benefit exists on paper | benefit delay, earnings penalty, extra costs, asset tests |
| childbirth or caregiving | income, job, savings, pension accrual | unpaid family care treated as free | leave coverage, care costs, pension credits, gender split |
| job loss | liquid buffer and benefits before forced sale | unemployment rate only | cash buffer, benefit delay, debt service, evictions |
| divorce/separation | person-level title, account, housing, legal aid | household wealth counted as shared | legal aid, title, account access, housing exit data |
| migration/relocation | portable claim and deposit support | benefits exist only in old place | portability, waiting-list reset, credential transfer |
| criminal-legal contact | civic status and earning capacity | fine amount only | fees, warrants, licenses, record clearing, subgroup data |
| climate/repair shock | habitable asset without forced debt | pre-shock home equity | premiums, deductibles, nonrenewal, repair grants |

## Pass rule

The claim must be usable **before** the interruption becomes irreversible. A later appeal, reimbursement, debt forgiveness, or lawsuit does not pass if the person lost housing, care, transport, employment, safe exit, or savings continuity in the meantime.

## Routing rule

If the interruption is predictable and common, it belongs in the baseline floor. If it is rare but catastrophic, it belongs in shock-survival and insurance design. If it is concentrated in a subordinated group, it belongs in anti-averaging and person-level vetoes.[S104][S112][S113]
