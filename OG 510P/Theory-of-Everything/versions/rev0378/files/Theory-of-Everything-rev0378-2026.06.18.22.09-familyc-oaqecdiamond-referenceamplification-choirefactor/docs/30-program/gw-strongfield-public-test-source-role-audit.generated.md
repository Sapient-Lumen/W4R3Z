# GW strong-field public-test source-role audit (generated)

Generated from the strong-field GW route, decision, evidence, credit, and control rows. Do not edit directly; run `make index` after changing GW catalog/test source roles.

- Route checked: `R-OQ0057-GW-STRONGFIELD-GR`
- Current GR-test refs: `REF-0677`, `REF-0678`
- Future/runway refs fenced from current evidence-credit: `REF-0213`, `REF-0214`, `REF-0630`, `REF-0631`, `REF-0632`
- GW strong-field source-role checks: `40`
- GW strong-field source-role failures: `0`

| Check | Passed | Detail |
|---|---:|---|
| `route-present` | `true` | route `R-OQ0057-GW-STRONGFIELD-GR` must exist |
| `route-authority-S2` | `true` | authority_state `S2` |
| `route-ceiling-S2` | `true` | promotion_ceiling `S2` |
| `route-nonidentifiability-language` | `true` | missing terms [] |
| `decision-present` | `true` | decision `DX-0003-GW-STRONGFIELD-DEVIATION-OR-POLARIZATION` must exist |
| `decision-route-local` | `true` | routes ['R-OQ0057-GW-STRONGFIELD-GR'] |
| `nested-outcomes-capped-S2` | `true` | too-high outcome ceilings [] |
| `decision-denominator-language` | `true` | missing terms [] |
| `current-test-row-present-DF-0004-STRONGFIELD-GW-DEVIATION` | `true` | DISCRIMINATOR-FORECAST-LEDGER.json:DF-0004-STRONGFIELD-GW-DEVIATION |
| `current-test-refs-DF-0004-STRONGFIELD-GW-DEVIATION` | `true` | missing refs []; present ['REF-0070', 'REF-0218', 'REF-0624', 'REF-0625', 'REF-0629', 'REF-0677', 'REF-0678'] |
| `current-test-row-present-ED-0004-GWTC5-STRONGFIELD-GR-CONSTRAINTS` | `true` | EMPIRICAL-DELTA-LEDGER.json:ED-0004-GWTC5-STRONGFIELD-GR-CONSTRAINTS |
| `current-test-refs-ED-0004-GWTC5-STRONGFIELD-GR-CONSTRAINTS` | `true` | missing refs []; present ['REF-0205', 'REF-0624', 'REF-0625', 'REF-0629', 'REF-0677', 'REF-0678'] |
| `current-test-row-present-DX-0003-GW-STRONGFIELD-DEVIATION-OR-POLARIZATION` | `true` | DECISION-EXPERIMENT-LEDGER.json:DX-0003-GW-STRONGFIELD-DEVIATION-OR-POLARIZATION |
| `current-test-refs-DX-0003-GW-STRONGFIELD-DEVIATION-OR-POLARIZATION` | `true` | missing refs []; present ['REF-0205', 'REF-0213', 'REF-0214', 'REF-0624', 'REF-0625', 'REF-0629', 'REF-0630', 'REF-0631', 'REF-0632', 'REF-0677', 'REF-0678'] |
| `current-test-row-present-EU-0009-GW-STRONGFIELD-CATALOG` | `true` | EVIDENCE-UNIT-LEDGER.json:EU-0009-GW-STRONGFIELD-CATALOG |
| `current-test-refs-EU-0009-GW-STRONGFIELD-CATALOG` | `true` | missing refs []; present ['REF-0070', 'REF-0218', 'REF-0230', 'REF-0624', 'REF-0625', 'REF-0629', 'REF-0677', 'REF-0678'] |
| `current-test-row-present-CA-GW-STRONGFIELD-GR` | `true` | CREDIT-ALLOCATION-LEDGER.json:CA-GW-STRONGFIELD-GR |
| `current-test-refs-CA-GW-STRONGFIELD-GR` | `true` | missing refs []; present ['REF-0070', 'REF-0218', 'REF-0230', 'REF-0094', 'REF-0095', 'REF-0100', 'REF-0677', 'REF-0678'] |
| `current-test-row-present-SV-0005-GW-STRONGFIELD-SEVERITY` | `true` | EVIDENCE-SEVERITY-LEDGER.json:SV-0005-GW-STRONGFIELD-SEVERITY |
| `current-test-refs-SV-0005-GW-STRONGFIELD-SEVERITY` | `true` | missing refs []; present ['REF-0205', 'REF-0218', 'REF-0227', 'REF-0229', 'REF-0624', 'REF-0625', 'REF-0629', 'REF-0677', 'REF-0678'] |
| `current-test-row-present-MM-0009-GW-STRONGFIELD-GR` | `true` | MEASUREMENT-MODEL-LEDGER.json:MM-0009-GW-STRONGFIELD-GR |
| `current-test-refs-MM-0009-GW-STRONGFIELD-GR` | `true` | missing refs []; present ['REF-0241', 'REF-0242', 'REF-0243', 'REF-0245', 'REF-0218', 'REF-0205', 'REF-0625', 'REF-0624', 'REF-0629', 'REF-0677', 'REF-0678'] |
| `current-test-row-present-SYS-0009-GW-STRONGFIELD-GR` | `true` | SYSTEMATIC-UNCERTAINTY-LEDGER.json:SYS-0009-GW-STRONGFIELD-GR |
| `current-test-refs-SYS-0009-GW-STRONGFIELD-GR` | `true` | missing refs []; present ['REF-0241', 'REF-0242', 'REF-0243', 'REF-0245', 'REF-0218', 'REF-0205', 'REF-0624', 'REF-0625', 'REF-0629', 'REF-0677', 'REF-0678'] |
| `current-test-row-present-CAL-0009-GW-STRONGFIELD-GR` | `true` | CALIBRATION-TRACEABILITY-LEDGER.json:CAL-0009-GW-STRONGFIELD-GR |
| `current-test-refs-CAL-0009-GW-STRONGFIELD-GR` | `true` | missing refs []; present ['REF-0241', 'REF-0242', 'REF-0243', 'REF-0245', 'REF-0218', 'REF-0205', 'REF-0624', 'REF-0625', 'REF-0629', 'REF-0677', 'REF-0678'] |
| `current-test-row-present-GRR-0009-GW-STRONGFIELD-GR` | `true` | GRAVITATIONAL-RADIATION-LEDGER.json:GRR-0009-GW-STRONGFIELD-GR |
| `current-test-refs-GRR-0009-GW-STRONGFIELD-GR` | `true` | missing refs []; present ['REF-0436', 'REF-0439', 'REF-0440', 'REF-0677', 'REF-0678'] |
| `current-credit-row-present-EU-0009-GW-STRONGFIELD-CATALOG` | `true` | EVIDENCE-UNIT-LEDGER.json:EU-0009-GW-STRONGFIELD-CATALOG |
| `future-refs-not-current-credit-EU-0009-GW-STRONGFIELD-CATALOG` | `true` | future refs on current credit/evidence row: [] |
| `future-runway-not-credit-language-EU-0009-GW-STRONGFIELD-CATALOG` | `true` | missing terms [] |
| `current-credit-row-present-CA-GW-STRONGFIELD-GR` | `true` | CREDIT-ALLOCATION-LEDGER.json:CA-GW-STRONGFIELD-GR |
| `future-refs-not-current-credit-CA-GW-STRONGFIELD-GR` | `true` | future refs on current credit/evidence row: [] |
| `future-runway-not-credit-language-CA-GW-STRONGFIELD-GR` | `true` | missing terms [] |
| `future-runway-row-present-ED-0011-LISA-AND-NEXTGEN-GW-FORECAST-CORRIDOR` | `true` | EMPIRICAL-DELTA-LEDGER.json:ED-0011-LISA-AND-NEXTGEN-GW-FORECAST-CORRIDOR |
| `future-runway-refs-ED-0011-LISA-AND-NEXTGEN-GW-FORECAST-CORRIDOR` | `true` | missing refs []; present ['REF-0213', 'REF-0214', 'REF-0630', 'REF-0631', 'REF-0632'] |
| `future-runway-row-present-DX-0003-GW-STRONGFIELD-DEVIATION-OR-POLARIZATION` | `true` | DECISION-EXPERIMENT-LEDGER.json:DX-0003-GW-STRONGFIELD-DEVIATION-OR-POLARIZATION |
| `future-runway-refs-DX-0003-GW-STRONGFIELD-DEVIATION-OR-POLARIZATION` | `true` | missing refs []; present ['REF-0205', 'REF-0213', 'REF-0214', 'REF-0624', 'REF-0625', 'REF-0629', 'REF-0630', 'REF-0631', 'REF-0632', 'REF-0677', 'REF-0678'] |
| `evidence-current-catalog-refs` | `true` | source refs ['REF-0070', 'REF-0218', 'REF-0230', 'REF-0624', 'REF-0625', 'REF-0629', 'REF-0677', 'REF-0678'] |
| `credit-current-test-refs` | `true` | source refs ['REF-0070', 'REF-0218', 'REF-0230', 'REF-0094', 'REF-0095', 'REF-0100', 'REF-0677', 'REF-0678'] |

## Non-promotion rule

GW catalog growth, parameterized GR tests, GW250114 spectroscopy, and future LISA/next-generation runway all remain route-local pressure. Current acquired evidence and credit are capped at S2; future runway refs must not appear on acquired evidence-unit or current-credit rows, and nested decision outcomes must not exceed the route ceiling.

