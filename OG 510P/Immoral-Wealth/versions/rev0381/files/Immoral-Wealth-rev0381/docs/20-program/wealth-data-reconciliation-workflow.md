---
status: active_protocol
claim_kind: measurement_workflow
route_role: measurement_uncertainty_core
canonical_anchor: false
route_refs:
- measurement_uncertainty_core
- case_calibration_core
supersedes: null
depends_on:
- measurement-source-quality-ladder.md
- top-tail-audit-and-uncertainty-bounds.md
source_refresh_due: 2026-12-31
---

# Wealth data reconciliation workflow

The reconciliation workflow converts conflicting data into a case verdict without pretending the conflict has disappeared.

## Workflow

1. **Inventory measures.** List the source family, unit, year, population, geography, household/person definition, asset perimeter, liability perimeter, and treatment of pensions/public claims.
2. **Map to the archive perimeter.** Convert each estimate into the closest archive concept: private net wealth, usable person-level floor, public/social counterweight, title-final asset, or control claim.
3. **Reconcile totals.** Compare micro totals with national accounts where possible. OECD distributional household wealth work is now the benchmark for macro-consistent experimental comparison.[S142][S143]
4. **Audit the top tail.** Check whether the rich, private business wealth, financial assets, offshore claims, trusts, and legal entities are captured.[S141][S146][S151][S160]
5. **Audit the bottom and liabilities.** Check whether negative wealth, informal debt, medical/student/criminal-legal debt, collections, and title defects are captured.
6. **Separate liquidity/control.** Do not treat home equity, locked pensions, business equity, illiquid private funds, and deposits as fungible.
7. **Produce a moral interval.** State the low/central/high readings and whether the verdict changes.
8. **Assign proof debt.** If a gate depends on unresolved data, state exactly what evidence would change the verdict.

## Reconciliation outputs

Every full country case should now include:

```json
{
  "source_family": "survey_plus_top_tail_adjustment",
  "measurement_uncertainty_band": "material",
  "top_tail_audit_status": "required",
  "macro_micro_reconciliation": "partial",
  "ownership_visibility_status": "warning",
  "verdict_consequence": "no_soft_pass_from_point_estimate"
}
```

These values live as scoreboard fields, not as decorative prose. They tell the operator whether a wealth-share number can actually support certification.
