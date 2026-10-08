---
status: active_case
claim_kind: case_memo
route_role: case_calibration_core
canonical_anchor: false
route_refs:
- case_calibration_core
- measurement_uncertainty_core
- certification_core
supersedes: null
depends_on:
- ../docs/20-program/top-tail-audit-and-uncertainty-bounds.md
- ../docs/20-program/measurement-source-quality-ladder.md
source_refresh_due: 2026-09-30
case_pressure: rev0308_macro_consistent_wealth_accounts_case
---

# Macro-consistent wealth accounts case — rev0355

## Verdict

**Verdict:** `provisional` as a cross-national measurement-infrastructure case.  
**Mode:** infrastructure building and comparability discipline.  
**Dominant breach:** many cases compare wealth shares that are not built on the same perimeter, totals, or source family.  
**Fastest washout:** cross-country moral comparisons become misleading when micro survey totals and macro balance sheets are not reconciled.

## Why this case was added

The archive now contains many country and subsystem cases. That makes comparability a live risk. OECD's 2025 experimental work on household wealth in line with national accounts shows one path toward macro-consistent distributional measurement, including evidence that wealth is concentrated in the top quintile, bottom quintiles can have negative wealth, and financial assets drive inequality while housing moderates it.[S142][S143]

This case is not about one country. It is about the measurement rail that lets country cases become comparable.

## Gate readings

| Gate | Reading | Reason |
|---|---|---|
| Source comparability | watch | experimental accounts improve comparability but need top-tail and asset-control checks |
| Share plausibility | watch | macro consistency helps totals but does not automatically solve hidden-control problems |
| Floor reality | watch | bottom-quintile negative wealth must be connected to liquidity, debt, and claimability screens |
| Top-tail audit | required | national accounts need distributional allocation and controller visibility |

## Proof debt

- Specify the wealth perimeter in each country case.
- Reconcile survey, tax, national accounts, and registry totals.
- Separate asset classes and liabilities.
- Add uncertainty intervals.
- Identify where country cases use non-comparable source families.

## Opening package

Use macro-consistent wealth accounts as a comparability rail, not as an automatic verdict engine. The rail helps prevent denominator and perimeter errors; it does not replace anti-averaging, top-tail audit, lower-half usable wealth, or ownership-control visibility.

## rev0325 refresh-sync note

The memo `source_refresh_due` now matches the paired scoreboard date of `2026-12-31`; validator enforcement prevents future memo/scoreboard refresh divergence.


## Rev0344 source-use burn-down note

Rev0344 binds formerly unused direct/context sources into this active case so the source ledger no longer carries high-value evidence outside the case/evidence/currentness lineage: [S01] [S03] [S151]. These bindings do not relax the verdict; they clarify which measurement, authority, or context burden the source supports.

## Rev0346 currentness note

Rev0346 shortens this measurement-infrastructure case to a quarterly refresh cadence because it now cites the June 11, 2026 Federal Reserve Z.1 current release. Z.1 supplies live aggregate household-balance-sheet totals; it does not by itself solve distributional allocation, source-family comparability, top-tail nonresponse, or hidden-control measurement debt.[S490]


## Rev0347 exact-DFA extraction note

Rev0347 uses the U.S. case as a worked example of the measurement rule: Z.1 supplies live aggregate household-balance-sheet totals, while the FRED/Federal Reserve DFA release table supplies distributional total-net-worth shares. The new extraction closes one current U.S. numeric gap, but the cross-national measurement case remains provisional because WID/DINA, survey, tax, registry, and national-account source families still need explicit perimeter labels and uncertainty intervals.[S490][S493][S142][S143]
