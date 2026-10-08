# rev0088 experiment matrix

| Item | Value |
|---|---:|
| Source paired-delta panel | rev0084 |
| Paired-delta rows | 240 |
| Source game rows | 480 |
| Sampling-design family groups | 3 |
| Gate component rows | 6 |
| Schema-contract rows | 4 |
| Schema hard failures | 0 |
| Score hard failures | 1 |
| Mechanism hard failures | 2 |
| Pool leak hard failures | 0 |
| Candidate pool eligible | false |
| Broad pool eligible | false |

The current rejection is unchanged from rev0087. The substantive change is that future adaptive sampling designs and missing pool/provenance columns now fail closed instead of slipping through a fixed-family gate.
