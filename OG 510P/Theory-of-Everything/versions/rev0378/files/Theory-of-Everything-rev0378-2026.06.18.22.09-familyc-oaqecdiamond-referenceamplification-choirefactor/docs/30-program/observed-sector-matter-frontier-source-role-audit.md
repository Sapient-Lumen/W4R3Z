# Observed-sector matter frontier source-role audit

`rev0337` repairs a high-risk overcredit seam: current observed-sector particle, Higgs/coupling, muon-precision, and neutrino-mass sources can make the matter target harder, but they cannot be spent as evidence that any route has recovered the Standard Model.

## What changed

- Added `REF-0392` and `REF-0699` through `REF-0701` for PDG 2026, final Fermilab Muon g-2, KATRIN direct neutrino mass, and CMS Higgs 2025.
- Attached those refs to the route-bearing particle-spectrum, interaction-coupling, and mass-hierarchy ledgers, plus the Standard-Model-matter observed-sector obligation.
- Added `tools/observed_sector_matter_policy.py`, wired into generated-surface sync and archive lint.
- Blocked those refs from acquired evidence-unit `source_refs` and from metadata/provenance wrapper freshness.

## Why this is substantive

Matter-sector fit is one of the easiest places for a ToE-like archive to overclaim: a route can accommodate known particles, couplings, or masses and then narrate that accommodation as risky prediction. This revision makes current observed-sector sources a credit barrier. They must be faced before matter-sector recovery language is spent, but they do not themselves add candidate-native support.

## Non-promotion rule

No route is promoted. Current observed-sector matter refs are denominator pressure, not acquired evidence, not route identity, and not Standard Model closure.
