# String/M observed-sector atlas source-role audit (generated)

Generated from the String/M route, forecast, empirical-delta, decision, evidence-unit, and route-control rows. Do not edit directly; run `make index` after changing String/M observed-sector custody.

- Route checked: `R-OQ0057-STRINGM-ATLAS`
- Current pressure refs: `REF-0673`, `REF-0674`, `REF-0675`, `REF-0676`
- String/M observed-sector checks: `73`
- String/M observed-sector failures: `0`

| Check | Passed | Detail |
|---|---:|---|
| `route-present` | `true` | route `R-OQ0057-STRINGM-ATLAS` must exist |
| `route-authority-capped` | `true` | authority_state is `S2`; expected S2 |
| `route-promotion-capped` | `true` | promotion ceiling is `S2`; expected S2 |
| `route-denominator-language` | `true` | route text missing [] |
| `route-hooks-forecast` | `true` | forecast_ids ['DF-0006-STRING-OBSERVED-SECTOR-INVERSE', 'DF-0017-STRINGM-FLUX-ATLAS-OBSERVED-SECTOR-QUOTIENT', 'DF-0024-CLASSICAL-GR-OBSERVED-SECTOR-REPLAY', 'DF-0025-QM-QFT-GAUGE-OBSERVED-SECTOR-REPLAY', 'DF-0026-QCD-HADRONIC-OBSERVED-SECTOR-REPLAY', 'DF-0027-LORENTZ-CPT-SME-OBSERVED-SECTOR-REPLAY', 'DF-0028-ELECTROWEAK-FLAVOR-NEUTRINO-OBSERVED-SECTOR-REPLAY', 'DF-0029-EQUIVALENCE-FIFTH-FORCE-WEAKFIELD-OBSERVED-SECTOR-REPLAY'] |
| `route-hooks-delta` | `true` | empirical_delta_ids ['ED-0005-DUALITY-UNDERDETERMINATION-QUOTIENT', 'ED-0022-STRINGM-ATLAS-MODULI-MEASURE-COSMOLOGY-PRESSURE', 'ED-0030-CLASSICAL-GR-OBSERVED-SECTOR-PRESSURE', 'ED-0031-QM-QFT-GAUGE-OBSERVED-SECTOR-PRESSURE', 'ED-0032-QCD-HADRONIC-OBSERVED-SECTOR-PRESSURE', 'ED-0033-LORENTZ-CPT-SME-OBSERVED-SECTOR-PRESSURE', 'ED-0034-ELECTROWEAK-FLAVOR-NEUTRINO-OBSERVED-SECTOR-PRESSURE', 'ED-0035-EQUIVALENCE-FIFTH-FORCE-WEAKFIELD-OBSERVED-SECTOR-PRESSURE'] |
| `forecast-present` | `true` | forecast `DF-0017-STRINGM-FLUX-ATLAS-OBSERVED-SECTOR-QUOTIENT` must exist |
| `forecast-route-local` | `true` | forecast route is `R-OQ0057-STRINGM-ATLAS` |
| `forecast-credit-capped` | `true` | forecast current maximum is `S2` |
| `forecast-current-refs` | `true` | missing refs []; present ['REF-0673', 'REF-0674', 'REF-0675', 'REF-0676'] |
| `forecast-public-denominators` | `true` | forecast text missing [] |
| `legacy-forecast-present` | `true` | forecast `DF-0006-STRING-OBSERVED-SECTOR-INVERSE` must exist |
| `legacy-forecast-current-refs` | `true` | missing refs []; present ['REF-0206', 'REF-0207', 'REF-0228', 'REF-0232', 'REF-0673', 'REF-0674', 'REF-0675', 'REF-0676'] |
| `legacy-forecast-credit-capped` | `true` | current max is `S2` |
| `delta-present` | `true` | delta `ED-0022-STRINGM-ATLAS-MODULI-MEASURE-COSMOLOGY-PRESSURE` must exist |
| `delta-route-local` | `true` | delta route_ids ['R-OQ0057-STRINGM-ATLAS'] |
| `delta-ceiling-capped` | `true` | delta ceiling is `S2` |
| `delta-current-refs` | `true` | missing refs []; present ['REF-0673', 'REF-0674', 'REF-0675', 'REF-0676'] |
| `delta-denominator-language` | `true` | delta text missing [] |
| `decision-present` | `true` | decision `DX-0008-STRINGM-OBSERVED-SECTOR-INVERSE-ATLAS` must exist |
| `decision-route-local` | `true` | decision routes ['R-OQ0057-STRINGM-ATLAS'] |
| `decision-current-refs` | `true` | missing refs []; present ['REF-0034', 'REF-0501', 'REF-0502', 'REF-0503', 'REF-0504', 'REF-0673', 'REF-0674', 'REF-0675', 'REF-0676'] |
| `decision-hooks-delta` | `true` | hooks ['ED-0005-DUALITY-UNDERDETERMINATION-QUOTIENT', 'ED-0022-STRINGM-ATLAS-MODULI-MEASURE-COSMOLOGY-PRESSURE'] |
| `decision-public-artifact-denominators` | `true` | decision text missing [] |
| `evidence-present` | `true` | evidence `EU-0004-STRINGM-ATLAS-DUALITY-VACUUM` must exist |
| `fresh-refs-not-acquired-evidence` | `true` | fresh refs incorrectly on evidence unit: [] |
| `evidence-credit-capped` | `true` | maximum credit is `S2` |
| `evidence-delta-handoff` | `true` | empirical_delta_ids ['ED-0005-DUALITY-UNDERDETERMINATION-QUOTIENT', 'ED-0022-STRINGM-ATLAS-MODULI-MEASURE-COSMOLOGY-PRESSURE', 'ED-0030-CLASSICAL-GR-OBSERVED-SECTOR-PRESSURE', 'ED-0031-QM-QFT-GAUGE-OBSERVED-SECTOR-PRESSURE', 'ED-0032-QCD-HADRONIC-OBSERVED-SECTOR-PRESSURE', 'ED-0033-LORENTZ-CPT-SME-OBSERVED-SECTOR-PRESSURE', 'ED-0034-ELECTROWEAK-FLAVOR-NEUTRINO-OBSERVED-SECTOR-PRESSURE', 'ED-0035-EQUIVALENCE-FIFTH-FORCE-WEAKFIELD-OBSERVED-SECTOR-PRESSURE'] |
| `condition-present-CPG-0004-STRINGM-ATLAS` | `true` | COMPACTIFICATION-GEOMETRY-LEDGER.json:CPG-0004-STRINGM-ATLAS |
| `condition-refs-CPG-0004-STRINGM-ATLAS` | `true` | missing refs []; present ['REF-0498', 'REF-0499', 'REF-0501', 'REF-0673', 'REF-0674', 'REF-0676'] |
| `condition-ceiling-CPG-0004-STRINGM-ATLAS` | `true` | maximum authority effect `S2` |
| `condition-present-MDS-0004-STRINGM-ATLAS` | `true` | MODULI-STABILIZATION-LEDGER.json:MDS-0004-STRINGM-ATLAS |
| `condition-refs-MDS-0004-STRINGM-ATLAS` | `true` | missing refs []; present ['REF-0498', 'REF-0499', 'REF-0500', 'REF-0501', 'REF-0673', 'REF-0674', 'REF-0676'] |
| `condition-ceiling-MDS-0004-STRINGM-ATLAS` | `true` | maximum authority effect `S2` |
| `condition-present-SWC-0004-STRINGM-ATLAS` | `true` | SWAMPLAND-COMPATIBILITY-LEDGER.json:SWC-0004-STRINGM-ATLAS |
| `condition-refs-SWC-0004-STRINGM-ATLAS` | `true` | missing refs []; present ['REF-0502', 'REF-0503', 'REF-0504', 'REF-0505', 'REF-0674', 'REF-0675', 'REF-0676'] |
| `condition-ceiling-SWC-0004-STRINGM-ATLAS` | `true` | maximum authority effect `S2` |
| `condition-present-VED-0004-STRINGM-ATLAS` | `true` | VACUUM-ENERGY-LEDGER.json:VED-0004-STRINGM-ATLAS |
| `condition-refs-VED-0004-STRINGM-ATLAS` | `true` | missing refs []; present ['REF-0401', 'REF-0402', 'REF-0403', 'REF-0404', 'REF-0405', 'REF-0406', 'REF-0407', 'REF-0408', 'REF-0409', 'REF-0410', 'REF-0499', 'REF-0502', 'REF-0675', 'REF-0706', 'REF-0707', 'REF-0708', 'REF-0709'] |
| `condition-ceiling-VED-0004-STRINGM-ATLAS` | `true` | maximum authority effect `S2` |
| `condition-present-CBG-0004-STRINGM-ATLAS` | `true` | COSMOLOGICAL-BACKGROUND-LEDGER.json:CBG-0004-STRINGM-ATLAS |
| `condition-refs-CBG-0004-STRINGM-ATLAS` | `true` | missing refs []; present ['REF-0401', 'REF-0402', 'REF-0403', 'REF-0404', 'REF-0405', 'REF-0406', 'REF-0407', 'REF-0408', 'REF-0409', 'REF-0410', 'REF-0502', 'REF-0675', 'REF-0704', 'REF-0706', 'REF-0707', 'REF-0708', 'REF-0709'] |
| `condition-ceiling-CBG-0004-STRINGM-ATLAS` | `true` | maximum authority effect `S2` |
| `condition-present-MEA-0004-STRINGM-ATLAS` | `true` | MEASURE-DEFINITION-LEDGER.json:MEA-0004-STRINGM-ATLAS |
| `condition-refs-MEA-0004-STRINGM-ATLAS` | `true` | missing refs []; present ['REF-0373', 'REF-0374', 'REF-0375', 'REF-0376', 'REF-0377', 'REF-0378', 'REF-0379', 'REF-0380', 'REF-0381', 'REF-0673', 'REF-0675'] |
| `condition-ceiling-MEA-0004-STRINGM-ATLAS` | `true` | maximum authority effect `S2` |
| `condition-present-TYP-0004-STRINGM-ATLAS` | `true` | TYPICALITY-WEIGHTING-LEDGER.json:TYP-0004-STRINGM-ATLAS |
| `condition-refs-TYP-0004-STRINGM-ATLAS` | `true` | missing refs []; present ['REF-0373', 'REF-0374', 'REF-0375', 'REF-0376', 'REF-0377', 'REF-0378', 'REF-0379', 'REF-0380', 'REF-0381', 'REF-0673', 'REF-0675'] |
| `condition-ceiling-TYP-0004-STRINGM-ATLAS` | `true` | maximum authority effect `S2` |
| `condition-present-SEC-0004-STRINGM-ATLAS` | `true` | SECTOR-SELECTION-LEDGER.json:SEC-0004-STRINGM-ATLAS |
| `condition-refs-SEC-0004-STRINGM-ATLAS` | `true` | missing refs []; present ['REF-0304', 'REF-0306', 'REF-0307', 'REF-0673', 'REF-0674', 'REF-0676'] |
| `condition-ceiling-SEC-0004-STRINGM-ATLAS` | `true` | maximum authority effect `S2` |
| `condition-present-PSP-0004-STRINGM-ATLAS` | `true` | PARTICLE-SPECTRUM-LEDGER.json:PSP-0004-STRINGM-ATLAS |
| `condition-refs-PSP-0004-STRINGM-ATLAS` | `true` | missing refs []; present ['REF-0392', 'REF-0393', 'REF-0394', 'REF-0395', 'REF-0034', 'REF-0397', 'REF-0398', 'REF-0399', 'REF-0400', 'REF-0673', 'REF-0674', 'REF-0676', 'REF-0699', 'REF-0700', 'REF-0701', 'REF-0712', 'REF-0713', 'REF-0714', 'REF-0719', 'REF-0720', 'REF-0721', 'REF-0722', 'REF-0723', 'REF-0724'] |
| `condition-ceiling-PSP-0004-STRINGM-ATLAS` | `true` | maximum authority effect `S2` |
| `condition-present-SF-0004-STRINGM-ATLAS` | `true` | SELECTION-FUNCTION-LEDGER.json:SF-0004-STRINGM-ATLAS |
| `condition-refs-SF-0004-STRINGM-ATLAS` | `true` | missing refs []; present ['REF-0257', 'REF-0258', 'REF-0259', 'REF-0260', 'REF-0261', 'REF-0262', 'REF-0673', 'REF-0675'] |
| `condition-ceiling-SF-0004-STRINGM-ATLAS` | `true` | maximum authority effect `S2` |
| `condition-present-MC-0004-STRINGM-ATLAS` | `true` | MULTIPLICITY-CONTROL-LEDGER.json:MC-0004-STRINGM-ATLAS |
| `condition-refs-MC-0004-STRINGM-ATLAS` | `true` | missing refs []; present ['REF-0257', 'REF-0258', 'REF-0259', 'REF-0260', 'REF-0261', 'REF-0262', 'REF-0673'] |
| `condition-ceiling-MC-0004-STRINGM-ATLAS` | `true` | maximum authority effect `S2` |
| `condition-present-RBIA-0004-STRINGM-ATLAS` | `true` | REPORTING-BIAS-LEDGER.json:RBIA-0004-STRINGM-ATLAS |
| `condition-refs-RBIA-0004-STRINGM-ATLAS` | `true` | missing refs []; present ['REF-0257', 'REF-0258', 'REF-0259', 'REF-0260', 'REF-0261', 'REF-0262', 'REF-0673', 'REF-0674'] |
| `condition-ceiling-RBIA-0004-STRINGM-ATLAS` | `true` | maximum authority effect `S2` |
| `condition-present-CRP-0004-STRINGM-ATLAS` | `true` | COMPUTATIONAL-REPRODUCIBILITY-LEDGER.json:CRP-0004-STRINGM-ATLAS |
| `condition-refs-CRP-0004-STRINGM-ATLAS` | `true` | missing refs []; present ['REF-0278', 'REF-0282', 'REF-0283', 'REF-0673'] |
| `condition-ceiling-CRP-0004-STRINGM-ATLAS` | `true` | maximum authority effect `S2` |
| `condition-present-NST-0004-STRINGM-ATLAS` | `true` | NUMERICAL-STABILITY-LEDGER.json:NST-0004-STRINGM-ATLAS |
| `condition-refs-NST-0004-STRINGM-ATLAS` | `true` | missing refs []; present ['REF-0286', 'REF-0287', 'REF-0673'] |
| `condition-ceiling-NST-0004-STRINGM-ATLAS` | `true` | maximum authority effect `S2` |
| `condition-present-POB-0004-STRINGM-ATLAS` | `true` | PROOF-OBLIGATION-LEDGER.json:POB-0004-STRINGM-ATLAS |
| `condition-refs-POB-0004-STRINGM-ATLAS` | `true` | missing refs []; present ['REF-0290', 'REF-0291', 'REF-0292', 'REF-0293', 'REF-0294', 'REF-0295', 'REF-0296', 'REF-0674', 'REF-0676'] |
| `condition-ceiling-POB-0004-STRINGM-ATLAS` | `true` | maximum authority effect `S2` |

## Non-promotion rule

Current String/M flux-vacuum, Landau-Ginzburg/Minkowski stabilization, and DESI/de Sitter swampland sources can tighten only route-local quotient, moduli, measure, spectrum, vacuum-energy, and cosmology denominators. The fresh refs must not become acquired evidence-unit support and cannot promote the String/M route beyond S2.

