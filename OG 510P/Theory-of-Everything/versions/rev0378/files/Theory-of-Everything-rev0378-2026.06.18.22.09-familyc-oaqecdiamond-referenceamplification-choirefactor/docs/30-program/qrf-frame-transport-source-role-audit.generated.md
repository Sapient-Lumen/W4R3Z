# QRF frame-transport source-role audit (generated)

Generated from QRF route, forecast, decision, empirical-delta, evidence-unit, and route-control rows. Do not edit directly; run `make index` after changing QRF frame-transport source custody.

- Route: `R-OQ0057-FRAME-QRF-RELATIONAL`
- QRF delta: `ED-0023-QRF-FRAME-TRANSPORT-LARGE-GAUGE-PRESSURE`
- FamilyC-only delta fenced off: `ED-0020-FAMILYC-SUBREGION-STATE-PORTABILITY-PRESSURE`
- Current QRF source refs: `REF-0679`, `REF-0680`
- QRF source-role checks: `24`
- QRF source-role failures: `0`

| Check | Passed | Detail |
|---|---:|---|
| `qrf-route-present` | `true` | QRF route row exists |
| `qrf-route-authority-s2` | `true` | authority_state=S2 |
| `qrf-route-ceiling-s2` | `true` | promotion_ceiling=S2 |
| `qrf-delta-present` | `true` | route-local QRF delta exists |
| `qrf-delta-route-local` | `true` | route_ids=['R-OQ0057-FRAME-QRF-RELATIONAL'] |
| `qrf-delta-evidence-link` | `true` | evidence_unit_ids=['EU-0010-QRF-FRAME-TRANSPORT'] |
| `qrf-delta-ceiling-s2` | `true` | promotion_ceiling=S2 |
| `qrf-delta-current-source-refs` | `true` | missing=[] |
| `qrf-evidence-includes-qrf-delta` | `true` | empirical_delta_ids=['ED-0003-SUBREGION-ALGEBRA-AND-EDGE-MODE-PRESSURE', 'ED-0023-QRF-FRAME-TRANSPORT-LARGE-GAUGE-PRESSURE', 'ED-0032-QCD-HADRONIC-OBSERVED-SECTOR-PRESSURE', 'ED-0033-LORENTZ-CPT-SME-OBSERVED-SECTOR-PRESSURE', 'ED-0034-ELECTROWEAK-FLAVOR-NEUTRINO-OBSERVED-SECTOR-PRESSURE', 'ED-0035-EQUIVALENCE-FIFTH-FORCE-WEAKFIELD-OBSERVED-SECTOR-PRESSURE'] |
| `qrf-evidence-excludes-familyc-only-delta` | `true` | empirical_delta_ids=['ED-0003-SUBREGION-ALGEBRA-AND-EDGE-MODE-PRESSURE', 'ED-0023-QRF-FRAME-TRANSPORT-LARGE-GAUGE-PRESSURE', 'ED-0032-QCD-HADRONIC-OBSERVED-SECTOR-PRESSURE', 'ED-0033-LORENTZ-CPT-SME-OBSERVED-SECTOR-PRESSURE', 'ED-0034-ELECTROWEAK-FLAVOR-NEUTRINO-OBSERVED-SECTOR-PRESSURE', 'ED-0035-EQUIVALENCE-FIFTH-FORCE-WEAKFIELD-OBSERVED-SECTOR-PRESSURE'] |
| `qrf-evidence-new-refs-not-acquired-credit` | `true` | forbidden_present=[] |
| `familyc-delta-excludes-qrf-route` | `true` | route_ids=['R-OQ0057-FAMILYC-EW-CODE'] |
| `familyc-delta-excludes-qrf-evidence` | `true` | evidence_unit_ids=['EU-0001-FAMILYC-EW-RECONSTRUCTION'] |
| `familyc-delta-excludes-qrf-control-handles` | `true` | leaked=[] |
| `qrf-forecast-current-source-refs` | `true` | missing=[] |
| `qrf-decision-current-source-refs` | `true` | missing=[] |
| `qrf-decision-hooks-qrf-delta` | `true` | empirical_delta_hooks=['ED-0003-SUBREGION-ALGEBRA-AND-EDGE-MODE-PRESSURE', 'ED-0023-QRF-FRAME-TRANSPORT-LARGE-GAUGE-PRESSURE'] |
| `control-row-current-refs-AP-REFERENCE-FRAME-TRANSPORT-ASSAY` | `true` | missing=[] |
| `control-row-current-refs-OBSQ-0010-FRAME-QRF-RELATIONAL` | `true` | missing=[] |
| `control-row-current-refs-GSY-0010-FRAME-QRF-RELATIONAL` | `true` | missing=[] |
| `control-row-current-refs-ALG-0010-FRAME-QRF-RELATIONAL` | `true` | missing=[] |
| `control-row-current-refs-EDG-0010-FRAME-QRF-RELATIONAL` | `true` | missing=[] |
| `control-row-current-refs-FAC-0010-FRAME-QRF-RELATIONAL` | `true` | missing=[] |
| `control-row-current-refs-TR-0010-FRAME-QRF-RELATIONAL` | `true` | missing=[] |

## Control rows

| Ledger row | Missing current QRF refs | Passed |
|---|---|---:|
| `ACQUISITION-PROTOCOL-LEDGER.json:AP-REFERENCE-FRAME-TRANSPORT-ASSAY` | — | `true` |
| `OBSERVABLE-QUOTIENT-LEDGER.json:OBSQ-0010-FRAME-QRF-RELATIONAL` | — | `true` |
| `GAUGE-SYMMETRY-LEDGER.json:GSY-0010-FRAME-QRF-RELATIONAL` | — | `true` |
| `ALGEBRAIC-LOCALITY-LEDGER.json:ALG-0010-FRAME-QRF-RELATIONAL` | — | `true` |
| `EDGE-MODE-CENTER-LEDGER.json:EDG-0010-FRAME-QRF-RELATIONAL` | — | `true` |
| `SUBSYSTEM-FACTORIZATION-LEDGER.json:FAC-0010-FRAME-QRF-RELATIONAL` | — | `true` |
| `TRANSPORTABILITY-LEDGER.json:TR-0010-FRAME-QRF-RELATIONAL` | — | `true` |

## Non-promotion rule

QRF, large-gauge, boundary/corner, and crossed-product sources are route-local S2 witness-portability pressure. They cannot be spent as FamilyC subregion-state support, acquired evidence-unit credit, observer-independent entropy closure, or ToE/candidate identity.
