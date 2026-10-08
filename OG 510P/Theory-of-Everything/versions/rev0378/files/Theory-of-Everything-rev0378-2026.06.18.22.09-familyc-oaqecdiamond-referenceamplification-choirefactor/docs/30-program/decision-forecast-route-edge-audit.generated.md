# Decision / forecast route-edge audit (generated)

Generated from `CANDIDATE-ROUTE-STATE-LEDGER.json`, `DISCRIMINATOR-FORECAST-LEDGER.json`, `DECISION-EXPERIMENT-LEDGER.json`, and `AUTHORITY-DEPENDENCY-GRAPH.json`. Do not edit directly; run `make index` after changing route-facing decision surfaces.

- Route rows: `13`
- Forecast rows: `29`
- Decision experiments: `22`
- Routes lacking both route-facing forecast and decision rows: `0`
- S2-or-higher routes lacking route-facing forecast rows: `0`
- Routes lacking route-facing decision-experiment rows: `0`
- Edge/audit failures: `0`

| Route | Authority | Forecast rows | Decision experiments |
|---|---:|---:|---:|
| `R-OQ0057-FAMILYC-EW-CODE` | `S3` | `8` | `7` |
| `R-OQ0057-FAMILYC-LEARNED-INVERSE` | `S2` | `1` | `6` |
| `R-OQ0057-FAMILYB-THERMO-ENTROPIC` | `S1` | `2` | `6` |
| `R-OQ0057-STRINGM-ATLAS` | `S2` | `2` | `7` |
| `R-OQ0057-ASYMPTOTIC-SAFETY` | `S2` | `1` | `7` |
| `R-OQ0057-CAUSAL-SET` | `S1` | `2` | `6` |
| `R-OQ0057-AMPLITUDES-BOOTSTRAP` | `S2` | `2` | `6` |
| `R-OQ0057-LAB-GIE-BMV` | `S2` | `3` | `8` |
| `R-OQ0057-GW-STRONGFIELD-GR` | `S2` | `1` | `6` |
| `R-OQ0057-FRAME-QRF-RELATIONAL` | `S2` | `1` | `5` |
| `R-OQ0057-LAB-GRAVITON-COUNTING` | `S2` | `2` | `6` |
| `R-OQ0057-COSMO-DARK-ENERGY-BAO` | `S2` | `2` | `5` |
| `R-OQ0057-PRIMORDIAL-TENSOR-BMODES` | `S2` | `2` | `5` |

## Non-promotion rule

This audit forces route-facing decision and forecast pressure to remain connected to the authority graph. It does not promote a route; it prevents an S2-or-higher candidate lane from surviving as a decision-only or pure-narrative corridor after its forecast handles disappear.
