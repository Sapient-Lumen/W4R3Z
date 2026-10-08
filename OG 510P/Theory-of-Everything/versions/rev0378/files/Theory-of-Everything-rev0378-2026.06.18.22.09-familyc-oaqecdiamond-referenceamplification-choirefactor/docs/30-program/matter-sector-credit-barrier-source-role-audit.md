# Matter-sector credit-barrier source-role audit

`rev0337` treats current observed-sector particle data as a burden surface, not as route support. This is a substance-side guard: a route cannot claim particle-spectrum, Higgs-sector, neutrino, flavor, or coupling recovery while ignoring current denominator sources, but those same sources cannot be spent as acquired candidate-native evidence.

## What changed

- `REF-0392` and `REF-0699` through `REF-0701` were added as current observed-sector denominator refs.
- The refs are attached to `PARTICLE-SPECTRUM-LEDGER.json`, `INTERACTION-COUPLING-LEDGER.json`, and `MASS-HIERARCHY-LEDGER.json`.
- `tools/observed_sector_matter_policy.py` checks all route-bearing matter rows for denominator refs, no evidence-unit overcredit, source-ref dedupe, route-ceiling compliance, and fit-versus-prediction barrier language.
- `FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json` and `tools/frontier_source_policy.py` now treat the refs as cross-route burden refs only.

## Non-promotion rule

Current PDG, Muon g-2, KATRIN, and Higgs rows make the observed matter target harder to satisfy. They do not prove any candidate, do not promote any route, and do not close Standard Model matter recovery.

## Refactor note

This revision avoids minting a route-specific policy for every matter-sector measurement. The observed-sector matter policy is intentionally one cross-route barrier over the three matter ledgers, because the risk is common: accommodated fit and current consistency can be mistaken for risky predictive surplus.
