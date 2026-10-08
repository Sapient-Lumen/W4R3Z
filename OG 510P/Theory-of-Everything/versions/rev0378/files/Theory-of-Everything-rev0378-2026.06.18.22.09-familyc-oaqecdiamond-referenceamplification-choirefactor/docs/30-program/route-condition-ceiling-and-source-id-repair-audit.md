# Route-condition ceiling and source-ID repair audit

Revision: `rev0325`

## Why this was risky

Two different source-pressure batches briefly tried to occupy the same local reference IDs. The learned-inverse batch used `REF-0131`/`REF-0143` plus `REF-0670` through `REF-0672`; the FamilyB thermodynamic and causal-set pressure batch also used the same identifiers. That is a real provenance failure: a single `REF-*` handle must not mean different papers in different route contexts.

This revision partitions the source namespace explicitly:

- `REF-0131`/`REF-0143` plus `REF-0670` through `REF-0672`: learned-inverse / holographic-ML / SciML / uncertainty-calibration pressure.
- `REF-0163`, `REF-0666`, and `REF-0667`: FamilyB relative-entropy, semiclassical-thermodynamic, and non-Riemannian Jacobson-scope pressure.
- `REF-0668` through `REF-0669`: causal-set continuum-emergence and discrete-horizon diagnostic pressure.

The frontier-source isolation and freshness audits now enforce the split.

## Route-condition ceiling repair

A second risky seam was route-local support rows advertising authority higher than their route promotion ceilings. This revision adds `tools/route_condition_ceiling_policy.py` and generated audit `docs/30-program/route-condition-ceiling-audit.generated.md`. The rule is simple: if a row names exactly one route, its `maximum_authority_effect`, `maximum_credit`, `current_maximum_credit`, or `promotion_ceiling` may not exceed that route's own `promotion_ceiling`.

The executable audit checks single-route rows and intentionally leaves multi-route rows outside this rule until those rows are split or given per-route authority fields.

## Non-promotion rule

These repairs are control-plane hygiene and source-role discipline. They prevent overcredit and source bleed, but they add no new candidate authority and promote no route.
