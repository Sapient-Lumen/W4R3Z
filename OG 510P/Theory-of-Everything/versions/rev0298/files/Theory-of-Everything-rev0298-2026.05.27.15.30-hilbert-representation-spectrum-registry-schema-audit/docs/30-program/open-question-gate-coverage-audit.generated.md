# Open-question gate coverage audit (generated)

Generated from `LEDGER-FAMILY-REGISTRY.json`, `CLAIM-ROUTE-BINDING-LEDGER.json`, and `docs/20-constitution/open-question-registry.md`. Do not edit directly; run `make index` after changing route-layer families or bindings.

- Registry revision: `rev0298`
- Registered layer families: `38`

| Family | OQ | OQ registered | Binding row | Controlling ledgers covered |
|---|---|---:|---|---:|
| `route-state-core` | `OQ-0057` | `true` | `CRB-OQ0057-ALL-ROUTES` | `true` |
| `public-record-custody` | `OQ-0060` | `true` | `CRB-OQ0060-PUBLIC-CARRIER-CLOSURE` | `true` |
| `defeat-rollback-severity` | `OQ-0061` | `true` | `CRB-OQ0061-DEFEAT-ROLLBACK` | `true` |
| `evidence-credit` | `OQ-0062` | `true` | `CRB-OQ0062-EVIDENCE-CREDIT` | `true` |
| `contrast-update-prior` | `OQ-0063` | `true` | `CRB-OQ0063-CONTRAST-UPDATES` | `true` |
| `measurement-systematics-calibration` | `OQ-0064` | `true` | `CRB-OQ0064-MEASUREMENT-SYSTEMATICS` | `true` |
| `validity-transport-extrapolation` | `OQ-0065` | `true` | `CRB-OQ0065-VALIDITY-TRANSPORT-FENCES` | `true` |
| `causal-intervention-counterfactual` | `OQ-0066` | `true` | `CRB-OQ0066-CAUSAL-INTERVENTION-COUNTERFACTUAL` | `true` |
| `selection-multiplicity-reporting` | `OQ-0067` | `true` | `CRB-OQ0067-SELECTION-MULTIPLICITY` | `true` |
| `capacity-complexity-generalization` | `OQ-0068` | `true` | `CRB-OQ0068-CAPACITY-COMPLEXITY` | `true` |
| `semantic-ontology-language` | `OQ-0069` | `true` | `CRB-OQ0069-SEMANTIC-ONTOLOGY-LANGUAGE` | `true` |
| `social-review-consensus` | `OQ-0070` | `true` | `CRB-OQ0070-SOCIAL-AUTHORITY` | `true` |
| `computational-numerical-software` | `OQ-0071` | `true` | `CRB-OQ0071-COMPUTATIONAL-REPRODUCIBILITY` | `true` |
| `formal-proof-assumption-coverage` | `OQ-0072` | `true` | `CRB-OQ0072-FORMAL-PROOF` | `true` |
| `idealization-approximation-limit` | `OQ-0073` | `true` | `CRB-OQ0073-IDEALIZATION-LIMITS` | `true` |
| `boundary-initial-sector` | `OQ-0074` | `true` | `CRB-OQ0074-BOUNDARY-SECTOR` | `true` |
| `gauge-constraint-observable` | `OQ-0075` | `true` | `CRB-OQ0075-GAUGE-CONSTRAINT-QUOTIENT` | `true` |
| `regularization-renormalization-matching` | `OQ-0076` | `true` | `CRB-OQ0076-RENORMALIZATION-MATCHING` | `true` |
| `composition-interface-global` | `OQ-0077` | `true` | `CRB-OQ0077-COMPOSITION-GLOBAL-CONSISTENCY` | `true` |
| `unitarity-causality-stability` | `OQ-0078` | `true` | `CRB-OQ0078-UNITARITY-CAUSALITY-STABILITY` | `true` |
| `quantization-classical-semiclassical` | `OQ-0079` | `true` | `CRB-OQ0079-QUANTIZATION-CORRESPONDENCE` | `true` |
| `information-entropy-no-go` | `OQ-0080` | `true` | `CRB-OQ0080-INFORMATION-ENTROPY-NOGO` | `true` |
| `symmetry-anomaly-conservation` | `OQ-0081` | `true` | `CRB-OQ0081-SYMMETRY-ANOMALY-CONSERVATION` | `true` |
| `topology-dimension-signature` | `OQ-0082` | `true` | `CRB-OQ0082-TOPOLOGY-DIMENSION-SIGNATURE` | `true` |
| `measure-ensemble-typicality` | `OQ-0084` | `true` | `CRB-OQ0084-MEASURE-ENSEMBLE-TYPICALITY` | `true` |
| `subsystem-algebra-edge-center` | `OQ-0083` | `true` | `CRB-OQ0083-SUBSYSTEM-ALGEBRA` | `true` |
| `matter-spectrum-coupling-mass` | `OQ-0085` | `true` | `CRB-OQ0085-MATTER-SECTOR` | `true` |
| `cosmological-background-vacuum-history` | `OQ-0086` | `true` | `CRB-OQ0086-COSMOLOGY-HISTORY` | `true` |
| `black-hole-horizon-thermodynamics-evaporation` | `OQ-0087` | `true` | `CRB-OQ0087-BLACK-HOLE-SECTOR` | `true` |
| `singularity-censorship-hyperbolicity` | `OQ-0088` | `true` | `CRB-OQ0088-SINGULARITY-CENSORSHIP` | `true` |
| `stress-energy-backreaction-conditions` | `OQ-0089` | `true` | `CRB-OQ0089-STRESS-ENERGY-BACKREACTION` | `true` |
| `classical-gr-recovery` | `OQ-0090` | `true` | `CRB-OQ0090-CLASSICAL-GR-RECOVERY` | `true` |
| `state-preparation-detector-decoherence` | `OQ-0091` | `true` | `CRB-OQ0091-STATE-PREPARATION-DETECTOR-DECOHERENCE` | `true` |
| `asymptotic-ir-scattering` | `OQ-0092` | `true` | `CRB-OQ0092-ASYMPTOTIC-IR-SCATTERING` | `true` |
| `discretization-finite-volume-continuum` | `OQ-0093` | `true` | `CRB-OQ0093-DISCRETIZATION-CONTINUUM` | `true` |
| `correlation-operator-bootstrap` | `OQ-0094` | `true` | `CRB-OQ0094-CORRELATION-OPERATOR-BOOTSTRAP` | `true` |
| `phase-order-universality` | `OQ-0095` | `true` | `CRB-OQ0095-PHASE-ORDER-UNIVERSALITY` | `true` |
| `hilbert-representation-spectrum` | `OQ-0096` | `true` | `CRB-OQ0096-HILBERT-REPRESENTATION-SPECTRUM` | `true` |

- Missing or incomplete OQ gates: `0`

## Rule

Every registered route-support family must name an owning OQ. That OQ must be present in the open-question registry and must have a claim-route binding row whose `controlling_ledgers` include the family ledgers. This prevents late-added support layers from existing without an explicit stop rule and authority-propagation gate.
