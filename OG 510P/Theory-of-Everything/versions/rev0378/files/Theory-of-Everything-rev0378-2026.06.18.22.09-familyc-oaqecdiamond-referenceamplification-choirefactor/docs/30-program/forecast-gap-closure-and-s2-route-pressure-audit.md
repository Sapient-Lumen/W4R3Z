# Forecast gap closure and S2 route-pressure audit

Revision: `rev0320`  
Bundle: `Theory-of-Everything-rev0320-2026.06.04.07.20-source-isolation-spt3g-bmode-pressure-audit.zip`

## Finding

Rev0319 made empirical deltas and decision experiments route-facing, but three S2 lanes still had no explicit discriminator forecast row. That left them as decision-only corridors: they could remain live without a concrete forecast artifact that later work could realize, miss, or roll back.

## Repair

Rev0320 adds three route-facing discriminator forecasts:

- `DF-0012-FAMILYC-LEARNED-INVERSE-OOD-PUBLIC-HOLDOUT` for `R-OQ0057-FAMILYC-LEARNED-INVERSE`.
- `DF-0013-DESI-DR2-COSMOLOGY-TENSION-SPLIT` for `R-OQ0057-COSMO-DARK-ENERGY-BAO`.
- `DF-0014-PRIMORDIAL-TENSOR-POST-CMBS4-REALIZATION` for `R-OQ0057-PRIMORDIAL-TENSOR-BMODES`.

The generated decision/forecast audit and archive lint now reject any S2-or-higher route that lacks a route-facing forecast row.

## Source-custody boundary

The DESI row is a public-likelihood / tension-splitting forecast, not an ontology claim. The CMB-S4 row is post-project-status forecast-realization custody, not a tensor null result. The learned-inverse row is an OOD/public-holdout benchmark pressure, not independent candidate identity.

## Cloudtainer refactor: authority graph hot path

The authority graph codec no longer deep-copies already-expanded logical graphs during replay validation. Compact graph inputs still expand into explicit edge rows; expanded inputs are now normalized by shallow mapping plus `edge_count`. This removes waste in the large generated proof-object hot path without weakening deterministic digest, source-replay, or compact-storage checks.

## Non-promotion rule

No route is promoted by these changes. Forecast rows create falsifiability and public-artifact pressure; they do not add scientific authority unless later public records satisfy the declared controls.
