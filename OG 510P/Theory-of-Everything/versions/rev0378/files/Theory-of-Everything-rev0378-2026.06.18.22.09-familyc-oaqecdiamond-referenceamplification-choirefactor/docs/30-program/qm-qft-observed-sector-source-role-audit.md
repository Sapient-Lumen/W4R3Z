# QM/QFT observed-sector source-role audit — rev0340

## Risk targeted

`OSR-QM-QFT` was still too easy to treat as background compatibility. Ordinary constants, precision QED/lepton records, gauge semantics, unitarity, Lorentz/CPT behavior, microcausality/local-QFT recovery, and low-energy scattering records could be borrowed as public vocabulary without a route-local denominator surface. That is an authority leak: compatibility with known QM/QFT can look like candidate-native evidence even when the route has not replayed the records from its own variables.

## Change

rev0340 adds `DF-0025-QM-QFT-GAUGE-OBSERVED-SECTOR-REPLAY`, `ED-0031-QM-QFT-GAUGE-OBSERVED-SECTOR-PRESSURE`, and `DX-0018-QM-QFT-GAUGE-OBSERVED-SECTOR-REPLAY` as explicit QM/QFT/gauge observed-sector pressure. `tools/qm_qft_observed_sector_policy.py` checks that `REF-0710` and `REF-0711` live on route-local quantization, gauge, unitarity, Lorentz, microcausality, local-QFT, and scattering rows, not on acquired evidence-unit source credit.

## Non-promotion rule

These records are denominators. They may preserve current corridor language after successful replay, or roll back quantum/gauge/local-QFT/scattering wording after failure. They do not promote any route, do not close observed-sector recovery, and do not count as ToE evidence.

## Files added or materially changed

- `tools/qm_qft_observed_sector_policy.py`
- `docs/30-program/qm-qft-observed-sector-source-role-audit.generated.md`
- `DISCRIMINATOR-FORECAST-LEDGER.json`
- `EMPIRICAL-DELTA-LEDGER.json`
- `DECISION-EXPERIMENT-LEDGER.json`
- `OBSERVED-SECTOR-RECOVERY-LEDGER.json`
- quantization, gauge, unitarity, Lorentz, microcausality, local-QFT, and scattering ledgers
- `FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json`
- `tools/frontier_source_policy.py`

## Release identity

Bundle: `Theory-of-Everything-rev0340-2026.06.05.18.30-qm-qft-observed-sector-source-role-audit.zip`
