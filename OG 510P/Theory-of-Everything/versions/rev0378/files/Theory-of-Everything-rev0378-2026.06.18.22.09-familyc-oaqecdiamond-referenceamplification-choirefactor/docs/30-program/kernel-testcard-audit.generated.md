# Kernel testcard audit (generated)

Generated from `KERNEL-TESTCARD.json`, `CANDIDATE-ROUTE-STATE-LEDGER.json`, and `RELEASE-MANIFEST.json`. Do not edit directly; run `make index` after changing route rows or the positive testcard.

- Revision: `rev0378`
- Route rows checked: `13`
- Testcard rows: `13`
- Missing routes: `0`
- Extra routes: `0`
- Owned executable result rows: `1`
- Validation failures: `0`

## Compact route coverage

| Route | Cap | Discriminator count | Owned executable | Dominant debt present | Next work present |
|---|---:|---:|---:|---:|---:|
| `R-OQ0057-FAMILYC-EW-CODE` | `S3` | `3` | `true` | `true` | `true` |
| `R-OQ0057-FAMILYC-LEARNED-INVERSE` | `S2` | `3` | `false` | `true` | `true` |
| `R-OQ0057-FAMILYB-THERMO-ENTROPIC` | `S1` | `3` | `false` | `true` | `true` |
| `R-OQ0057-STRINGM-ATLAS` | `S2` | `3` | `false` | `true` | `true` |
| `R-OQ0057-ASYMPTOTIC-SAFETY` | `S2` | `3` | `false` | `true` | `true` |
| `R-OQ0057-CAUSAL-SET` | `S1` | `3` | `false` | `true` | `true` |
| `R-OQ0057-AMPLITUDES-BOOTSTRAP` | `S2` | `3` | `false` | `true` | `true` |
| `R-OQ0057-LAB-GIE-BMV` | `S2` | `3` | `false` | `true` | `true` |
| `R-OQ0057-GW-STRONGFIELD-GR` | `S2` | `3` | `false` | `true` | `true` |
| `R-OQ0057-FRAME-QRF-RELATIONAL` | `S2` | `3` | `false` | `true` | `true` |
| `R-OQ0057-LAB-GRAVITON-COUNTING` | `S2` | `3` | `false` | `true` | `true` |
| `R-OQ0057-COSMO-DARK-ENERGY-BAO` | `S2` | `3` | `false` | `true` | `true` |
| `R-OQ0057-PRIMORDIAL-TENSOR-BMODES` | `S2` | `3` | `false` | `true` | `true` |

## Rule

The positive kernel testcard is a compression target, not a promotion mechanism. A row is valid only when it covers an existing route, names at least three discriminator observables, and keeps its testcard cap at or below the route's current authority state and promotion ceiling.
