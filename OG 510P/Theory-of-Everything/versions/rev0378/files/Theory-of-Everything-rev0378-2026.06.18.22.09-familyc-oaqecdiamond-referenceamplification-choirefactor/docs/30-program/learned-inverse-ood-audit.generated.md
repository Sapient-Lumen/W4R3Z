# Learned-inverse OOD / simulator-inheritance audit (generated)

Generated from the learned-inverse route, forecast, empirical-delta, decision-experiment, evidence-unit, and ML/control ledgers. Do not edit directly; run `make index` after changing learned-inverse OOD custody.

- Route checked: `R-OQ0057-FAMILYC-LEARNED-INVERSE`
- Required current refs: `REF-0131`, `REF-0143`, `REF-0670`, `REF-0671`, `REF-0672`
- Learned-inverse OOD checks: `45`
- Learned-inverse OOD failures: `0`

| Check | Passed | Detail |
|---|---:|---|
| `route-present` | `true` | route `R-OQ0057-FAMILYC-LEARNED-INVERSE` must exist |
| `route-current-state-capped` | `true` | current authority is `S2`; expected `S2` |
| `route-promotion-ceiling-capped` | `true` | promotion ceiling is `S2`; expected `S2` |
| `route-names-ood-denominators` | `true` | route text missing terms [] |
| `forecast-present` | `true` | forecast `DF-0012-FAMILYC-LEARNED-INVERSE-OOD-PUBLIC-HOLDOUT` must exist |
| `forecast-route-local` | `true` | forecast route is `R-OQ0057-FAMILYC-LEARNED-INVERSE` |
| `forecast-credit-capped` | `true` | forecast current maximum is `S2`; expected `S2` |
| `forecast-current-refs` | `true` | missing refs []; present ['REF-0131', 'REF-0142', 'REF-0143', 'REF-0148', 'REF-0670', 'REF-0671', 'REF-0672'] |
| `forecast-public-denominators` | `true` | forecast text missing terms [] |
| `forecast-non-promotion` | `true` | forecast must explicitly block promotion/ontology/identity spending |
| `delta-present` | `true` | delta `ED-0012-FAMILYC-LEARNED-INVERSE-OOD-CUTOFF-PRESSURE` must exist |
| `delta-route-local` | `true` | delta route_ids are `['R-OQ0057-FAMILYC-LEARNED-INVERSE']` |
| `delta-credit-capped` | `true` | delta promotion ceiling is `S2`; expected `S2` |
| `delta-current-refs` | `true` | missing refs []; present ['REF-0131', 'REF-0142', 'REF-0143', 'REF-0148', 'REF-0670', 'REF-0671', 'REF-0672'] |
| `delta-hard-denominators` | `true` | delta text missing terms [] |
| `decision-present` | `true` | decision experiment `DX-0014-FAMILYC-LEARNED-INVERSE-OOD-ABSTENTION` must exist |
| `decision-route-local` | `true` | decision route_ids are `['R-OQ0057-FAMILYC-LEARNED-INVERSE']` |
| `decision-current-refs` | `true` | missing refs []; present ['REF-0131', 'REF-0143', 'REF-0670', 'REF-0671', 'REF-0672'] |
| `decision-hooks-delta` | `true` | decision hooks ['ED-0012-FAMILYC-LEARNED-INVERSE-OOD-CUTOFF-PRESSURE'] |
| `decision-public-artifact-denominators` | `true` | decision artifact missing terms [] |
| `decision-non-promotion` | `true` | decision must bound positive and negative outcome authority |
| `evidence-present` | `true` | evidence unit `EU-0002-FAMILYC-LEARNED-INVERSE-BENCHMARK` must exist |
| `fresh-refs-not-acquired-evidence` | `true` | fresh refs incorrectly present on acquired evidence unit: [] |
| `evidence-credit-capped` | `true` | evidence maximum credit is `S2`; expected `S2` |
| `evidence-names-current-delta-handoff` | `true` | evidence empirical_delta_ids ['ED-0012-FAMILYC-LEARNED-INVERSE-OOD-CUTOFF-PRESSURE', 'ED-0032-QCD-HADRONIC-OBSERVED-SECTOR-PRESSURE', 'ED-0033-LORENTZ-CPT-SME-OBSERVED-SECTOR-PRESSURE', 'ED-0034-ELECTROWEAK-FLAVOR-NEUTRINO-OBSERVED-SECTOR-PRESSURE', 'ED-0035-EQUIVALENCE-FIFTH-FORCE-WEAKFIELD-OBSERVED-SECTOR-PRESSURE'] |
| `condition-row-present-GEN-0002-FAMILYC-LEARNED-INVERSE` | `true` | PREDICTIVE-GENERALIZATION-LEDGER.json:GEN-0002-FAMILYC-LEARNED-INVERSE |
| `condition-row-refs-GEN-0002-FAMILYC-LEARNED-INVERSE` | `true` | missing refs []; present ['REF-0263', 'REF-0264', 'REF-0265', 'REF-0266', 'REF-0236', 'REF-0268', 'REF-0670', 'REF-0671', 'REF-0672'] |
| `condition-row-present-SUR-0002-FAMILYC-LEARNED-INVERSE` | `true` | SURROGATE-EMULATOR-LEDGER.json:SUR-0002-FAMILYC-LEARNED-INVERSE |
| `condition-row-refs-SUR-0002-FAMILYC-LEARNED-INVERSE` | `true` | missing refs []; present ['REF-0581', 'REF-0583', 'REF-0584', 'REF-0587', 'REF-0131', 'REF-0143', 'REF-0670', 'REF-0671'] |
| `condition-row-present-SRT-0002-FAMILYC-LEARNED-INVERSE` | `true` | SIM-TO-REAL-TRANSFER-LEDGER.json:SRT-0002-FAMILYC-LEARNED-INVERSE |
| `condition-row-refs-SRT-0002-FAMILYC-LEARNED-INVERSE` | `true` | missing refs []; present ['REF-0579', 'REF-0582', 'REF-0585', 'REF-0588', 'REF-0131', 'REF-0143', 'REF-0672'] |
| `condition-row-present-EVP-0002-FAMILYC-LEARNED-INVERSE` | `true` | EVALUATION-PROTOCOL-LEDGER.json:EVP-0002-FAMILYC-LEARNED-INVERSE |
| `condition-row-refs-EVP-0002-FAMILYC-LEARNED-INVERSE` | `true` | missing refs []; present ['REF-0590', 'REF-0591', 'REF-0593', 'REF-0594', 'REF-0598', 'REF-0670', 'REF-0671', 'REF-0672'] |
| `condition-row-present-BMS-0002-FAMILYC-LEARNED-INVERSE` | `true` | BENCHMARK-SUITE-LEDGER.json:BMS-0002-FAMILYC-LEARNED-INVERSE |
| `condition-row-refs-BMS-0002-FAMILYC-LEARNED-INVERSE` | `true` | missing refs []; present ['REF-0589', 'REF-0590', 'REF-0591', 'REF-0592', 'REF-0593', 'REF-0670', 'REF-0671'] |
| `condition-row-present-BMT-0002-FAMILYC-LEARNED-INVERSE` | `true` | BENCHMARK-METRIC-LEDGER.json:BMT-0002-FAMILYC-LEARNED-INVERSE |
| `condition-row-refs-BMT-0002-FAMILYC-LEARNED-INVERSE` | `true` | missing refs []; present ['REF-0589', 'REF-0592', 'REF-0595', 'REF-0596', 'REF-0597', 'REF-0671', 'REF-0672'] |
| `condition-row-present-UIN-0002-FAMILYC-LEARNED-INVERSE` | `true` | UNCERTAINTY-INTERVAL-LEDGER.json:UIN-0002-FAMILYC-LEARNED-INVERSE |
| `condition-row-refs-UIN-0002-FAMILYC-LEARNED-INVERSE` | `true` | missing refs []; present ['REF-0616', 'REF-0617', 'REF-0623', 'REF-0672'] |
| `condition-row-present-CCG-0002-FAMILYC-LEARNED-INVERSE` | `true` | COVERAGE-CALIBRATION-LEDGER.json:CCG-0002-FAMILYC-LEARNED-INVERSE |
| `condition-row-refs-CCG-0002-FAMILYC-LEARNED-INVERSE` | `true` | missing refs []; present ['REF-0620', 'REF-0621', 'REF-0617', 'REF-0672'] |
| `condition-row-present-NST-0002-FAMILYC-LEARNED-INVERSE` | `true` | NUMERICAL-STABILITY-LEDGER.json:NST-0002-FAMILYC-LEARNED-INVERSE |
| `condition-row-refs-NST-0002-FAMILYC-LEARNED-INVERSE` | `true` | missing refs []; present ['REF-0286', 'REF-0287', 'REF-0670', 'REF-0671'] |
| `condition-row-present-CAP-0002-FAMILYC-LEARNED-INVERSE` | `true` | MODEL-CAPACITY-LEDGER.json:CAP-0002-FAMILYC-LEARNED-INVERSE |
| `condition-row-refs-CAP-0002-FAMILYC-LEARNED-INVERSE` | `true` | missing refs []; present ['REF-0263', 'REF-0264', 'REF-0265', 'REF-0266', 'REF-0236', 'REF-0268', 'REF-0670', 'REF-0671'] |

## Non-promotion rule

Current learned-inverse / holographic-ML papers can strengthen only route-local finite-window, cutoff, OOD, baseline, uncertainty/coverage, and simulator-inheritance pressure. They may be exposed through forecast, decision, and empirical-delta handoff rows, but the fresh refs must not become acquired evidence-unit support or a route promotion beyond S2.
