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
case_pressure: rev0308_canada_top_tail_measurement_case
---

# Canada top-tail measurement case — rev0355

## Verdict

**Verdict:** `proof_debt` as a measurement subsystem case.  
**Mode:** top-tail audit and reconciliation.  
**Dominant breach:** survey-only wealth concentration is materially lower than top-tail-adjusted estimates.  
**Fastest washout:** false comfort from unadjusted survey shares that understate high-net-worth control.

## Why this case was added

Canada already appears in the portfolio as a rich asset democracy with housing and regional pressures. rev0308 adds a narrower measurement case because Canada now supplies a clean demonstration of the cube's new rule: a country can have high-quality statistical institutions and still require top-tail correction before moral certification.

The Parliamentary Budget Officer's 2025 update reports that its High-net-worth Family Database estimate gives the top 1% a much larger share of net wealth than unadjusted Survey of Financial Security data.[S146] Statistics Canada's distributional-account work also shows an active move toward combining surveys, tax data, and capitalization methods rather than relying on one source family.[S144][S145]

## Gate readings

| Gate | Reading | Reason |
|---|---|---|
| Share plausibility | warning | top-tail adjusted estimates materially change concentration reading |
| Measurement uncertainty | blocked for comfort pass | unadjusted survey shares cannot certify the top tail |
| Ownership visibility | watch | the case still needs private-business, trust, and offshore-control reconciliation |
| Floor and liability | not rescored | inherited from Canada country case; this memo targets measurement |

## Proof debt

1. Reconcile SFS, DHEA, tax-capitalized, and HFD estimates in one table.
2. State top 1%, top 0.1%, and top 0.01% ranges under low/central/high assumptions.
3. Separate housing, pensions, deposits, public equities, private business equity, and other financial assets.
4. Add person-level and group readings where possible.
5. Document whether trusts, private corporations, and offshore holdings are captured.

## Opening package

- Lead with top-tail reconciliation before claiming any Canadian share verdict.
- Treat survey-only top shares as lower-bound clues, not certification values.
- Use the Canada case as the template for any rich-democracy case where top-tail adjustment shifts the verdict.


## Rev0344 source-use burn-down note

Rev0344 binds formerly unused direct/context sources into this active case so the source ledger no longer carries high-value evidence outside the case/evidence/currentness lineage: [S160] [S161]. These bindings do not relax the verdict; they clarify which measurement, authority, or context burden the source supports.
