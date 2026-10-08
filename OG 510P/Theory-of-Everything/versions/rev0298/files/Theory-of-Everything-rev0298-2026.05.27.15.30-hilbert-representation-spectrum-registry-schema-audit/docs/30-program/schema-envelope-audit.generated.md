# Schema-envelope audit (generated)

Generated from `LEDGER-FAMILY-REGISTRY.json` and `schemas/*.schema.json`. Do not edit directly; run `make index` after changing registered ledger families or schemas.

- Registry revision: `rev0298`
- Registered layer families: `38`

| Family | Ledger | Schema | Row key | Envelope OK |
|---|---|---|---|---:|
| `route-state-core` | `CANDIDATE-ROUTE-STATE-LEDGER.json` | `schemas/candidate-route-state-ledger.schema.json` | `route_rows` | `1` |
| `route-state-core` | `NEGATIVE-CONTROL-LEDGER.json` | `schemas/negative-control-ledger.schema.json` | `controls` | `1` |
| `route-state-core` | `EMPIRICAL-DELTA-LEDGER.json` | `schemas/empirical-delta-ledger.schema.json` | `empirical_deltas` | `1` |
| `public-record-custody` | `PUBLIC-RECORD-CARRIER-LEDGER.json` | `schemas/public-record-carrier-ledger.schema.json` | `carrier_rows` | `1` |
| `public-record-custody` | `ACQUISITION-PROTOCOL-LEDGER.json` | `schemas/acquisition-protocol-ledger.schema.json` | `protocol_rows` | `1` |
| `public-record-custody` | `CLAIM-ROUTE-BINDING-LEDGER.json` | `schemas/claim-route-binding-ledger.schema.json` | `binding_rows` | `1` |
| `defeat-rollback-severity` | `EPISTEMIC-DEFEATER-LEDGER.json` | `schemas/epistemic-defeater-ledger.schema.json` | `defeater_rows` | `1` |
| `defeat-rollback-severity` | `ROLLBACK-PROPAGATION-LEDGER.json` | `schemas/rollback-propagation-ledger.schema.json` | `rollback_rows` | `1` |
| `defeat-rollback-severity` | `EVIDENCE-SEVERITY-LEDGER.json` | `schemas/evidence-severity-ledger.schema.json` | `severity_rows` | `1` |
| `evidence-credit` | `EVIDENCE-UNIT-LEDGER.json` | `schemas/evidence-unit-ledger.schema.json` | `evidence_units` | `1` |
| `evidence-credit` | `INDEPENDENCE-ASSUMPTION-LEDGER.json` | `schemas/independence-assumption-ledger.schema.json` | `independence_rows` | `1` |
| `evidence-credit` | `CREDIT-ALLOCATION-LEDGER.json` | `schemas/credit-allocation-ledger.schema.json` | `credit_rows` | `1` |
| `contrast-update-prior` | `CONTRAST-CLASS-LEDGER.json` | `schemas/contrast-class-ledger.schema.json` | `contrast_rows` | `1` |
| `contrast-update-prior` | `LIKELIHOOD-UPDATE-LEDGER.json` | `schemas/likelihood-update-ledger.schema.json` | `update_rows` | `1` |
| `contrast-update-prior` | `PRIOR-SENSITIVITY-LEDGER.json` | `schemas/prior-sensitivity-ledger.schema.json` | `prior_rows` | `1` |
| `measurement-systematics-calibration` | `MEASUREMENT-MODEL-LEDGER.json` | `schemas/measurement-model-ledger.schema.json` | `measurement_model_rows` | `1` |
| `measurement-systematics-calibration` | `SYSTEMATIC-UNCERTAINTY-LEDGER.json` | `schemas/systematic-uncertainty-ledger.schema.json` | `systematic_rows` | `1` |
| `measurement-systematics-calibration` | `CALIBRATION-TRACEABILITY-LEDGER.json` | `schemas/calibration-traceability-ledger.schema.json` | `calibration_rows` | `1` |
| `validity-transport-extrapolation` | `DOMAIN-OF-VALIDITY-LEDGER.json` | `schemas/domain-of-validity-ledger.schema.json` | `domain_rows` | `1` |
| `validity-transport-extrapolation` | `TRANSPORTABILITY-LEDGER.json` | `schemas/transportability-ledger.schema.json` | `transport_rows` | `1` |
| `validity-transport-extrapolation` | `EXTRAPOLATION-FENCE-LEDGER.json` | `schemas/extrapolation-fence-ledger.schema.json` | `fence_rows` | `1` |
| `causal-intervention-counterfactual` | `CAUSAL-MECHANISM-LEDGER.json` | `schemas/causal-mechanism-ledger.schema.json` | `mechanism_rows` | `1` |
| `causal-intervention-counterfactual` | `INTERVENTION-PROTOCOL-LEDGER.json` | `schemas/intervention-protocol-ledger.schema.json` | `intervention_rows` | `1` |
| `causal-intervention-counterfactual` | `COUNTERFACTUAL-ROBUSTNESS-LEDGER.json` | `schemas/counterfactual-robustness-ledger.schema.json` | `counterfactual_rows` | `1` |
| `selection-multiplicity-reporting` | `SELECTION-FUNCTION-LEDGER.json` | `schemas/selection-function-ledger.schema.json` | `selection_rows` | `1` |
| `selection-multiplicity-reporting` | `MULTIPLICITY-CONTROL-LEDGER.json` | `schemas/multiplicity-control-ledger.schema.json` | `multiplicity_rows` | `1` |
| `selection-multiplicity-reporting` | `REPORTING-BIAS-LEDGER.json` | `schemas/reporting-bias-ledger.schema.json` | `bias_rows` | `1` |
| `capacity-complexity-generalization` | `MODEL-CAPACITY-LEDGER.json` | `schemas/model-capacity-ledger.schema.json` | `capacity_rows` | `1` |
| `capacity-complexity-generalization` | `COMPLEXITY-PENALTY-LEDGER.json` | `schemas/complexity-penalty-ledger.schema.json` | `complexity_rows` | `1` |
| `capacity-complexity-generalization` | `PREDICTIVE-GENERALIZATION-LEDGER.json` | `schemas/predictive-generalization-ledger.schema.json` | `generalization_rows` | `1` |
| `semantic-ontology-language` | `SEMANTIC-TERM-LEDGER.json` | `schemas/semantic-term-ledger.schema.json` | `semantic_rows` | `1` |
| `semantic-ontology-language` | `ONTOLOGY-COMMITMENT-LEDGER.json` | `schemas/ontology-commitment-ledger.schema.json` | `commitment_rows` | `1` |
| `semantic-ontology-language` | `CLAIM-LANGUAGE-PERMISSION-LEDGER.json` | `schemas/claim-language-permission-ledger.schema.json` | `permission_rows` | `1` |
| `social-review-consensus` | `SOCIAL-AUTHORITY-LEDGER.json` | `schemas/social-authority-ledger.schema.json` | `social_rows` | `1` |
| `social-review-consensus` | `REVIEW-REPLICATION-LEDGER.json` | `schemas/review-replication-ledger.schema.json` | `review_rows` | `1` |
| `social-review-consensus` | `CONSENSUS-ELICITATION-LEDGER.json` | `schemas/consensus-elicitation-ledger.schema.json` | `consensus_rows` | `1` |
| `computational-numerical-software` | `COMPUTATIONAL-REPRODUCIBILITY-LEDGER.json` | `schemas/computational-reproducibility-ledger.schema.json` | `reproducibility_rows` | `1` |
| `computational-numerical-software` | `NUMERICAL-STABILITY-LEDGER.json` | `schemas/numerical-stability-ledger.schema.json` | `stability_rows` | `1` |
| `computational-numerical-software` | `SOFTWARE-SUPPLY-CHAIN-LEDGER.json` | `schemas/software-supply-chain-ledger.schema.json` | `supply_chain_rows` | `1` |
| `formal-proof-assumption-coverage` | `PROOF-OBLIGATION-LEDGER.json` | `schemas/proof-obligation-ledger.schema.json` | `proof_obligation_rows` | `1` |
| `formal-proof-assumption-coverage` | `ASSUMPTION-DISCHARGE-LEDGER.json` | `schemas/assumption-discharge-ledger.schema.json` | `assumption_discharge_rows` | `1` |
| `formal-proof-assumption-coverage` | `FORMALIZATION-COVERAGE-LEDGER.json` | `schemas/formalization-coverage-ledger.schema.json` | `formalization_rows` | `1` |
| `idealization-approximation-limit` | `IDEALIZATION-LEDGER.json` | `schemas/idealization-ledger.schema.json` | `idealization_rows` | `1` |
| `idealization-approximation-limit` | `APPROXIMATION-ERROR-LEDGER.json` | `schemas/approximation-error-ledger.schema.json` | `approximation_rows` | `1` |
| `idealization-approximation-limit` | `LIMIT-INTERCHANGE-LEDGER.json` | `schemas/limit-interchange-ledger.schema.json` | `limit_rows` | `1` |
| `boundary-initial-sector` | `BOUNDARY-CONDITION-LEDGER.json` | `schemas/boundary-condition-ledger.schema.json` | `boundary_rows` | `1` |
| `boundary-initial-sector` | `INITIAL-DATA-LEDGER.json` | `schemas/initial-data-ledger.schema.json` | `initial_data_rows` | `1` |
| `boundary-initial-sector` | `SECTOR-SELECTION-LEDGER.json` | `schemas/sector-selection-ledger.schema.json` | `sector_rows` | `1` |
| `gauge-constraint-observable` | `GAUGE-SYMMETRY-LEDGER.json` | `schemas/gauge-symmetry-ledger.schema.json` | `gauge_rows` | `1` |
| `gauge-constraint-observable` | `CONSTRAINT-CLOSURE-LEDGER.json` | `schemas/constraint-closure-ledger.schema.json` | `constraint_rows` | `1` |
| `gauge-constraint-observable` | `OBSERVABLE-QUOTIENT-LEDGER.json` | `schemas/observable-quotient-ledger.schema.json` | `observable_rows` | `1` |
| `regularization-renormalization-matching` | `REGULARIZATION-SCHEME-LEDGER.json` | `schemas/regularization-scheme-ledger.schema.json` | `regularization_rows` | `1` |
| `regularization-renormalization-matching` | `RENORMALIZATION-FLOW-LEDGER.json` | `schemas/renormalization-flow-ledger.schema.json` | `flow_rows` | `1` |
| `regularization-renormalization-matching` | `MATCHING-CONDITION-LEDGER.json` | `schemas/matching-condition-ledger.schema.json` | `matching_rows` | `1` |
| `composition-interface-global` | `COMPOSITION-LAW-LEDGER.json` | `schemas/composition-law-ledger.schema.json` | `composition_rows` | `1` |
| `composition-interface-global` | `INTERFACE-COMPATIBILITY-LEDGER.json` | `schemas/interface-compatibility-ledger.schema.json` | `interface_rows` | `1` |
| `composition-interface-global` | `GLOBAL-CONSISTENCY-LEDGER.json` | `schemas/global-consistency-ledger.schema.json` | `global_rows` | `1` |
| `unitarity-causality-stability` | `UNITARITY-CHECK-LEDGER.json` | `schemas/unitarity-check-ledger.schema.json` | `unitarity_rows` | `1` |
| `unitarity-causality-stability` | `CAUSALITY-CONE-LEDGER.json` | `schemas/causality-cone-ledger.schema.json` | `causality_rows` | `1` |
| `unitarity-causality-stability` | `STABILITY-POSITIVITY-LEDGER.json` | `schemas/stability-positivity-ledger.schema.json` | `stability_rows` | `1` |
| `quantization-classical-semiclassical` | `QUANTIZATION-MAP-LEDGER.json` | `schemas/quantization-map-ledger.schema.json` | `quantization_rows` | `1` |
| `quantization-classical-semiclassical` | `CLASSICAL-LIMIT-LEDGER.json` | `schemas/classical-limit-ledger.schema.json` | `classical_limit_rows` | `1` |
| `quantization-classical-semiclassical` | `SEMICLASSICAL-CORRESPONDENCE-LEDGER.json` | `schemas/semiclassical-correspondence-ledger.schema.json` | `semiclassical_rows` | `1` |
| `information-entropy-no-go` | `INFORMATION-FLOW-LEDGER.json` | `schemas/information-flow-ledger.schema.json` | `information_rows` | `1` |
| `information-entropy-no-go` | `ENTROPY-ACCOUNTING-LEDGER.json` | `schemas/entropy-accounting-ledger.schema.json` | `entropy_rows` | `1` |
| `information-entropy-no-go` | `NO-GO-COMPLIANCE-LEDGER.json` | `schemas/no-go-compliance-ledger.schema.json` | `no_go_rows` | `1` |
| `symmetry-anomaly-conservation` | `SYMMETRY-REALIZATION-LEDGER.json` | `schemas/symmetry-realization-ledger.schema.json` | `symmetry_rows` | `1` |
| `symmetry-anomaly-conservation` | `ANOMALY-MATCHING-LEDGER.json` | `schemas/anomaly-matching-ledger.schema.json` | `anomaly_rows` | `1` |
| `symmetry-anomaly-conservation` | `CONSERVATION-LAW-LEDGER.json` | `schemas/conservation-law-ledger.schema.json` | `conservation_rows` | `1` |
| `topology-dimension-signature` | `SPACETIME-TOPOLOGY-LEDGER.json` | `schemas/spacetime-topology-ledger.schema.json` | `topology_rows` | `1` |
| `topology-dimension-signature` | `DIMENSION-REALIZATION-LEDGER.json` | `schemas/dimension-realization-ledger.schema.json` | `dimension_rows` | `1` |
| `topology-dimension-signature` | `SIGNATURE-STRUCTURE-LEDGER.json` | `schemas/signature-structure-ledger.schema.json` | `signature_rows` | `1` |
| `measure-ensemble-typicality` | `MEASURE-DEFINITION-LEDGER.json` | `schemas/measure-definition-ledger.schema.json` | `measure_rows` | `1` |
| `measure-ensemble-typicality` | `ENSEMBLE-SAMPLING-LEDGER.json` | `schemas/ensemble-sampling-ledger.schema.json` | `ensemble_rows` | `1` |
| `measure-ensemble-typicality` | `TYPICALITY-WEIGHTING-LEDGER.json` | `schemas/typicality-weighting-ledger.schema.json` | `typicality_rows` | `1` |
| `subsystem-algebra-edge-center` | `ALGEBRAIC-LOCALITY-LEDGER.json` | `schemas/algebraic-locality-ledger.schema.json` | `algebraic_rows` | `1` |
| `subsystem-algebra-edge-center` | `SUBSYSTEM-FACTORIZATION-LEDGER.json` | `schemas/subsystem-factorization-ledger.schema.json` | `factorization_rows` | `1` |
| `subsystem-algebra-edge-center` | `EDGE-MODE-CENTER-LEDGER.json` | `schemas/edge-mode-center-ledger.schema.json` | `edge_mode_rows` | `1` |
| `matter-spectrum-coupling-mass` | `PARTICLE-SPECTRUM-LEDGER.json` | `schemas/particle-spectrum-ledger.schema.json` | `particle_spectrum_rows` | `1` |
| `matter-spectrum-coupling-mass` | `INTERACTION-COUPLING-LEDGER.json` | `schemas/interaction-coupling-ledger.schema.json` | `interaction_coupling_rows` | `1` |
| `matter-spectrum-coupling-mass` | `MASS-HIERARCHY-LEDGER.json` | `schemas/mass-hierarchy-ledger.schema.json` | `mass_hierarchy_rows` | `1` |
| `cosmological-background-vacuum-history` | `COSMOLOGICAL-BACKGROUND-LEDGER.json` | `schemas/cosmological-background-ledger.schema.json` | `background_rows` | `1` |
| `cosmological-background-vacuum-history` | `VACUUM-ENERGY-LEDGER.json` | `schemas/vacuum-energy-ledger.schema.json` | `vacuum_energy_rows` | `1` |
| `cosmological-background-vacuum-history` | `THERMAL-HISTORY-LEDGER.json` | `schemas/thermal-history-ledger.schema.json` | `thermal_history_rows` | `1` |
| `black-hole-horizon-thermodynamics-evaporation` | `HORIZON-STRUCTURE-LEDGER.json` | `schemas/horizon-structure-ledger.schema.json` | `horizon_rows` | `1` |
| `black-hole-horizon-thermodynamics-evaporation` | `BLACK-HOLE-THERMODYNAMICS-LEDGER.json` | `schemas/black-hole-thermodynamics-ledger.schema.json` | `thermodynamics_rows` | `1` |
| `black-hole-horizon-thermodynamics-evaporation` | `EVAPORATION-RADIATION-LEDGER.json` | `schemas/evaporation-radiation-ledger.schema.json` | `evaporation_rows` | `1` |
| `singularity-censorship-hyperbolicity` | `CURVATURE-REGIME-LEDGER.json` | `schemas/curvature-regime-ledger.schema.json` | `curvature_rows` | `1` |
| `singularity-censorship-hyperbolicity` | `SINGULARITY-RESOLUTION-LEDGER.json` | `schemas/singularity-resolution-ledger.schema.json` | `singularity_rows` | `1` |
| `singularity-censorship-hyperbolicity` | `CENSORSHIP-HYPERBOLICITY-LEDGER.json` | `schemas/censorship-hyperbolicity-ledger.schema.json` | `censorship_rows` | `1` |
| `stress-energy-backreaction-conditions` | `STRESS-ENERGY-SOURCE-LEDGER.json` | `schemas/stress-energy-source-ledger.schema.json` | `source_rows` | `1` |
| `stress-energy-backreaction-conditions` | `SEMICLASSICAL-BACKREACTION-LEDGER.json` | `schemas/semiclassical-backreaction-ledger.schema.json` | `backreaction_rows` | `1` |
| `stress-energy-backreaction-conditions` | `ENERGY-CONDITION-LEDGER.json` | `schemas/energy-condition-ledger.schema.json` | `energy_condition_rows` | `1` |
| `classical-gr-recovery` | `EQUIVALENCE-PRINCIPLE-LEDGER.json` | `schemas/equivalence-principle-ledger.schema.json` | `equivalence_principle_rows` | `1` |
| `classical-gr-recovery` | `WEAK-FIELD-PPN-LEDGER.json` | `schemas/weak-field-ppn-ledger.schema.json` | `weak_field_ppn_rows` | `1` |
| `classical-gr-recovery` | `GRAVITATIONAL-RADIATION-LEDGER.json` | `schemas/gravitational-radiation-ledger.schema.json` | `radiation_rows` | `1` |
| `state-preparation-detector-decoherence` | `STATE-PREPARATION-LEDGER.json` | `schemas/state-preparation-ledger.schema.json` | `state_preparation_rows` | `1` |
| `state-preparation-detector-decoherence` | `DETECTOR-RESPONSE-LEDGER.json` | `schemas/detector-response-ledger.schema.json` | `detector_response_rows` | `1` |
| `state-preparation-detector-decoherence` | `DECOHERENCE-POINTER-LEDGER.json` | `schemas/decoherence-pointer-ledger.schema.json` | `decoherence_pointer_rows` | `1` |
| `asymptotic-ir-scattering` | `ASYMPTOTIC-STATE-LEDGER.json` | `schemas/asymptotic-state-ledger.schema.json` | `asymptotic_state_rows` | `1` |
| `asymptotic-ir-scattering` | `INFRARED-DRESSING-LEDGER.json` | `schemas/infrared-dressing-ledger.schema.json` | `infrared_dressing_rows` | `1` |
| `asymptotic-ir-scattering` | `SCATTERING-OBSERVABLE-LEDGER.json` | `schemas/scattering-observable-ledger.schema.json` | `scattering_observable_rows` | `1` |
| `discretization-finite-volume-continuum` | `DISCRETIZATION-REGIME-LEDGER.json` | `schemas/discretization-regime-ledger.schema.json` | `discretization_rows` | `1` |
| `discretization-finite-volume-continuum` | `FINITE-VOLUME-SCALING-LEDGER.json` | `schemas/finite-volume-scaling-ledger.schema.json` | `finite_volume_rows` | `1` |
| `discretization-finite-volume-continuum` | `CONTINUUM-EXTRAPOLATION-LEDGER.json` | `schemas/continuum-extrapolation-ledger.schema.json` | `continuum_extrapolation_rows` | `1` |
| `correlation-operator-bootstrap` | `CORRELATION-FUNCTION-LEDGER.json` | `schemas/correlation-function-ledger.schema.json` | `correlation_function_rows` | `1` |
| `correlation-operator-bootstrap` | `OPERATOR-INSERTION-LEDGER.json` | `schemas/operator-insertion-ledger.schema.json` | `operator_insertion_rows` | `1` |
| `correlation-operator-bootstrap` | `BOOTSTRAP-DATA-LEDGER.json` | `schemas/bootstrap-data-ledger.schema.json` | `bootstrap_data_rows` | `1` |
| `phase-order-universality` | `PHASE-STRUCTURE-LEDGER.json` | `schemas/phase-structure-ledger.schema.json` | `phase_structure_rows` | `1` |
| `phase-order-universality` | `ORDER-PARAMETER-LEDGER.json` | `schemas/order-parameter-ledger.schema.json` | `order_parameter_rows` | `1` |
| `phase-order-universality` | `UNIVERSALITY-CLASS-LEDGER.json` | `schemas/universality-class-ledger.schema.json` | `universality_class_rows` | `1` |
| `hilbert-representation-spectrum` | `HILBERT-SPACE-LEDGER.json` | `schemas/hilbert-space-ledger.schema.json` | `hilbert_space_rows` | `1` |
| `hilbert-representation-spectrum` | `REPRESENTATION-MAP-LEDGER.json` | `schemas/representation-map-ledger.schema.json` | `representation_map_rows` | `1` |
| `hilbert-representation-spectrum` | `SPECTRAL-RECONSTRUCTION-LEDGER.json` | `schemas/spectral-reconstruction-ledger.schema.json` | `spectral_reconstruction_rows` | `1` |

- Envelope failures: `0`

## Audit rule

Every registered ledger family must expose ledgers whose basic JSON envelope is reflected in its schema: `project`, `revision`, `schema_version`, `purpose`, and the primary row array. This audit is not a scientific authority source; it prevents schema drift and restart confusion.
