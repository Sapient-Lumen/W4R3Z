# Asymptotic-safety Lorentzian-observable source-role audit (generated)

Generated from the asymptotic-safety route, forecast, decision, empirical-delta, evidence-unit, and route-control ledgers. Do not edit directly; run `make index` after changing these rows.

- Route checked: `R-OQ0057-ASYMPTOTIC-SAFETY`
- Required current refs: `REF-0166`, `REF-0658`, `REF-0659`, `REF-0481`
- Lorentzian-observable checks: `47`
- Lorentzian-observable failures: `0`

| Check | Passed | Detail |
|---|---:|---|
| `route-present` | `true` | route `R-OQ0057-ASYMPTOTIC-SAFETY` must exist |
| `route-current-state-capped` | `true` | current authority is `S2`; expected `S2` |
| `route-promotion-ceiling-capped` | `true` | promotion ceiling is `S2`; expected `S2` |
| `route-names-observable-debt` | `true` | route text missing terms [] |
| `forecast-present` | `true` | forecast `DF-0007-AS-REGULATOR-PORTABILITY` must exist |
| `forecast-route-local` | `true` | forecast route is `R-OQ0057-ASYMPTOTIC-SAFETY` |
| `forecast-credit-capped` | `true` | forecast current maximum is `S2`; expected `S2` |
| `forecast-current-refs` | `true` | missing refs []; present ['REF-0229', 'REF-0233', 'REF-0166', 'REF-0658', 'REF-0659', 'REF-0481'] |
| `forecast-replay-denominators` | `true` | required_public_record missing terms [] |
| `forecast-non-promotion` | `true` | forecast must explicitly block closure/identity spending |
| `delta-present` | `true` | delta `ED-0013-AS-AMPLITUDE-REGULATOR-PORTABILITY-PRESSURE` must exist |
| `delta-route-local` | `true` | delta route_ids are `['R-OQ0057-ASYMPTOTIC-SAFETY']` |
| `delta-credit-capped` | `true` | delta promotion ceiling is `S2`; expected `S2` |
| `delta-current-refs` | `true` | missing refs []; present ['REF-0035', 'REF-0040', 'REF-0166', 'REF-0481', 'REF-0658', 'REF-0659'] |
| `delta-hard-denominators` | `true` | delta text missing terms [] |
| `decision-present` | `true` | decision experiment `DX-0009-AS-REGULATOR-PORTABILITY-EXTRACTION` must exist |
| `decision-current-refs` | `true` | missing refs []; present ['REF-0035', 'REF-0481', 'REF-0166', 'REF-0658', 'REF-0659'] |
| `decision-hooks-delta` | `true` | decision hooks ['ED-0013-AS-AMPLITUDE-REGULATOR-PORTABILITY-PRESSURE'] |
| `decision-public-artifact-denominators` | `true` | decision artifact missing terms [] |
| `evidence-present` | `true` | evidence unit `EU-0005-AS-RG-TRUNCATION` must exist |
| `fresh-refs-not-acquired-evidence` | `true` | fresh refs incorrectly present on acquired evidence unit: [] |
| `evidence-credit-capped` | `true` | evidence maximum credit is `S2`; expected `S2` |
| `evidence-names-current-delta-handoff` | `true` | evidence empirical_delta_ids ['ED-0013-AS-AMPLITUDE-REGULATOR-PORTABILITY-PRESSURE', 'ED-0030-CLASSICAL-GR-OBSERVED-SECTOR-PRESSURE', 'ED-0031-QM-QFT-GAUGE-OBSERVED-SECTOR-PRESSURE', 'ED-0032-QCD-HADRONIC-OBSERVED-SECTOR-PRESSURE', 'ED-0033-LORENTZ-CPT-SME-OBSERVED-SECTOR-PRESSURE', 'ED-0034-ELECTROWEAK-FLAVOR-NEUTRINO-OBSERVED-SECTOR-PRESSURE', 'ED-0035-EQUIVALENCE-FIFTH-FORCE-WEAKFIELD-OBSERVED-SECTOR-PRESSURE'] |
| `condition-row-present-RGF-0005-ASYMPTOTIC-SAFETY` | `true` | RENORMALIZATION-FLOW-LEDGER.json:RGF-0005-ASYMPTOTIC-SAFETY |
| `condition-row-refs-RGF-0005-ASYMPTOTIC-SAFETY` | `true` | missing refs []; present ['REF-0325', 'REF-0326', 'REF-0320', 'REF-0324', 'REF-0166', 'REF-0658'] |
| `condition-row-present-REG-0005-ASYMPTOTIC-SAFETY` | `true` | REGULARIZATION-SCHEME-LEDGER.json:REG-0005-ASYMPTOTIC-SAFETY |
| `condition-row-refs-REG-0005-ASYMPTOTIC-SAFETY` | `true` | missing refs []; present ['REF-0325', 'REF-0326', 'REF-0320', 'REF-0324', 'REF-0166', 'REF-0658'] |
| `condition-row-present-SCAT-0005-ASYMPTOTIC-SAFETY` | `true` | SCATTERING-OBSERVABLE-LEDGER.json:SCAT-0005-ASYMPTOTIC-SAFETY |
| `condition-row-refs-SCAT-0005-ASYMPTOTIC-SAFETY` | `true` | missing refs []; present ['REF-0451', 'REF-0453', 'REF-0455', 'REF-0456', 'REF-0166', 'REF-0658', 'REF-0710', 'REF-0711'] |
| `condition-row-present-ASYM-0005-ASYMPTOTIC-SAFETY` | `true` | ASYMPTOTIC-STATE-LEDGER.json:ASYM-0005-ASYMPTOTIC-SAFETY |
| `condition-row-refs-ASYM-0005-ASYMPTOTIC-SAFETY` | `true` | missing refs []; present ['REF-0450', 'REF-0451', 'REF-0453', 'REF-0166'] |
| `condition-row-present-IRD-0005-ASYMPTOTIC-SAFETY` | `true` | INFRARED-DRESSING-LEDGER.json:IRD-0005-ASYMPTOTIC-SAFETY |
| `condition-row-refs-IRD-0005-ASYMPTOTIC-SAFETY` | `true` | missing refs []; present ['REF-0450', 'REF-0452', 'REF-0453', 'REF-0454', 'REF-0166'] |
| `condition-row-present-UNI-0005-ASYMPTOTIC-SAFETY` | `true` | UNITARITY-CHECK-LEDGER.json:UNI-0005-ASYMPTOTIC-SAFETY |
| `condition-row-refs-UNI-0005-ASYMPTOTIC-SAFETY` | `true` | missing refs []; present ['REF-0334', 'REF-0337', 'REF-0340', 'REF-0166', 'REF-0481', 'REF-0710', 'REF-0711'] |
| `condition-row-present-CAU-0005-ASYMPTOTIC-SAFETY` | `true` | CAUSALITY-CONE-LEDGER.json:CAU-0005-ASYMPTOTIC-SAFETY |
| `condition-row-refs-CAU-0005-ASYMPTOTIC-SAFETY` | `true` | missing refs []; present ['REF-0334', 'REF-0337', 'REF-0340', 'REF-0481'] |
| `condition-row-present-STB-0005-ASYMPTOTIC-SAFETY` | `true` | STABILITY-POSITIVITY-LEDGER.json:STB-0005-ASYMPTOTIC-SAFETY |
| `condition-row-refs-STB-0005-ASYMPTOTIC-SAFETY` | `true` | missing refs []; present ['REF-0334', 'REF-0337', 'REF-0340', 'REF-0166', 'REF-0481'] |
| `condition-row-present-HZN-0005-ASYMPTOTIC-SAFETY` | `true` | HORIZON-STRUCTURE-LEDGER.json:HZN-0005-ASYMPTOTIC-SAFETY |
| `condition-row-refs-HZN-0005-ASYMPTOTIC-SAFETY` | `true` | missing refs []; present ['REF-0007', 'REF-0008', 'REF-0191', 'REF-0192', 'REF-0411', 'REF-0412', 'REF-0413', 'REF-0414', 'REF-0415', 'REF-0416', 'REF-0417', 'REF-0418', 'REF-0659', 'REF-0481', 'REF-0702', 'REF-0703'] |
| `condition-row-present-BHT-0005-ASYMPTOTIC-SAFETY` | `true` | BLACK-HOLE-THERMODYNAMICS-LEDGER.json:BHT-0005-ASYMPTOTIC-SAFETY |
| `condition-row-refs-BHT-0005-ASYMPTOTIC-SAFETY` | `true` | missing refs []; present ['REF-0007', 'REF-0008', 'REF-0191', 'REF-0192', 'REF-0411', 'REF-0412', 'REF-0413', 'REF-0414', 'REF-0415', 'REF-0416', 'REF-0417', 'REF-0418', 'REF-0659', 'REF-0481'] |
| `condition-row-present-TOP-0005-ASYMPTOTIC-SAFETY` | `true` | SPACETIME-TOPOLOGY-LEDGER.json:TOP-0005-ASYMPTOTIC-SAFETY |
| `condition-row-refs-TOP-0005-ASYMPTOTIC-SAFETY` | `true` | missing refs []; present ['REF-0364', 'REF-0365', 'REF-0366', 'REF-0367', 'REF-0368', 'REF-0369', 'REF-0370', 'REF-0371', 'REF-0372', 'REF-0481'] |
| `condition-row-present-LCV-0005-ASYMPTOTIC-SAFETY` | `true` | LORENTZ-COVARIANCE-LEDGER.json:LCV-0005-ASYMPTOTIC-SAFETY |
| `condition-row-refs-LCV-0005-ASYMPTOTIC-SAFETY` | `true` | missing refs []; present ['REF-0510', 'REF-0511', 'REF-0512', 'REF-0166', 'REF-0658', 'REF-0710', 'REF-0711', 'REF-0509', 'REF-0715', 'REF-0716', 'REF-0717', 'REF-0718'] |

## Non-promotion rule

Current asymptotic-safety papers can strengthen only route-local Lorentzian-observable, scattering, momentum-dependence, black-hole/GLOB, and topology/swampland pressure. They may be exposed through empirical-delta handoff rows, but the fresh refs must not become acquired evidence-unit support or a route promotion beyond S2.
