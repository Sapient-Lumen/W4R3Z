---
status: active
claim_kind: audit_report
route_role: public_balance_sheet_core
route_refs:
- public_balance_sheet_core
- source_governance_core
- case_calibration_core
revision_current: rev0355
source_refresh_due: 2026-12-31
---

# Sovereign/public-fiscal status-parity burndown — rev0355

Generated: `2026-06-13T01:08:27Z`  
Codename: `sovereign-fiscal-contingent-liability-and-public-asset-burndown`

## Priority judgment

The riskiest unfinished queue after rev0328 was the public-fiscal/sovereign-backstop cluster. These cases were already active memos, but their scoreboards remained seed. That made the cube vulnerable to treating large public claims, contingent liabilities, sovereign assets, and aging repair as doctrine rather than operational scoreboards.

## Cases promoted from seed scoreboard to active scoreboard

1. **China local-government/property/state-capital risk** — active loss-allocation case for property adjustment, LGFV restructuring, loss recognition, local-service exposure, bank spillovers, and central-local burden sharing. [S383] [S384]
2. **Japan/Korea aging pension-care fiscal risk** — active claim-security case for pensions, health, long-term care, family-care burden, contribution repair, and intergenerational/gender incidence. [S385] [S386] [S387] [S388] [S389]
3. **Norway GPFG public-asset governance** — active positive benchmark with stress conditions: fiscal-rule transfer, drawdown risk, ordinary-claimant linkage, raiding firewall, and intergenerational allocation. [S369] [S370] [S371] [S456]
4. **PPP/SOE/legal-judgment contingent liabilities** — active fiscal-risk-register case for guarantees, availability payments, termination payments, disasters, judgments, arrears, risk transfer, and public-upside recovery. [S350] [S381] [S382] [S457]
5. **U.S. state/local public-pension risk** — active public claim-security case using state/local pension data and return-assumption anchors; PBGC is retained as context, not the main proof surface. [S347] [S353] [S354] [S355] [S356] [S454] [S455]

## Audit/refactor result

The state/local pension case had a source-fit problem: PBGC sources were useful pension-backstop context but were not the right primary evidence for state/local pension assets, membership, benefit payments, and return assumptions. rev0329 adds Census ASPP and NASRA assumption sources, then marks PBGC as comparative context.

Remaining active-memo/seed-scoreboard mismatches after this pass: **16**. The remaining queue is now overwhelmingly household claim-security and remedy machinery rather than public-fiscal backstops.

## Substance-over-bureaucracy rule

No new cases and no new schema fields were added. Four sources were added only to repair source fit and currentness burden. The work is in active scoreboards, evidence debt, public-balance-sheet registers, seniority waterfalls, and validator locks.

<!-- current_revision: rev0329; codename: sovereign-fiscal-contingent-liability-and-public-asset-burndown -->
