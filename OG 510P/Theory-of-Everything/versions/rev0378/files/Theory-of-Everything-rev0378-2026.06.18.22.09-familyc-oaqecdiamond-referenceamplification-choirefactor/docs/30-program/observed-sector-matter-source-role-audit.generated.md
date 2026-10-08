# Observed-sector matter source-role audit (generated)

Generated from particle-spectrum, interaction-coupling, mass-hierarchy, evidence-unit, observed-sector, and route-state ledgers. Do not edit directly; run `make index` after changing matter-sector denominator pressure.

- Current matter/QCD denominator refs: `REF-0392`, `REF-0699`, `REF-0700`, `REF-0701`, `REF-0712`, `REF-0713`, `REF-0714`, `REF-0719`, `REF-0720`, `REF-0721`, `REF-0722`, `REF-0723`, `REF-0724`
- QCD/hadronic denominator refs: `REF-0712`, `REF-0713`, `REF-0714`
- Electroweak/flavor/neutrino denominator refs: `REF-0719`, `REF-0720`, `REF-0721`, `REF-0722`, `REF-0723`, `REF-0724`
- Matter rows checked: `42`
- Route-bearing matter rows checked: `42`
- Standard-Model-obligation burden rows: `9`
- Denominator-only non-SM route rows: `30`
- Metadata wrapper rows capped at S0: `3`
- Matter-credit cap checks: `42`
- QCD/hadronic denominator route rows: `39`
- Electroweak/flavor/neutrino denominator route rows: `39`
- Observed-sector matter checks: `700`
- Observed-sector matter failures: `0`

## Ledger summary

| Ledger | Rows | Failures |
|---|---:|---:|
| `PARTICLE-SPECTRUM-LEDGER.json` | `14` | `0` |
| `INTERACTION-COUPLING-LEDGER.json` | `14` | `0` |
| `MASS-HIERARCHY-LEDGER.json` | `14` | `0` |

## Failure details

- None.

## Non-promotion rule

Current observed-particle, Higgs, muon, neutrino, QCD/hadronic, electroweak-precision, CKM/flavor, and neutrino-oscillation refs are denominator/burden refs. They make matter-sector, strong-coupling, confinement, hadron-spectrum, quark-mass, coupling, electroweak input-scheme, flavor/CKM, and neutrino-mass/mixing claims harder to spend; they do not supply acquired candidate-native evidence or promote any route. Routes without `OSR-STANDARD-MODEL-MATTER` carry explicit S0 observed-matter credit caps on these ledgers, and the explicit QCD and electroweak/flavor/neutrino pressure rows are capped at S0 for every route.

