---
status: active
claim_kind: audit_report
route_role: workplace_power_core
route_refs:
- workplace_power_core
- enforcement_remedy_core
- source_governance_core
- case_calibration_core
revision_current: rev0355
source_refresh_due: 2026-12-31
---

# Workplace-power current-law hardening and seedclass refactor — rev0355

Generated: `2026-06-13T03:41:50Z`  
Codename: `workplace-power-current-law-hardening-and-seedclass-refactor`

## Priority judgment

With seed scoreboards closed in rev0332, the next highest-risk failure was not a missing case; it was active scoreboards that still carried seed calibration labels. Gate 14 workplace power was the riskiest subset because the legal perimeter is volatile: noncompete, joint-employer, independent-contractor, platform-work, union-remedy, and employee-ownership evidence can change the verdict quickly.

## Cases hardened

1. `united-states-union-density-wealth-formation-rev0312` — now blocks comfort scoring until private-sector bargaining coverage, first-contract conversion, remedy collection, and worker-voice evidence are visible. [S220] [S221] [S237]
2. `united-states-noncompete-worker-mobility-rev0312` — now treats FTC rule vacatur/abandonment as a live current-law blocker and shifts proof to state law, de facto restraints, and enforcement outcomes. [S225] [S226] [S232] [S233]
3. `united-states-fissured-workplace-joint-employer-rev0312` — now separates contractor classification, joint-employer liability, and lead-firm control/responsibility alignment. [S222] [S223] [S224] [S227] [S228]
4. `eu-platform-work-employment-presumption-rev0312` — now treats Directive transposition and enforcement as the operative threshold, not the Directive text alone. [S229]
5. `employee-ownership-esop-wealth-formation-rev0312` — now treats employee ownership as claim design: breadth, materiality, liquidity, valuation, diversification, and governance voice. [S235] [S236]

## Audit/refactor result

- Seed scoreboards remain closed: 0.
- Active-memo/seed-scoreboard mismatches remain closed: 0.
- Five workplace-power scoreboards no longer use `workplace_power_gate_seed` as their calibration class.
- Remaining active seed-calibration labels are now inventoried in `reports/seed-calibration-class-audit-rev0333.json` rather than hidden.

## Substance-over-bureaucracy rule

No cases, sources, or schema fields were added. The forward movement is in the active scoreboards: current-law notes, sourced evidence-debt rows, stricter certification gates, source-refresh/currentness rows, and case-memo hardening notes.

<!-- current_revision: rev0333; codename: workplace-power-current-law-hardening-and-seedclass-refactor -->
