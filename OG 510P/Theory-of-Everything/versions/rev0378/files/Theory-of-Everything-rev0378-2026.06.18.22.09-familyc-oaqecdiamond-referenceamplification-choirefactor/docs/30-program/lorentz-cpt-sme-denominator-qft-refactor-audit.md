# Lorentz/CPT/SME denominator and QFT policy refactor audit (rev0342)

## Decision

`rev0342` treats current Lorentz/CPT/SME public records as observed-sector denominator pressure, not as candidate-native evidence and not as route promotion. The repair is implemented by extending the existing QM/QFT observed-sector policy rather than minting a parallel policy surface.

## Why this was risky

The cube already carried Lorentz covariance, CPT/discrete symmetry, microcausality, local-QFT, and QFT denominator rows. The remaining risk was source-role ambiguity: null tests, SME coefficient tables, precision spectroscopy, meson-sector CPT bounds, and photon-propagation constraints could be read as generic freshness or broad support rather than route-local burden. That is especially dangerous for routes that use modified dispersion, emergent spacetime, nonlocal reconstruction, preferred-frame language, antimatter/flavour language, or quantum-gravity relic language.

## Change

- Added `DF-0027-LORENTZ-CPT-SME-OBSERVED-SECTOR-REPLAY`.
- Added `ED-0033-LORENTZ-CPT-SME-OBSERVED-SECTOR-PRESSURE`.
- Added `DX-0020-LORENTZ-CPT-SME-OBSERVED-SECTOR-REPLAY`.
- Reused existing `REF-0509` for SME Data Tables and added `REF-0715` through `REF-0718` as Lorentz/CPT/SME denominator refs.
- Attached those refs to route-specific Lorentz-covariance, CPT/discrete-symmetry, and microcausality/locality rows.
- Kept those refs out of metadata-wrapper and acquired evidence-unit `source_refs`.
- Extended `tools/qm_qft_observed_sector_policy.py`; no new policy file was introduced.
- Added `FSF-0030-LORENTZ-CPT-SME-SOURCE-ROLE` and frontier-source isolation entries for the new refs.

## Non-promotion boundary

Passing the SME/Lorentz/CPT denominator only preserves compatibility wording. It does not show that a route derives Lorentz symmetry, proves CPT, closes locality, detects quantum gravity, or recovers the Standard Model. Failure is likewise regime-local unless the route made the claim global.

## Refactor note

This revision is intentionally a consolidation: the existing QM/QFT policy now owns constants/QED pressure and Lorentz/CPT/SME pressure. That prevents policy sprawl while making the risk executable.
