# Route-state summary (generated)

Generated from `CANDIDATE-ROUTE-STATE-LEDGER.json` plus `LEDGER-FAMILY-REGISTRY.json`. Do not edit directly; run `make index` after changing executable ledgers.

- Revision: `rev0298`
- Route rows: `13`
- Registered route-layer families: `38`
- Measurement-model rows: `14`
- Systematic-uncertainty rows: `14`
- Calibration-traceability rows: `14`
- Validity-domain rows: `14`
- Transportability rows: `14`
- Extrapolation-fence rows: `14`

## State counts

- `S1`: `2`
- `S2`: `9`
- `S3`: `2`

## Registered layer-family row counts

| Family | OQ | Ledgers | Ledger rows | Route fields | Policy | Max cardinality |
|---|---|---:|---:|---:|---|---:|
| `route-state-core` | `OQ-0057` | `3` | `45` | `1` | `nonempty-route-fields` | `` |
| `public-record-custody` | `OQ-0060` | `3` | `66` | `2` | `nonempty-route-fields` | `` |
| `defeat-rollback-severity` | `OQ-0061` | `3` | `40` | `3` | `nonempty-route-fields` | `` |
| `evidence-credit` | `OQ-0062` | `3` | `38` | `3` | `nonempty-route-fields` | `` |
| `contrast-update-prior` | `OQ-0063` | `3` | `41` | `3` | `cluster-local-plus-wrapper` | `2` |
| `measurement-systematics-calibration` | `OQ-0064` | `3` | `42` | `3` | `route-local-plus-wrapper` | `2` |
| `validity-transport-extrapolation` | `OQ-0065` | `3` | `42` | `3` | `route-local-plus-wrapper` | `2` |
| `causal-intervention-counterfactual` | `OQ-0066` | `3` | `42` | `3` | `route-local-plus-wrapper` | `2` |
| `selection-multiplicity-reporting` | `OQ-0067` | `3` | `42` | `3` | `route-local-plus-wrapper` | `2` |
| `capacity-complexity-generalization` | `OQ-0068` | `3` | `42` | `3` | `route-local-plus-wrapper` | `2` |
| `semantic-ontology-language` | `OQ-0069` | `3` | `42` | `3` | `route-local-plus-wrapper` | `2` |
| `social-review-consensus` | `OQ-0070` | `3` | `28` | `3` | `route-local-plus-wrapper` | `2` |
| `computational-numerical-software` | `OQ-0071` | `3` | `42` | `3` | `route-local-plus-wrapper` | `2` |
| `formal-proof-assumption-coverage` | `OQ-0072` | `3` | `42` | `3` | `route-local-plus-wrapper` | `2` |
| `idealization-approximation-limit` | `OQ-0073` | `3` | `42` | `3` | `route-local-plus-wrapper` | `2` |
| `boundary-initial-sector` | `OQ-0074` | `3` | `42` | `3` | `route-local-plus-wrapper` | `2` |
| `gauge-constraint-observable` | `OQ-0075` | `3` | `42` | `3` | `route-local-plus-wrapper` | `2` |
| `regularization-renormalization-matching` | `OQ-0076` | `3` | `42` | `3` | `route-local-plus-wrapper` | `2` |
| `composition-interface-global` | `OQ-0077` | `3` | `42` | `3` | `route-local-plus-wrapper` | `2` |
| `unitarity-causality-stability` | `OQ-0078` | `3` | `42` | `3` | `route-local-plus-wrapper` | `2` |
| `quantization-classical-semiclassical` | `OQ-0079` | `3` | `42` | `3` | `route-local-plus-wrapper` | `2` |
| `information-entropy-no-go` | `OQ-0080` | `3` | `42` | `3` | `route-local-plus-wrapper` | `2` |
| `symmetry-anomaly-conservation` | `OQ-0081` | `3` | `42` | `3` | `route-local-plus-wrapper` | `2` |
| `topology-dimension-signature` | `OQ-0082` | `3` | `42` | `3` | `route-local-plus-wrapper` | `2` |
| `measure-ensemble-typicality` | `OQ-0084` | `3` | `42` | `3` | `route-local-plus-wrapper` | `2` |
| `subsystem-algebra-edge-center` | `OQ-0083` | `3` | `42` | `3` | `route-local-plus-wrapper` | `2` |
| `matter-spectrum-coupling-mass` | `OQ-0085` | `3` | `42` | `3` | `route-local-plus-wrapper` | `2` |
| `cosmological-background-vacuum-history` | `OQ-0086` | `3` | `42` | `3` | `route-local-plus-wrapper` | `2` |
| `black-hole-horizon-thermodynamics-evaporation` | `OQ-0087` | `3` | `42` | `3` | `route-local-plus-wrapper` | `2` |
| `singularity-censorship-hyperbolicity` | `OQ-0088` | `3` | `0` | `3` | `route-local-plus-wrapper` | `2` |
| `stress-energy-backreaction-conditions` | `OQ-0089` | `3` | `0` | `3` | `route-local-plus-wrapper` | `2` |
| `classical-gr-recovery` | `OQ-0090` | `3` | `0` | `3` | `route-local-plus-wrapper` | `2` |
| `state-preparation-detector-decoherence` | `OQ-0091` | `3` | `0` | `3` | `route-local-plus-wrapper` | `2` |
| `asymptotic-ir-scattering` | `OQ-0092` | `3` | `0` | `3` | `route-local-plus-wrapper` | `2` |
| `discretization-finite-volume-continuum` | `OQ-0093` | `3` | `0` | `3` | `route-local-plus-wrapper` | `2` |
| `correlation-operator-bootstrap` | `OQ-0094` | `3` | `0` | `3` | `route-local-plus-wrapper` | `2` |
| `phase-order-universality` | `OQ-0095` | `3` | `0` | `3` | `route-local-plus-wrapper` | `2` |
| `hilbert-representation-spectrum` | `OQ-0096` | `3` | `0` | `3` | `route-local-plus-wrapper` | `2` |

## Route rows by registered layer family

### `R-OQ0057-FAMILYC-EW-CODE`

- State: `S3`
- Ceiling: `S3`
- Earliest blocker: public bridge and cross-package target quotient

| Family | Route-field counts |
|---|---:|
| `route-state-core` | `promotion_gate_ids` = `2` |
| `public-record-custody` | `public_record_carrier_ids` = `3`; `acquisition_protocol_ids` = `2` |
| `defeat-rollback-severity` | `defeater_ids` = `6`; `rollback_rule_ids` = `6`; `severity_test_ids` = `1` |
| `evidence-credit` | `evidence_unit_ids` = `2`; `independence_assumption_ids` = `4`; `credit_allocation_ids` = `1` |
| `contrast-update-prior` | `contrast_class_ids` = `1`; `likelihood_update_ids` = `1`; `prior_sensitivity_ids` = `1` |
| `measurement-systematics-calibration` | `measurement_model_ids` = `2`; `systematic_uncertainty_ids` = `2`; `calibration_traceability_ids` = `2` |
| `validity-transport-extrapolation` | `validity_domain_ids` = `2`; `transportability_ids` = `2`; `extrapolation_fence_ids` = `2` |
| `causal-intervention-counterfactual` | `causal_mechanism_ids` = `2`; `intervention_protocol_ids` = `2`; `counterfactual_robustness_ids` = `2` |
| `selection-multiplicity-reporting` | `selection_function_ids` = `2`; `multiplicity_control_ids` = `2`; `reporting_bias_ids` = `2` |
| `capacity-complexity-generalization` | `model_capacity_ids` = `2`; `complexity_penalty_ids` = `2`; `generalization_validation_ids` = `2` |
| `semantic-ontology-language` | `semantic_term_ids` = `2`; `ontology_commitment_ids` = `2`; `claim_language_permission_ids` = `2` |
| `social-review-consensus` | `social_authority_ids` = `2`; `review_replication_ids` = `2`; `consensus_elicitation_ids` = `2` |
| `computational-numerical-software` | `computational_reproducibility_ids` = `2`; `numerical_stability_ids` = `2`; `software_supply_chain_ids` = `2` |
| `formal-proof-assumption-coverage` | `proof_obligation_ids` = `2`; `assumption_discharge_ids` = `2`; `formalization_coverage_ids` = `2` |
| `idealization-approximation-limit` | `idealization_ids` = `2`; `approximation_error_ids` = `2`; `limit_interchange_ids` = `2` |
| `boundary-initial-sector` | `boundary_condition_ids` = `2`; `initial_data_ids` = `2`; `sector_selection_ids` = `2` |
| `gauge-constraint-observable` | `gauge_symmetry_ids` = `2`; `constraint_closure_ids` = `2`; `observable_quotient_ids` = `2` |
| `regularization-renormalization-matching` | `regularization_scheme_ids` = `2`; `renormalization_flow_ids` = `2`; `matching_condition_ids` = `2` |
| `composition-interface-global` | `composition_law_ids` = `2`; `interface_compatibility_ids` = `2`; `global_consistency_ids` = `2` |
| `unitarity-causality-stability` | `unitarity_check_ids` = `2`; `causality_cone_ids` = `2`; `stability_positivity_ids` = `2` |
| `quantization-classical-semiclassical` | `quantization_map_ids` = `2`; `classical_limit_ids` = `2`; `semiclassical_correspondence_ids` = `2` |
| `information-entropy-no-go` | `information_flow_ids` = `2`; `entropy_accounting_ids` = `2`; `no_go_compliance_ids` = `2` |
| `symmetry-anomaly-conservation` | `symmetry_realization_ids` = `2`; `anomaly_matching_ids` = `2`; `conservation_law_ids` = `2` |
| `topology-dimension-signature` | `spacetime_topology_ids` = `2`; `dimension_realization_ids` = `2`; `signature_structure_ids` = `2` |
| `measure-ensemble-typicality` | `measure_definition_ids` = `2`; `ensemble_sampling_ids` = `2`; `typicality_weighting_ids` = `2` |
| `subsystem-algebra-edge-center` | `algebraic_locality_ids` = `2`; `subsystem_factorization_ids` = `2`; `edge_mode_center_ids` = `2` |
| `matter-spectrum-coupling-mass` | `particle_spectrum_ids` = `2`; `interaction_coupling_ids` = `2`; `mass_hierarchy_ids` = `2` |
| `cosmological-background-vacuum-history` | `cosmological_background_ids` = `2`; `vacuum_energy_ids` = `2`; `thermal_history_ids` = `2` |
| `black-hole-horizon-thermodynamics-evaporation` | `horizon_structure_ids` = `2`; `black_hole_thermodynamics_ids` = `2`; `evaporation_radiation_ids` = `2` |
| `singularity-censorship-hyperbolicity` | `curvature_regime_ids` = `2`; `singularity_resolution_ids` = `2`; `censorship_hyperbolicity_ids` = `2` |
| `stress-energy-backreaction-conditions` | `stress_energy_source_ids` = `2`; `backreaction_consistency_ids` = `2`; `energy_condition_ids` = `2` |
| `classical-gr-recovery` | `equivalence_principle_ids` = `2`; `weak_field_ppn_ids` = `2`; `gravitational_radiation_ids` = `2` |
| `state-preparation-detector-decoherence` | `state_preparation_ids` = `2`; `detector_response_ids` = `2`; `decoherence_pointer_ids` = `2` |
| `asymptotic-ir-scattering` | `asymptotic_state_ids` = `2`; `infrared_dressing_ids` = `2`; `scattering_observable_ids` = `2` |
| `discretization-finite-volume-continuum` | `discretization_regime_ids` = `2`; `finite_volume_scaling_ids` = `2`; `continuum_extrapolation_ids` = `2` |
| `correlation-operator-bootstrap` | `correlation_function_ids` = `2`; `operator_insertion_ids` = `2`; `bootstrap_data_ids` = `2` |
| `phase-order-universality` | `phase_structure_ids` = `2`; `order_parameter_ids` = `2`; `universality_class_ids` = `2` |
| `hilbert-representation-spectrum` | `hilbert_space_ids` = `2`; `representation_map_ids` = `2`; `spectral_reconstruction_ids` = `2` |

### `R-OQ0057-FAMILYC-LEARNED-INVERSE`

- State: `S2`
- Ceiling: `S2`
- Earliest blocker: surrogate target and route-local publicness

| Family | Route-field counts |
|---|---:|
| `route-state-core` | `promotion_gate_ids` = `3` |
| `public-record-custody` | `public_record_carrier_ids` = `3`; `acquisition_protocol_ids` = `1` |
| `defeat-rollback-severity` | `defeater_ids` = `4`; `rollback_rule_ids` = `4`; `severity_test_ids` = `1` |
| `evidence-credit` | `evidence_unit_ids` = `2`; `independence_assumption_ids` = `3`; `credit_allocation_ids` = `1` |
| `contrast-update-prior` | `contrast_class_ids` = `1`; `likelihood_update_ids` = `1`; `prior_sensitivity_ids` = `2` |
| `measurement-systematics-calibration` | `measurement_model_ids` = `2`; `systematic_uncertainty_ids` = `2`; `calibration_traceability_ids` = `2` |
| `validity-transport-extrapolation` | `validity_domain_ids` = `2`; `transportability_ids` = `2`; `extrapolation_fence_ids` = `2` |
| `causal-intervention-counterfactual` | `causal_mechanism_ids` = `2`; `intervention_protocol_ids` = `2`; `counterfactual_robustness_ids` = `2` |
| `selection-multiplicity-reporting` | `selection_function_ids` = `2`; `multiplicity_control_ids` = `2`; `reporting_bias_ids` = `2` |
| `capacity-complexity-generalization` | `model_capacity_ids` = `2`; `complexity_penalty_ids` = `2`; `generalization_validation_ids` = `2` |
| `semantic-ontology-language` | `semantic_term_ids` = `2`; `ontology_commitment_ids` = `2`; `claim_language_permission_ids` = `2` |
| `social-review-consensus` | `social_authority_ids` = `2`; `review_replication_ids` = `2`; `consensus_elicitation_ids` = `2` |
| `computational-numerical-software` | `computational_reproducibility_ids` = `2`; `numerical_stability_ids` = `2`; `software_supply_chain_ids` = `2` |
| `formal-proof-assumption-coverage` | `proof_obligation_ids` = `2`; `assumption_discharge_ids` = `2`; `formalization_coverage_ids` = `2` |
| `idealization-approximation-limit` | `idealization_ids` = `2`; `approximation_error_ids` = `2`; `limit_interchange_ids` = `2` |
| `boundary-initial-sector` | `boundary_condition_ids` = `2`; `initial_data_ids` = `2`; `sector_selection_ids` = `2` |
| `gauge-constraint-observable` | `gauge_symmetry_ids` = `2`; `constraint_closure_ids` = `2`; `observable_quotient_ids` = `2` |
| `regularization-renormalization-matching` | `regularization_scheme_ids` = `2`; `renormalization_flow_ids` = `2`; `matching_condition_ids` = `2` |
| `composition-interface-global` | `composition_law_ids` = `2`; `interface_compatibility_ids` = `2`; `global_consistency_ids` = `2` |
| `unitarity-causality-stability` | `unitarity_check_ids` = `2`; `causality_cone_ids` = `2`; `stability_positivity_ids` = `2` |
| `quantization-classical-semiclassical` | `quantization_map_ids` = `2`; `classical_limit_ids` = `2`; `semiclassical_correspondence_ids` = `2` |
| `information-entropy-no-go` | `information_flow_ids` = `2`; `entropy_accounting_ids` = `2`; `no_go_compliance_ids` = `2` |
| `symmetry-anomaly-conservation` | `symmetry_realization_ids` = `2`; `anomaly_matching_ids` = `2`; `conservation_law_ids` = `2` |
| `topology-dimension-signature` | `spacetime_topology_ids` = `2`; `dimension_realization_ids` = `2`; `signature_structure_ids` = `2` |
| `measure-ensemble-typicality` | `measure_definition_ids` = `2`; `ensemble_sampling_ids` = `2`; `typicality_weighting_ids` = `2` |
| `subsystem-algebra-edge-center` | `algebraic_locality_ids` = `2`; `subsystem_factorization_ids` = `2`; `edge_mode_center_ids` = `2` |
| `matter-spectrum-coupling-mass` | `particle_spectrum_ids` = `2`; `interaction_coupling_ids` = `2`; `mass_hierarchy_ids` = `2` |
| `cosmological-background-vacuum-history` | `cosmological_background_ids` = `2`; `vacuum_energy_ids` = `2`; `thermal_history_ids` = `2` |
| `black-hole-horizon-thermodynamics-evaporation` | `horizon_structure_ids` = `2`; `black_hole_thermodynamics_ids` = `2`; `evaporation_radiation_ids` = `2` |
| `singularity-censorship-hyperbolicity` | `curvature_regime_ids` = `2`; `singularity_resolution_ids` = `2`; `censorship_hyperbolicity_ids` = `2` |
| `stress-energy-backreaction-conditions` | `stress_energy_source_ids` = `2`; `backreaction_consistency_ids` = `2`; `energy_condition_ids` = `2` |
| `classical-gr-recovery` | `equivalence_principle_ids` = `2`; `weak_field_ppn_ids` = `2`; `gravitational_radiation_ids` = `2` |
| `state-preparation-detector-decoherence` | `state_preparation_ids` = `2`; `detector_response_ids` = `2`; `decoherence_pointer_ids` = `2` |
| `asymptotic-ir-scattering` | `asymptotic_state_ids` = `2`; `infrared_dressing_ids` = `2`; `scattering_observable_ids` = `2` |
| `discretization-finite-volume-continuum` | `discretization_regime_ids` = `2`; `finite_volume_scaling_ids` = `2`; `continuum_extrapolation_ids` = `2` |
| `correlation-operator-bootstrap` | `correlation_function_ids` = `2`; `operator_insertion_ids` = `2`; `bootstrap_data_ids` = `2` |
| `phase-order-universality` | `phase_structure_ids` = `2`; `order_parameter_ids` = `2`; `universality_class_ids` = `2` |
| `hilbert-representation-spectrum` | `hilbert_space_ids` = `2`; `representation_map_ids` = `2`; `spectral_reconstruction_ids` = `2` |

### `R-OQ0057-FAMILYB-THERMO-ENTROPIC`

- State: `S1`
- Ceiling: `S1`
- Earliest blocker: missing candidate-native target and inverse map

| Family | Route-field counts |
|---|---:|
| `route-state-core` | `promotion_gate_ids` = `4` |
| `public-record-custody` | `public_record_carrier_ids` = `2`; `acquisition_protocol_ids` = `1` |
| `defeat-rollback-severity` | `defeater_ids` = `2`; `rollback_rule_ids` = `2`; `severity_test_ids` = `1` |
| `evidence-credit` | `evidence_unit_ids` = `2`; `independence_assumption_ids` = `2`; `credit_allocation_ids` = `1` |
| `contrast-update-prior` | `contrast_class_ids` = `1`; `likelihood_update_ids` = `1`; `prior_sensitivity_ids` = `1` |
| `measurement-systematics-calibration` | `measurement_model_ids` = `2`; `systematic_uncertainty_ids` = `2`; `calibration_traceability_ids` = `2` |
| `validity-transport-extrapolation` | `validity_domain_ids` = `2`; `transportability_ids` = `2`; `extrapolation_fence_ids` = `2` |
| `causal-intervention-counterfactual` | `causal_mechanism_ids` = `2`; `intervention_protocol_ids` = `2`; `counterfactual_robustness_ids` = `2` |
| `selection-multiplicity-reporting` | `selection_function_ids` = `2`; `multiplicity_control_ids` = `2`; `reporting_bias_ids` = `2` |
| `capacity-complexity-generalization` | `model_capacity_ids` = `2`; `complexity_penalty_ids` = `2`; `generalization_validation_ids` = `2` |
| `semantic-ontology-language` | `semantic_term_ids` = `2`; `ontology_commitment_ids` = `2`; `claim_language_permission_ids` = `2` |
| `social-review-consensus` | `social_authority_ids` = `2`; `review_replication_ids` = `2`; `consensus_elicitation_ids` = `2` |
| `computational-numerical-software` | `computational_reproducibility_ids` = `2`; `numerical_stability_ids` = `2`; `software_supply_chain_ids` = `2` |
| `formal-proof-assumption-coverage` | `proof_obligation_ids` = `2`; `assumption_discharge_ids` = `2`; `formalization_coverage_ids` = `2` |
| `idealization-approximation-limit` | `idealization_ids` = `2`; `approximation_error_ids` = `2`; `limit_interchange_ids` = `2` |
| `boundary-initial-sector` | `boundary_condition_ids` = `2`; `initial_data_ids` = `2`; `sector_selection_ids` = `2` |
| `gauge-constraint-observable` | `gauge_symmetry_ids` = `2`; `constraint_closure_ids` = `2`; `observable_quotient_ids` = `2` |
| `regularization-renormalization-matching` | `regularization_scheme_ids` = `2`; `renormalization_flow_ids` = `2`; `matching_condition_ids` = `2` |
| `composition-interface-global` | `composition_law_ids` = `2`; `interface_compatibility_ids` = `2`; `global_consistency_ids` = `2` |
| `unitarity-causality-stability` | `unitarity_check_ids` = `2`; `causality_cone_ids` = `2`; `stability_positivity_ids` = `2` |
| `quantization-classical-semiclassical` | `quantization_map_ids` = `2`; `classical_limit_ids` = `2`; `semiclassical_correspondence_ids` = `2` |
| `information-entropy-no-go` | `information_flow_ids` = `2`; `entropy_accounting_ids` = `2`; `no_go_compliance_ids` = `2` |
| `symmetry-anomaly-conservation` | `symmetry_realization_ids` = `2`; `anomaly_matching_ids` = `2`; `conservation_law_ids` = `2` |
| `topology-dimension-signature` | `spacetime_topology_ids` = `2`; `dimension_realization_ids` = `2`; `signature_structure_ids` = `2` |
| `measure-ensemble-typicality` | `measure_definition_ids` = `2`; `ensemble_sampling_ids` = `2`; `typicality_weighting_ids` = `2` |
| `subsystem-algebra-edge-center` | `algebraic_locality_ids` = `2`; `subsystem_factorization_ids` = `2`; `edge_mode_center_ids` = `2` |
| `matter-spectrum-coupling-mass` | `particle_spectrum_ids` = `2`; `interaction_coupling_ids` = `2`; `mass_hierarchy_ids` = `2` |
| `cosmological-background-vacuum-history` | `cosmological_background_ids` = `2`; `vacuum_energy_ids` = `2`; `thermal_history_ids` = `2` |
| `black-hole-horizon-thermodynamics-evaporation` | `horizon_structure_ids` = `2`; `black_hole_thermodynamics_ids` = `2`; `evaporation_radiation_ids` = `2` |
| `singularity-censorship-hyperbolicity` | `curvature_regime_ids` = `2`; `singularity_resolution_ids` = `2`; `censorship_hyperbolicity_ids` = `2` |
| `stress-energy-backreaction-conditions` | `stress_energy_source_ids` = `2`; `backreaction_consistency_ids` = `2`; `energy_condition_ids` = `2` |
| `classical-gr-recovery` | `equivalence_principle_ids` = `2`; `weak_field_ppn_ids` = `2`; `gravitational_radiation_ids` = `2` |
| `state-preparation-detector-decoherence` | `state_preparation_ids` = `2`; `detector_response_ids` = `2`; `decoherence_pointer_ids` = `2` |
| `asymptotic-ir-scattering` | `asymptotic_state_ids` = `2`; `infrared_dressing_ids` = `2`; `scattering_observable_ids` = `2` |
| `discretization-finite-volume-continuum` | `discretization_regime_ids` = `2`; `finite_volume_scaling_ids` = `2`; `continuum_extrapolation_ids` = `2` |
| `correlation-operator-bootstrap` | `correlation_function_ids` = `2`; `operator_insertion_ids` = `2`; `bootstrap_data_ids` = `2` |
| `phase-order-universality` | `phase_structure_ids` = `2`; `order_parameter_ids` = `2`; `universality_class_ids` = `2` |
| `hilbert-representation-spectrum` | `hilbert_space_ids` = `2`; `representation_map_ids` = `2`; `spectral_reconstruction_ids` = `2` |

### `R-OQ0057-STRINGM-ATLAS`

- State: `S2`
- Ceiling: `S2`
- Earliest blocker: observed-sector inverse and vacuum/duality quotient

| Family | Route-field counts |
|---|---:|
| `route-state-core` | `promotion_gate_ids` = `3` |
| `public-record-custody` | `public_record_carrier_ids` = `3`; `acquisition_protocol_ids` = `2` |
| `defeat-rollback-severity` | `defeater_ids` = `4`; `rollback_rule_ids` = `4`; `severity_test_ids` = `1` |
| `evidence-credit` | `evidence_unit_ids` = `2`; `independence_assumption_ids` = `3`; `credit_allocation_ids` = `1` |
| `contrast-update-prior` | `contrast_class_ids` = `1`; `likelihood_update_ids` = `1`; `prior_sensitivity_ids` = `1` |
| `measurement-systematics-calibration` | `measurement_model_ids` = `2`; `systematic_uncertainty_ids` = `2`; `calibration_traceability_ids` = `2` |
| `validity-transport-extrapolation` | `validity_domain_ids` = `2`; `transportability_ids` = `2`; `extrapolation_fence_ids` = `2` |
| `causal-intervention-counterfactual` | `causal_mechanism_ids` = `2`; `intervention_protocol_ids` = `2`; `counterfactual_robustness_ids` = `2` |
| `selection-multiplicity-reporting` | `selection_function_ids` = `2`; `multiplicity_control_ids` = `2`; `reporting_bias_ids` = `2` |
| `capacity-complexity-generalization` | `model_capacity_ids` = `2`; `complexity_penalty_ids` = `2`; `generalization_validation_ids` = `2` |
| `semantic-ontology-language` | `semantic_term_ids` = `2`; `ontology_commitment_ids` = `2`; `claim_language_permission_ids` = `2` |
| `social-review-consensus` | `social_authority_ids` = `2`; `review_replication_ids` = `2`; `consensus_elicitation_ids` = `2` |
| `computational-numerical-software` | `computational_reproducibility_ids` = `2`; `numerical_stability_ids` = `2`; `software_supply_chain_ids` = `2` |
| `formal-proof-assumption-coverage` | `proof_obligation_ids` = `2`; `assumption_discharge_ids` = `2`; `formalization_coverage_ids` = `2` |
| `idealization-approximation-limit` | `idealization_ids` = `2`; `approximation_error_ids` = `2`; `limit_interchange_ids` = `2` |
| `boundary-initial-sector` | `boundary_condition_ids` = `2`; `initial_data_ids` = `2`; `sector_selection_ids` = `2` |
| `gauge-constraint-observable` | `gauge_symmetry_ids` = `2`; `constraint_closure_ids` = `2`; `observable_quotient_ids` = `2` |
| `regularization-renormalization-matching` | `regularization_scheme_ids` = `2`; `renormalization_flow_ids` = `2`; `matching_condition_ids` = `2` |
| `composition-interface-global` | `composition_law_ids` = `2`; `interface_compatibility_ids` = `2`; `global_consistency_ids` = `2` |
| `unitarity-causality-stability` | `unitarity_check_ids` = `2`; `causality_cone_ids` = `2`; `stability_positivity_ids` = `2` |
| `quantization-classical-semiclassical` | `quantization_map_ids` = `2`; `classical_limit_ids` = `2`; `semiclassical_correspondence_ids` = `2` |
| `information-entropy-no-go` | `information_flow_ids` = `2`; `entropy_accounting_ids` = `2`; `no_go_compliance_ids` = `2` |
| `symmetry-anomaly-conservation` | `symmetry_realization_ids` = `2`; `anomaly_matching_ids` = `2`; `conservation_law_ids` = `2` |
| `topology-dimension-signature` | `spacetime_topology_ids` = `2`; `dimension_realization_ids` = `2`; `signature_structure_ids` = `2` |
| `measure-ensemble-typicality` | `measure_definition_ids` = `2`; `ensemble_sampling_ids` = `2`; `typicality_weighting_ids` = `2` |
| `subsystem-algebra-edge-center` | `algebraic_locality_ids` = `2`; `subsystem_factorization_ids` = `2`; `edge_mode_center_ids` = `2` |
| `matter-spectrum-coupling-mass` | `particle_spectrum_ids` = `2`; `interaction_coupling_ids` = `2`; `mass_hierarchy_ids` = `2` |
| `cosmological-background-vacuum-history` | `cosmological_background_ids` = `2`; `vacuum_energy_ids` = `2`; `thermal_history_ids` = `2` |
| `black-hole-horizon-thermodynamics-evaporation` | `horizon_structure_ids` = `2`; `black_hole_thermodynamics_ids` = `2`; `evaporation_radiation_ids` = `2` |
| `singularity-censorship-hyperbolicity` | `curvature_regime_ids` = `2`; `singularity_resolution_ids` = `2`; `censorship_hyperbolicity_ids` = `2` |
| `stress-energy-backreaction-conditions` | `stress_energy_source_ids` = `2`; `backreaction_consistency_ids` = `2`; `energy_condition_ids` = `2` |
| `classical-gr-recovery` | `equivalence_principle_ids` = `2`; `weak_field_ppn_ids` = `2`; `gravitational_radiation_ids` = `2` |
| `state-preparation-detector-decoherence` | `state_preparation_ids` = `2`; `detector_response_ids` = `2`; `decoherence_pointer_ids` = `2` |
| `asymptotic-ir-scattering` | `asymptotic_state_ids` = `2`; `infrared_dressing_ids` = `2`; `scattering_observable_ids` = `2` |
| `discretization-finite-volume-continuum` | `discretization_regime_ids` = `2`; `finite_volume_scaling_ids` = `2`; `continuum_extrapolation_ids` = `2` |
| `correlation-operator-bootstrap` | `correlation_function_ids` = `2`; `operator_insertion_ids` = `2`; `bootstrap_data_ids` = `2` |
| `phase-order-universality` | `phase_structure_ids` = `2`; `order_parameter_ids` = `2`; `universality_class_ids` = `2` |
| `hilbert-representation-spectrum` | `hilbert_space_ids` = `2`; `representation_map_ids` = `2`; `spectral_reconstruction_ids` = `2` |

### `R-OQ0057-ASYMPTOTIC-SAFETY`

- State: `S2`
- Ceiling: `S2`
- Earliest blocker: truncation/regulator independence and observed-sector cash-out

| Family | Route-field counts |
|---|---:|
| `route-state-core` | `promotion_gate_ids` = `3` |
| `public-record-custody` | `public_record_carrier_ids` = `3`; `acquisition_protocol_ids` = `2` |
| `defeat-rollback-severity` | `defeater_ids` = `3`; `rollback_rule_ids` = `3`; `severity_test_ids` = `1` |
| `evidence-credit` | `evidence_unit_ids` = `2`; `independence_assumption_ids` = `3`; `credit_allocation_ids` = `1` |
| `contrast-update-prior` | `contrast_class_ids` = `1`; `likelihood_update_ids` = `1`; `prior_sensitivity_ids` = `1` |
| `measurement-systematics-calibration` | `measurement_model_ids` = `2`; `systematic_uncertainty_ids` = `2`; `calibration_traceability_ids` = `2` |
| `validity-transport-extrapolation` | `validity_domain_ids` = `2`; `transportability_ids` = `2`; `extrapolation_fence_ids` = `2` |
| `causal-intervention-counterfactual` | `causal_mechanism_ids` = `2`; `intervention_protocol_ids` = `2`; `counterfactual_robustness_ids` = `2` |
| `selection-multiplicity-reporting` | `selection_function_ids` = `2`; `multiplicity_control_ids` = `2`; `reporting_bias_ids` = `2` |
| `capacity-complexity-generalization` | `model_capacity_ids` = `2`; `complexity_penalty_ids` = `2`; `generalization_validation_ids` = `2` |
| `semantic-ontology-language` | `semantic_term_ids` = `2`; `ontology_commitment_ids` = `2`; `claim_language_permission_ids` = `2` |
| `social-review-consensus` | `social_authority_ids` = `2`; `review_replication_ids` = `2`; `consensus_elicitation_ids` = `2` |
| `computational-numerical-software` | `computational_reproducibility_ids` = `2`; `numerical_stability_ids` = `2`; `software_supply_chain_ids` = `2` |
| `formal-proof-assumption-coverage` | `proof_obligation_ids` = `2`; `assumption_discharge_ids` = `2`; `formalization_coverage_ids` = `2` |
| `idealization-approximation-limit` | `idealization_ids` = `2`; `approximation_error_ids` = `2`; `limit_interchange_ids` = `2` |
| `boundary-initial-sector` | `boundary_condition_ids` = `2`; `initial_data_ids` = `2`; `sector_selection_ids` = `2` |
| `gauge-constraint-observable` | `gauge_symmetry_ids` = `2`; `constraint_closure_ids` = `2`; `observable_quotient_ids` = `2` |
| `regularization-renormalization-matching` | `regularization_scheme_ids` = `2`; `renormalization_flow_ids` = `2`; `matching_condition_ids` = `2` |
| `composition-interface-global` | `composition_law_ids` = `2`; `interface_compatibility_ids` = `2`; `global_consistency_ids` = `2` |
| `unitarity-causality-stability` | `unitarity_check_ids` = `2`; `causality_cone_ids` = `2`; `stability_positivity_ids` = `2` |
| `quantization-classical-semiclassical` | `quantization_map_ids` = `2`; `classical_limit_ids` = `2`; `semiclassical_correspondence_ids` = `2` |
| `information-entropy-no-go` | `information_flow_ids` = `2`; `entropy_accounting_ids` = `2`; `no_go_compliance_ids` = `2` |
| `symmetry-anomaly-conservation` | `symmetry_realization_ids` = `2`; `anomaly_matching_ids` = `2`; `conservation_law_ids` = `2` |
| `topology-dimension-signature` | `spacetime_topology_ids` = `2`; `dimension_realization_ids` = `2`; `signature_structure_ids` = `2` |
| `measure-ensemble-typicality` | `measure_definition_ids` = `2`; `ensemble_sampling_ids` = `2`; `typicality_weighting_ids` = `2` |
| `subsystem-algebra-edge-center` | `algebraic_locality_ids` = `2`; `subsystem_factorization_ids` = `2`; `edge_mode_center_ids` = `2` |
| `matter-spectrum-coupling-mass` | `particle_spectrum_ids` = `2`; `interaction_coupling_ids` = `2`; `mass_hierarchy_ids` = `2` |
| `cosmological-background-vacuum-history` | `cosmological_background_ids` = `2`; `vacuum_energy_ids` = `2`; `thermal_history_ids` = `2` |
| `black-hole-horizon-thermodynamics-evaporation` | `horizon_structure_ids` = `2`; `black_hole_thermodynamics_ids` = `2`; `evaporation_radiation_ids` = `2` |
| `singularity-censorship-hyperbolicity` | `curvature_regime_ids` = `2`; `singularity_resolution_ids` = `2`; `censorship_hyperbolicity_ids` = `2` |
| `stress-energy-backreaction-conditions` | `stress_energy_source_ids` = `2`; `backreaction_consistency_ids` = `2`; `energy_condition_ids` = `2` |
| `classical-gr-recovery` | `equivalence_principle_ids` = `2`; `weak_field_ppn_ids` = `2`; `gravitational_radiation_ids` = `2` |
| `state-preparation-detector-decoherence` | `state_preparation_ids` = `2`; `detector_response_ids` = `2`; `decoherence_pointer_ids` = `2` |
| `asymptotic-ir-scattering` | `asymptotic_state_ids` = `2`; `infrared_dressing_ids` = `2`; `scattering_observable_ids` = `2` |
| `discretization-finite-volume-continuum` | `discretization_regime_ids` = `2`; `finite_volume_scaling_ids` = `2`; `continuum_extrapolation_ids` = `2` |
| `correlation-operator-bootstrap` | `correlation_function_ids` = `2`; `operator_insertion_ids` = `2`; `bootstrap_data_ids` = `2` |
| `phase-order-universality` | `phase_structure_ids` = `2`; `order_parameter_ids` = `2`; `universality_class_ids` = `2` |
| `hilbert-representation-spectrum` | `hilbert_space_ids` = `2`; `representation_map_ids` = `2`; `spectral_reconstruction_ids` = `2` |

### `R-OQ0057-CAUSAL-SET`

- State: `S1`
- Ceiling: `S2`
- Earliest blocker: native quantum dynamics and inverse from public records

| Family | Route-field counts |
|---|---:|
| `route-state-core` | `promotion_gate_ids` = `4` |
| `public-record-custody` | `public_record_carrier_ids` = `3`; `acquisition_protocol_ids` = `1` |
| `defeat-rollback-severity` | `defeater_ids` = `3`; `rollback_rule_ids` = `3`; `severity_test_ids` = `1` |
| `evidence-credit` | `evidence_unit_ids` = `2`; `independence_assumption_ids` = `2`; `credit_allocation_ids` = `1` |
| `contrast-update-prior` | `contrast_class_ids` = `1`; `likelihood_update_ids` = `1`; `prior_sensitivity_ids` = `1` |
| `measurement-systematics-calibration` | `measurement_model_ids` = `2`; `systematic_uncertainty_ids` = `2`; `calibration_traceability_ids` = `2` |
| `validity-transport-extrapolation` | `validity_domain_ids` = `2`; `transportability_ids` = `2`; `extrapolation_fence_ids` = `2` |
| `causal-intervention-counterfactual` | `causal_mechanism_ids` = `2`; `intervention_protocol_ids` = `2`; `counterfactual_robustness_ids` = `2` |
| `selection-multiplicity-reporting` | `selection_function_ids` = `2`; `multiplicity_control_ids` = `2`; `reporting_bias_ids` = `2` |
| `capacity-complexity-generalization` | `model_capacity_ids` = `2`; `complexity_penalty_ids` = `2`; `generalization_validation_ids` = `2` |
| `semantic-ontology-language` | `semantic_term_ids` = `2`; `ontology_commitment_ids` = `2`; `claim_language_permission_ids` = `2` |
| `social-review-consensus` | `social_authority_ids` = `2`; `review_replication_ids` = `2`; `consensus_elicitation_ids` = `2` |
| `computational-numerical-software` | `computational_reproducibility_ids` = `2`; `numerical_stability_ids` = `2`; `software_supply_chain_ids` = `2` |
| `formal-proof-assumption-coverage` | `proof_obligation_ids` = `2`; `assumption_discharge_ids` = `2`; `formalization_coverage_ids` = `2` |
| `idealization-approximation-limit` | `idealization_ids` = `2`; `approximation_error_ids` = `2`; `limit_interchange_ids` = `2` |
| `boundary-initial-sector` | `boundary_condition_ids` = `2`; `initial_data_ids` = `2`; `sector_selection_ids` = `2` |
| `gauge-constraint-observable` | `gauge_symmetry_ids` = `2`; `constraint_closure_ids` = `2`; `observable_quotient_ids` = `2` |
| `regularization-renormalization-matching` | `regularization_scheme_ids` = `2`; `renormalization_flow_ids` = `2`; `matching_condition_ids` = `2` |
| `composition-interface-global` | `composition_law_ids` = `2`; `interface_compatibility_ids` = `2`; `global_consistency_ids` = `2` |
| `unitarity-causality-stability` | `unitarity_check_ids` = `2`; `causality_cone_ids` = `2`; `stability_positivity_ids` = `2` |
| `quantization-classical-semiclassical` | `quantization_map_ids` = `2`; `classical_limit_ids` = `2`; `semiclassical_correspondence_ids` = `2` |
| `information-entropy-no-go` | `information_flow_ids` = `2`; `entropy_accounting_ids` = `2`; `no_go_compliance_ids` = `2` |
| `symmetry-anomaly-conservation` | `symmetry_realization_ids` = `2`; `anomaly_matching_ids` = `2`; `conservation_law_ids` = `2` |
| `topology-dimension-signature` | `spacetime_topology_ids` = `2`; `dimension_realization_ids` = `2`; `signature_structure_ids` = `2` |
| `measure-ensemble-typicality` | `measure_definition_ids` = `2`; `ensemble_sampling_ids` = `2`; `typicality_weighting_ids` = `2` |
| `subsystem-algebra-edge-center` | `algebraic_locality_ids` = `2`; `subsystem_factorization_ids` = `2`; `edge_mode_center_ids` = `2` |
| `matter-spectrum-coupling-mass` | `particle_spectrum_ids` = `2`; `interaction_coupling_ids` = `2`; `mass_hierarchy_ids` = `2` |
| `cosmological-background-vacuum-history` | `cosmological_background_ids` = `2`; `vacuum_energy_ids` = `2`; `thermal_history_ids` = `2` |
| `black-hole-horizon-thermodynamics-evaporation` | `horizon_structure_ids` = `2`; `black_hole_thermodynamics_ids` = `2`; `evaporation_radiation_ids` = `2` |
| `singularity-censorship-hyperbolicity` | `curvature_regime_ids` = `2`; `singularity_resolution_ids` = `2`; `censorship_hyperbolicity_ids` = `2` |
| `stress-energy-backreaction-conditions` | `stress_energy_source_ids` = `2`; `backreaction_consistency_ids` = `2`; `energy_condition_ids` = `2` |
| `classical-gr-recovery` | `equivalence_principle_ids` = `2`; `weak_field_ppn_ids` = `2`; `gravitational_radiation_ids` = `2` |
| `state-preparation-detector-decoherence` | `state_preparation_ids` = `2`; `detector_response_ids` = `2`; `decoherence_pointer_ids` = `2` |
| `asymptotic-ir-scattering` | `asymptotic_state_ids` = `2`; `infrared_dressing_ids` = `2`; `scattering_observable_ids` = `2` |
| `discretization-finite-volume-continuum` | `discretization_regime_ids` = `2`; `finite_volume_scaling_ids` = `2`; `continuum_extrapolation_ids` = `2` |
| `correlation-operator-bootstrap` | `correlation_function_ids` = `2`; `operator_insertion_ids` = `2`; `bootstrap_data_ids` = `2` |
| `phase-order-universality` | `phase_structure_ids` = `2`; `order_parameter_ids` = `2`; `universality_class_ids` = `2` |
| `hilbert-representation-spectrum` | `hilbert_space_ids` = `2`; `representation_map_ids` = `2`; `spectral_reconstruction_ids` = `2` |

### `R-OQ0057-AMPLITUDES-BOOTSTRAP`

- State: `S2`
- Ceiling: `S2`
- Earliest blocker: many-to-one inverse and public attribution

| Family | Route-field counts |
|---|---:|
| `route-state-core` | `promotion_gate_ids` = `3` |
| `public-record-custody` | `public_record_carrier_ids` = `3`; `acquisition_protocol_ids` = `2` |
| `defeat-rollback-severity` | `defeater_ids` = `4`; `rollback_rule_ids` = `4`; `severity_test_ids` = `1` |
| `evidence-credit` | `evidence_unit_ids` = `2`; `independence_assumption_ids` = `3`; `credit_allocation_ids` = `1` |
| `contrast-update-prior` | `contrast_class_ids` = `1`; `likelihood_update_ids` = `1`; `prior_sensitivity_ids` = `1` |
| `measurement-systematics-calibration` | `measurement_model_ids` = `2`; `systematic_uncertainty_ids` = `2`; `calibration_traceability_ids` = `2` |
| `validity-transport-extrapolation` | `validity_domain_ids` = `2`; `transportability_ids` = `2`; `extrapolation_fence_ids` = `2` |
| `causal-intervention-counterfactual` | `causal_mechanism_ids` = `2`; `intervention_protocol_ids` = `2`; `counterfactual_robustness_ids` = `2` |
| `selection-multiplicity-reporting` | `selection_function_ids` = `2`; `multiplicity_control_ids` = `2`; `reporting_bias_ids` = `2` |
| `capacity-complexity-generalization` | `model_capacity_ids` = `2`; `complexity_penalty_ids` = `2`; `generalization_validation_ids` = `2` |
| `semantic-ontology-language` | `semantic_term_ids` = `2`; `ontology_commitment_ids` = `2`; `claim_language_permission_ids` = `2` |
| `social-review-consensus` | `social_authority_ids` = `2`; `review_replication_ids` = `2`; `consensus_elicitation_ids` = `2` |
| `computational-numerical-software` | `computational_reproducibility_ids` = `2`; `numerical_stability_ids` = `2`; `software_supply_chain_ids` = `2` |
| `formal-proof-assumption-coverage` | `proof_obligation_ids` = `2`; `assumption_discharge_ids` = `2`; `formalization_coverage_ids` = `2` |
| `idealization-approximation-limit` | `idealization_ids` = `2`; `approximation_error_ids` = `2`; `limit_interchange_ids` = `2` |
| `boundary-initial-sector` | `boundary_condition_ids` = `2`; `initial_data_ids` = `2`; `sector_selection_ids` = `2` |
| `gauge-constraint-observable` | `gauge_symmetry_ids` = `2`; `constraint_closure_ids` = `2`; `observable_quotient_ids` = `2` |
| `regularization-renormalization-matching` | `regularization_scheme_ids` = `2`; `renormalization_flow_ids` = `2`; `matching_condition_ids` = `2` |
| `composition-interface-global` | `composition_law_ids` = `2`; `interface_compatibility_ids` = `2`; `global_consistency_ids` = `2` |
| `unitarity-causality-stability` | `unitarity_check_ids` = `2`; `causality_cone_ids` = `2`; `stability_positivity_ids` = `2` |
| `quantization-classical-semiclassical` | `quantization_map_ids` = `2`; `classical_limit_ids` = `2`; `semiclassical_correspondence_ids` = `2` |
| `information-entropy-no-go` | `information_flow_ids` = `2`; `entropy_accounting_ids` = `2`; `no_go_compliance_ids` = `2` |
| `symmetry-anomaly-conservation` | `symmetry_realization_ids` = `2`; `anomaly_matching_ids` = `2`; `conservation_law_ids` = `2` |
| `topology-dimension-signature` | `spacetime_topology_ids` = `2`; `dimension_realization_ids` = `2`; `signature_structure_ids` = `2` |
| `measure-ensemble-typicality` | `measure_definition_ids` = `2`; `ensemble_sampling_ids` = `2`; `typicality_weighting_ids` = `2` |
| `subsystem-algebra-edge-center` | `algebraic_locality_ids` = `2`; `subsystem_factorization_ids` = `2`; `edge_mode_center_ids` = `2` |
| `matter-spectrum-coupling-mass` | `particle_spectrum_ids` = `2`; `interaction_coupling_ids` = `2`; `mass_hierarchy_ids` = `2` |
| `cosmological-background-vacuum-history` | `cosmological_background_ids` = `2`; `vacuum_energy_ids` = `2`; `thermal_history_ids` = `2` |
| `black-hole-horizon-thermodynamics-evaporation` | `horizon_structure_ids` = `2`; `black_hole_thermodynamics_ids` = `2`; `evaporation_radiation_ids` = `2` |
| `singularity-censorship-hyperbolicity` | `curvature_regime_ids` = `2`; `singularity_resolution_ids` = `2`; `censorship_hyperbolicity_ids` = `2` |
| `stress-energy-backreaction-conditions` | `stress_energy_source_ids` = `2`; `backreaction_consistency_ids` = `2`; `energy_condition_ids` = `2` |
| `classical-gr-recovery` | `equivalence_principle_ids` = `2`; `weak_field_ppn_ids` = `2`; `gravitational_radiation_ids` = `2` |
| `state-preparation-detector-decoherence` | `state_preparation_ids` = `2`; `detector_response_ids` = `2`; `decoherence_pointer_ids` = `2` |
| `asymptotic-ir-scattering` | `asymptotic_state_ids` = `2`; `infrared_dressing_ids` = `2`; `scattering_observable_ids` = `2` |
| `discretization-finite-volume-continuum` | `discretization_regime_ids` = `2`; `finite_volume_scaling_ids` = `2`; `continuum_extrapolation_ids` = `2` |
| `correlation-operator-bootstrap` | `correlation_function_ids` = `2`; `operator_insertion_ids` = `2`; `bootstrap_data_ids` = `2` |
| `phase-order-universality` | `phase_structure_ids` = `2`; `order_parameter_ids` = `2`; `universality_class_ids` = `2` |
| `hilbert-representation-spectrum` | `hilbert_space_ids` = `2`; `representation_map_ids` = `2`; `spectral_reconstruction_ids` = `2` |

### `R-OQ0057-LAB-GIE-BMV`

- State: `S3`
- Ceiling: `S3`
- Earliest blocker: candidate target quotient and subsystem/public bridge assumptions

| Family | Route-field counts |
|---|---:|
| `route-state-core` | `promotion_gate_ids` = `2` |
| `public-record-custody` | `public_record_carrier_ids` = `2`; `acquisition_protocol_ids` = `1` |
| `defeat-rollback-severity` | `defeater_ids` = `5`; `rollback_rule_ids` = `5`; `severity_test_ids` = `1` |
| `evidence-credit` | `evidence_unit_ids` = `2`; `independence_assumption_ids` = `2`; `credit_allocation_ids` = `1` |
| `contrast-update-prior` | `contrast_class_ids` = `1`; `likelihood_update_ids` = `1`; `prior_sensitivity_ids` = `1` |
| `measurement-systematics-calibration` | `measurement_model_ids` = `2`; `systematic_uncertainty_ids` = `2`; `calibration_traceability_ids` = `2` |
| `validity-transport-extrapolation` | `validity_domain_ids` = `2`; `transportability_ids` = `2`; `extrapolation_fence_ids` = `2` |
| `causal-intervention-counterfactual` | `causal_mechanism_ids` = `2`; `intervention_protocol_ids` = `2`; `counterfactual_robustness_ids` = `2` |
| `selection-multiplicity-reporting` | `selection_function_ids` = `2`; `multiplicity_control_ids` = `2`; `reporting_bias_ids` = `2` |
| `capacity-complexity-generalization` | `model_capacity_ids` = `2`; `complexity_penalty_ids` = `2`; `generalization_validation_ids` = `2` |
| `semantic-ontology-language` | `semantic_term_ids` = `2`; `ontology_commitment_ids` = `2`; `claim_language_permission_ids` = `2` |
| `social-review-consensus` | `social_authority_ids` = `2`; `review_replication_ids` = `2`; `consensus_elicitation_ids` = `2` |
| `computational-numerical-software` | `computational_reproducibility_ids` = `2`; `numerical_stability_ids` = `2`; `software_supply_chain_ids` = `2` |
| `formal-proof-assumption-coverage` | `proof_obligation_ids` = `2`; `assumption_discharge_ids` = `2`; `formalization_coverage_ids` = `2` |
| `idealization-approximation-limit` | `idealization_ids` = `2`; `approximation_error_ids` = `2`; `limit_interchange_ids` = `2` |
| `boundary-initial-sector` | `boundary_condition_ids` = `2`; `initial_data_ids` = `2`; `sector_selection_ids` = `2` |
| `gauge-constraint-observable` | `gauge_symmetry_ids` = `2`; `constraint_closure_ids` = `2`; `observable_quotient_ids` = `2` |
| `regularization-renormalization-matching` | `regularization_scheme_ids` = `2`; `renormalization_flow_ids` = `2`; `matching_condition_ids` = `2` |
| `composition-interface-global` | `composition_law_ids` = `2`; `interface_compatibility_ids` = `2`; `global_consistency_ids` = `2` |
| `unitarity-causality-stability` | `unitarity_check_ids` = `2`; `causality_cone_ids` = `2`; `stability_positivity_ids` = `2` |
| `quantization-classical-semiclassical` | `quantization_map_ids` = `2`; `classical_limit_ids` = `2`; `semiclassical_correspondence_ids` = `2` |
| `information-entropy-no-go` | `information_flow_ids` = `2`; `entropy_accounting_ids` = `2`; `no_go_compliance_ids` = `2` |
| `symmetry-anomaly-conservation` | `symmetry_realization_ids` = `2`; `anomaly_matching_ids` = `2`; `conservation_law_ids` = `2` |
| `topology-dimension-signature` | `spacetime_topology_ids` = `2`; `dimension_realization_ids` = `2`; `signature_structure_ids` = `2` |
| `measure-ensemble-typicality` | `measure_definition_ids` = `2`; `ensemble_sampling_ids` = `2`; `typicality_weighting_ids` = `2` |
| `subsystem-algebra-edge-center` | `algebraic_locality_ids` = `2`; `subsystem_factorization_ids` = `2`; `edge_mode_center_ids` = `2` |
| `matter-spectrum-coupling-mass` | `particle_spectrum_ids` = `2`; `interaction_coupling_ids` = `2`; `mass_hierarchy_ids` = `2` |
| `cosmological-background-vacuum-history` | `cosmological_background_ids` = `2`; `vacuum_energy_ids` = `2`; `thermal_history_ids` = `2` |
| `black-hole-horizon-thermodynamics-evaporation` | `horizon_structure_ids` = `2`; `black_hole_thermodynamics_ids` = `2`; `evaporation_radiation_ids` = `2` |
| `singularity-censorship-hyperbolicity` | `curvature_regime_ids` = `2`; `singularity_resolution_ids` = `2`; `censorship_hyperbolicity_ids` = `2` |
| `stress-energy-backreaction-conditions` | `stress_energy_source_ids` = `2`; `backreaction_consistency_ids` = `2`; `energy_condition_ids` = `2` |
| `classical-gr-recovery` | `equivalence_principle_ids` = `2`; `weak_field_ppn_ids` = `2`; `gravitational_radiation_ids` = `2` |
| `state-preparation-detector-decoherence` | `state_preparation_ids` = `2`; `detector_response_ids` = `2`; `decoherence_pointer_ids` = `2` |
| `asymptotic-ir-scattering` | `asymptotic_state_ids` = `2`; `infrared_dressing_ids` = `2`; `scattering_observable_ids` = `2` |
| `discretization-finite-volume-continuum` | `discretization_regime_ids` = `2`; `finite_volume_scaling_ids` = `2`; `continuum_extrapolation_ids` = `2` |
| `correlation-operator-bootstrap` | `correlation_function_ids` = `2`; `operator_insertion_ids` = `2`; `bootstrap_data_ids` = `2` |
| `phase-order-universality` | `phase_structure_ids` = `2`; `order_parameter_ids` = `2`; `universality_class_ids` = `2` |
| `hilbert-representation-spectrum` | `hilbert_space_ids` = `2`; `representation_map_ids` = `2`; `spectral_reconstruction_ids` = `2` |

### `R-OQ0057-GW-STRONGFIELD-GR`

- State: `S2`
- Ceiling: `S2`
- Earliest blocker: many-to-one reduction to GR and non-quantum target

| Family | Route-field counts |
|---|---:|
| `route-state-core` | `promotion_gate_ids` = `3` |
| `public-record-custody` | `public_record_carrier_ids` = `2`; `acquisition_protocol_ids` = `1` |
| `defeat-rollback-severity` | `defeater_ids` = `3`; `rollback_rule_ids` = `3`; `severity_test_ids` = `2` |
| `evidence-credit` | `evidence_unit_ids` = `2`; `independence_assumption_ids` = `2`; `credit_allocation_ids` = `1` |
| `contrast-update-prior` | `contrast_class_ids` = `1`; `likelihood_update_ids` = `1`; `prior_sensitivity_ids` = `1` |
| `measurement-systematics-calibration` | `measurement_model_ids` = `2`; `systematic_uncertainty_ids` = `2`; `calibration_traceability_ids` = `2` |
| `validity-transport-extrapolation` | `validity_domain_ids` = `2`; `transportability_ids` = `2`; `extrapolation_fence_ids` = `2` |
| `causal-intervention-counterfactual` | `causal_mechanism_ids` = `2`; `intervention_protocol_ids` = `2`; `counterfactual_robustness_ids` = `2` |
| `selection-multiplicity-reporting` | `selection_function_ids` = `2`; `multiplicity_control_ids` = `2`; `reporting_bias_ids` = `2` |
| `capacity-complexity-generalization` | `model_capacity_ids` = `2`; `complexity_penalty_ids` = `2`; `generalization_validation_ids` = `2` |
| `semantic-ontology-language` | `semantic_term_ids` = `2`; `ontology_commitment_ids` = `2`; `claim_language_permission_ids` = `2` |
| `social-review-consensus` | `social_authority_ids` = `2`; `review_replication_ids` = `2`; `consensus_elicitation_ids` = `2` |
| `computational-numerical-software` | `computational_reproducibility_ids` = `2`; `numerical_stability_ids` = `2`; `software_supply_chain_ids` = `2` |
| `formal-proof-assumption-coverage` | `proof_obligation_ids` = `2`; `assumption_discharge_ids` = `2`; `formalization_coverage_ids` = `2` |
| `idealization-approximation-limit` | `idealization_ids` = `2`; `approximation_error_ids` = `2`; `limit_interchange_ids` = `2` |
| `boundary-initial-sector` | `boundary_condition_ids` = `2`; `initial_data_ids` = `2`; `sector_selection_ids` = `2` |
| `gauge-constraint-observable` | `gauge_symmetry_ids` = `2`; `constraint_closure_ids` = `2`; `observable_quotient_ids` = `2` |
| `regularization-renormalization-matching` | `regularization_scheme_ids` = `2`; `renormalization_flow_ids` = `2`; `matching_condition_ids` = `2` |
| `composition-interface-global` | `composition_law_ids` = `2`; `interface_compatibility_ids` = `2`; `global_consistency_ids` = `2` |
| `unitarity-causality-stability` | `unitarity_check_ids` = `2`; `causality_cone_ids` = `2`; `stability_positivity_ids` = `2` |
| `quantization-classical-semiclassical` | `quantization_map_ids` = `2`; `classical_limit_ids` = `2`; `semiclassical_correspondence_ids` = `2` |
| `information-entropy-no-go` | `information_flow_ids` = `2`; `entropy_accounting_ids` = `2`; `no_go_compliance_ids` = `2` |
| `symmetry-anomaly-conservation` | `symmetry_realization_ids` = `2`; `anomaly_matching_ids` = `2`; `conservation_law_ids` = `2` |
| `topology-dimension-signature` | `spacetime_topology_ids` = `2`; `dimension_realization_ids` = `2`; `signature_structure_ids` = `2` |
| `measure-ensemble-typicality` | `measure_definition_ids` = `2`; `ensemble_sampling_ids` = `2`; `typicality_weighting_ids` = `2` |
| `subsystem-algebra-edge-center` | `algebraic_locality_ids` = `2`; `subsystem_factorization_ids` = `2`; `edge_mode_center_ids` = `2` |
| `matter-spectrum-coupling-mass` | `particle_spectrum_ids` = `2`; `interaction_coupling_ids` = `2`; `mass_hierarchy_ids` = `2` |
| `cosmological-background-vacuum-history` | `cosmological_background_ids` = `2`; `vacuum_energy_ids` = `2`; `thermal_history_ids` = `2` |
| `black-hole-horizon-thermodynamics-evaporation` | `horizon_structure_ids` = `2`; `black_hole_thermodynamics_ids` = `2`; `evaporation_radiation_ids` = `2` |
| `singularity-censorship-hyperbolicity` | `curvature_regime_ids` = `2`; `singularity_resolution_ids` = `2`; `censorship_hyperbolicity_ids` = `2` |
| `stress-energy-backreaction-conditions` | `stress_energy_source_ids` = `2`; `backreaction_consistency_ids` = `2`; `energy_condition_ids` = `2` |
| `classical-gr-recovery` | `equivalence_principle_ids` = `2`; `weak_field_ppn_ids` = `2`; `gravitational_radiation_ids` = `2` |
| `state-preparation-detector-decoherence` | `state_preparation_ids` = `2`; `detector_response_ids` = `2`; `decoherence_pointer_ids` = `2` |
| `asymptotic-ir-scattering` | `asymptotic_state_ids` = `2`; `infrared_dressing_ids` = `2`; `scattering_observable_ids` = `2` |
| `discretization-finite-volume-continuum` | `discretization_regime_ids` = `2`; `finite_volume_scaling_ids` = `2`; `continuum_extrapolation_ids` = `2` |
| `correlation-operator-bootstrap` | `correlation_function_ids` = `2`; `operator_insertion_ids` = `2`; `bootstrap_data_ids` = `2` |
| `phase-order-universality` | `phase_structure_ids` = `2`; `order_parameter_ids` = `2`; `universality_class_ids` = `2` |
| `hilbert-representation-spectrum` | `hilbert_space_ids` = `2`; `representation_map_ids` = `2`; `spectral_reconstruction_ids` = `2` |

### `R-OQ0057-FRAME-QRF-RELATIONAL`

- State: `S2`
- Ceiling: `S2`
- Earliest blocker: public same-record equivalence and candidate-native witness substrate

| Family | Route-field counts |
|---|---:|
| `route-state-core` | `promotion_gate_ids` = `3` |
| `public-record-custody` | `public_record_carrier_ids` = `3`; `acquisition_protocol_ids` = `1` |
| `defeat-rollback-severity` | `defeater_ids` = `4`; `rollback_rule_ids` = `4`; `severity_test_ids` = `1` |
| `evidence-credit` | `evidence_unit_ids` = `2`; `independence_assumption_ids` = `3`; `credit_allocation_ids` = `1` |
| `contrast-update-prior` | `contrast_class_ids` = `1`; `likelihood_update_ids` = `1`; `prior_sensitivity_ids` = `1` |
| `measurement-systematics-calibration` | `measurement_model_ids` = `2`; `systematic_uncertainty_ids` = `2`; `calibration_traceability_ids` = `2` |
| `validity-transport-extrapolation` | `validity_domain_ids` = `2`; `transportability_ids` = `2`; `extrapolation_fence_ids` = `2` |
| `causal-intervention-counterfactual` | `causal_mechanism_ids` = `2`; `intervention_protocol_ids` = `2`; `counterfactual_robustness_ids` = `2` |
| `selection-multiplicity-reporting` | `selection_function_ids` = `2`; `multiplicity_control_ids` = `2`; `reporting_bias_ids` = `2` |
| `capacity-complexity-generalization` | `model_capacity_ids` = `2`; `complexity_penalty_ids` = `2`; `generalization_validation_ids` = `2` |
| `semantic-ontology-language` | `semantic_term_ids` = `2`; `ontology_commitment_ids` = `2`; `claim_language_permission_ids` = `2` |
| `social-review-consensus` | `social_authority_ids` = `2`; `review_replication_ids` = `2`; `consensus_elicitation_ids` = `2` |
| `computational-numerical-software` | `computational_reproducibility_ids` = `2`; `numerical_stability_ids` = `2`; `software_supply_chain_ids` = `2` |
| `formal-proof-assumption-coverage` | `proof_obligation_ids` = `2`; `assumption_discharge_ids` = `2`; `formalization_coverage_ids` = `2` |
| `idealization-approximation-limit` | `idealization_ids` = `2`; `approximation_error_ids` = `2`; `limit_interchange_ids` = `2` |
| `boundary-initial-sector` | `boundary_condition_ids` = `2`; `initial_data_ids` = `2`; `sector_selection_ids` = `2` |
| `gauge-constraint-observable` | `gauge_symmetry_ids` = `2`; `constraint_closure_ids` = `2`; `observable_quotient_ids` = `2` |
| `regularization-renormalization-matching` | `regularization_scheme_ids` = `2`; `renormalization_flow_ids` = `2`; `matching_condition_ids` = `2` |
| `composition-interface-global` | `composition_law_ids` = `2`; `interface_compatibility_ids` = `2`; `global_consistency_ids` = `2` |
| `unitarity-causality-stability` | `unitarity_check_ids` = `2`; `causality_cone_ids` = `2`; `stability_positivity_ids` = `2` |
| `quantization-classical-semiclassical` | `quantization_map_ids` = `2`; `classical_limit_ids` = `2`; `semiclassical_correspondence_ids` = `2` |
| `information-entropy-no-go` | `information_flow_ids` = `2`; `entropy_accounting_ids` = `2`; `no_go_compliance_ids` = `2` |
| `symmetry-anomaly-conservation` | `symmetry_realization_ids` = `2`; `anomaly_matching_ids` = `2`; `conservation_law_ids` = `2` |
| `topology-dimension-signature` | `spacetime_topology_ids` = `2`; `dimension_realization_ids` = `2`; `signature_structure_ids` = `2` |
| `measure-ensemble-typicality` | `measure_definition_ids` = `2`; `ensemble_sampling_ids` = `2`; `typicality_weighting_ids` = `2` |
| `subsystem-algebra-edge-center` | `algebraic_locality_ids` = `2`; `subsystem_factorization_ids` = `2`; `edge_mode_center_ids` = `2` |
| `matter-spectrum-coupling-mass` | `particle_spectrum_ids` = `2`; `interaction_coupling_ids` = `2`; `mass_hierarchy_ids` = `2` |
| `cosmological-background-vacuum-history` | `cosmological_background_ids` = `2`; `vacuum_energy_ids` = `2`; `thermal_history_ids` = `2` |
| `black-hole-horizon-thermodynamics-evaporation` | `horizon_structure_ids` = `2`; `black_hole_thermodynamics_ids` = `2`; `evaporation_radiation_ids` = `2` |
| `singularity-censorship-hyperbolicity` | `curvature_regime_ids` = `2`; `singularity_resolution_ids` = `2`; `censorship_hyperbolicity_ids` = `2` |
| `stress-energy-backreaction-conditions` | `stress_energy_source_ids` = `2`; `backreaction_consistency_ids` = `2`; `energy_condition_ids` = `2` |
| `classical-gr-recovery` | `equivalence_principle_ids` = `2`; `weak_field_ppn_ids` = `2`; `gravitational_radiation_ids` = `2` |
| `state-preparation-detector-decoherence` | `state_preparation_ids` = `2`; `detector_response_ids` = `2`; `decoherence_pointer_ids` = `2` |
| `asymptotic-ir-scattering` | `asymptotic_state_ids` = `2`; `infrared_dressing_ids` = `2`; `scattering_observable_ids` = `2` |
| `discretization-finite-volume-continuum` | `discretization_regime_ids` = `2`; `finite_volume_scaling_ids` = `2`; `continuum_extrapolation_ids` = `2` |
| `correlation-operator-bootstrap` | `correlation_function_ids` = `2`; `operator_insertion_ids` = `2`; `bootstrap_data_ids` = `2` |
| `phase-order-universality` | `phase_structure_ids` = `2`; `order_parameter_ids` = `2`; `universality_class_ids` = `2` |
| `hilbert-representation-spectrum` | `hilbert_space_ids` = `2`; `representation_map_ids` = `2`; `spectral_reconstruction_ids` = `2` |

### `R-OQ0057-LAB-GRAVITON-COUNTING`

- State: `S2`
- Ceiling: `S3`
- Earliest blocker: candidate target quotient and source/detector attribution

| Family | Route-field counts |
|---|---:|
| `route-state-core` | `promotion_gate_ids` = `3` |
| `public-record-custody` | `public_record_carrier_ids` = `3`; `acquisition_protocol_ids` = `1` |
| `defeat-rollback-severity` | `defeater_ids` = `6`; `rollback_rule_ids` = `6`; `severity_test_ids` = `2` |
| `evidence-credit` | `evidence_unit_ids` = `2`; `independence_assumption_ids` = `3`; `credit_allocation_ids` = `1` |
| `contrast-update-prior` | `contrast_class_ids` = `2`; `likelihood_update_ids` = `1`; `prior_sensitivity_ids` = `2` |
| `measurement-systematics-calibration` | `measurement_model_ids` = `2`; `systematic_uncertainty_ids` = `2`; `calibration_traceability_ids` = `2` |
| `validity-transport-extrapolation` | `validity_domain_ids` = `2`; `transportability_ids` = `2`; `extrapolation_fence_ids` = `2` |
| `causal-intervention-counterfactual` | `causal_mechanism_ids` = `2`; `intervention_protocol_ids` = `2`; `counterfactual_robustness_ids` = `2` |
| `selection-multiplicity-reporting` | `selection_function_ids` = `2`; `multiplicity_control_ids` = `2`; `reporting_bias_ids` = `2` |
| `capacity-complexity-generalization` | `model_capacity_ids` = `2`; `complexity_penalty_ids` = `2`; `generalization_validation_ids` = `2` |
| `semantic-ontology-language` | `semantic_term_ids` = `2`; `ontology_commitment_ids` = `2`; `claim_language_permission_ids` = `2` |
| `social-review-consensus` | `social_authority_ids` = `2`; `review_replication_ids` = `2`; `consensus_elicitation_ids` = `2` |
| `computational-numerical-software` | `computational_reproducibility_ids` = `2`; `numerical_stability_ids` = `2`; `software_supply_chain_ids` = `2` |
| `formal-proof-assumption-coverage` | `proof_obligation_ids` = `2`; `assumption_discharge_ids` = `2`; `formalization_coverage_ids` = `2` |
| `idealization-approximation-limit` | `idealization_ids` = `2`; `approximation_error_ids` = `2`; `limit_interchange_ids` = `2` |
| `boundary-initial-sector` | `boundary_condition_ids` = `2`; `initial_data_ids` = `2`; `sector_selection_ids` = `2` |
| `gauge-constraint-observable` | `gauge_symmetry_ids` = `2`; `constraint_closure_ids` = `2`; `observable_quotient_ids` = `2` |
| `regularization-renormalization-matching` | `regularization_scheme_ids` = `2`; `renormalization_flow_ids` = `2`; `matching_condition_ids` = `2` |
| `composition-interface-global` | `composition_law_ids` = `2`; `interface_compatibility_ids` = `2`; `global_consistency_ids` = `2` |
| `unitarity-causality-stability` | `unitarity_check_ids` = `2`; `causality_cone_ids` = `2`; `stability_positivity_ids` = `2` |
| `quantization-classical-semiclassical` | `quantization_map_ids` = `2`; `classical_limit_ids` = `2`; `semiclassical_correspondence_ids` = `2` |
| `information-entropy-no-go` | `information_flow_ids` = `2`; `entropy_accounting_ids` = `2`; `no_go_compliance_ids` = `2` |
| `symmetry-anomaly-conservation` | `symmetry_realization_ids` = `2`; `anomaly_matching_ids` = `2`; `conservation_law_ids` = `2` |
| `topology-dimension-signature` | `spacetime_topology_ids` = `2`; `dimension_realization_ids` = `2`; `signature_structure_ids` = `2` |
| `measure-ensemble-typicality` | `measure_definition_ids` = `2`; `ensemble_sampling_ids` = `2`; `typicality_weighting_ids` = `2` |
| `subsystem-algebra-edge-center` | `algebraic_locality_ids` = `2`; `subsystem_factorization_ids` = `2`; `edge_mode_center_ids` = `2` |
| `matter-spectrum-coupling-mass` | `particle_spectrum_ids` = `2`; `interaction_coupling_ids` = `2`; `mass_hierarchy_ids` = `2` |
| `cosmological-background-vacuum-history` | `cosmological_background_ids` = `2`; `vacuum_energy_ids` = `2`; `thermal_history_ids` = `2` |
| `black-hole-horizon-thermodynamics-evaporation` | `horizon_structure_ids` = `2`; `black_hole_thermodynamics_ids` = `2`; `evaporation_radiation_ids` = `2` |
| `singularity-censorship-hyperbolicity` | `curvature_regime_ids` = `2`; `singularity_resolution_ids` = `2`; `censorship_hyperbolicity_ids` = `2` |
| `stress-energy-backreaction-conditions` | `stress_energy_source_ids` = `2`; `backreaction_consistency_ids` = `2`; `energy_condition_ids` = `2` |
| `classical-gr-recovery` | `equivalence_principle_ids` = `2`; `weak_field_ppn_ids` = `2`; `gravitational_radiation_ids` = `2` |
| `state-preparation-detector-decoherence` | `state_preparation_ids` = `2`; `detector_response_ids` = `2`; `decoherence_pointer_ids` = `2` |
| `asymptotic-ir-scattering` | `asymptotic_state_ids` = `2`; `infrared_dressing_ids` = `2`; `scattering_observable_ids` = `2` |
| `discretization-finite-volume-continuum` | `discretization_regime_ids` = `2`; `finite_volume_scaling_ids` = `2`; `continuum_extrapolation_ids` = `2` |
| `correlation-operator-bootstrap` | `correlation_function_ids` = `2`; `operator_insertion_ids` = `2`; `bootstrap_data_ids` = `2` |
| `phase-order-universality` | `phase_structure_ids` = `2`; `order_parameter_ids` = `2`; `universality_class_ids` = `2` |
| `hilbert-representation-spectrum` | `hilbert_space_ids` = `2`; `representation_map_ids` = `2`; `spectral_reconstruction_ids` = `2` |

### `R-OQ0057-COSMO-DARK-ENERGY-BAO`

- State: `S2`
- Ceiling: `S2`
- Earliest blocker: many-to-one cosmological inverse and parameterization/systematics dependence

| Family | Route-field counts |
|---|---:|
| `route-state-core` | `promotion_gate_ids` = `3` |
| `public-record-custody` | `public_record_carrier_ids` = `2`; `acquisition_protocol_ids` = `1` |
| `defeat-rollback-severity` | `defeater_ids` = `5`; `rollback_rule_ids` = `5`; `severity_test_ids` = `2` |
| `evidence-credit` | `evidence_unit_ids` = `2`; `independence_assumption_ids` = `2`; `credit_allocation_ids` = `1` |
| `contrast-update-prior` | `contrast_class_ids` = `1`; `likelihood_update_ids` = `1`; `prior_sensitivity_ids` = `1` |
| `measurement-systematics-calibration` | `measurement_model_ids` = `2`; `systematic_uncertainty_ids` = `2`; `calibration_traceability_ids` = `2` |
| `validity-transport-extrapolation` | `validity_domain_ids` = `2`; `transportability_ids` = `2`; `extrapolation_fence_ids` = `2` |
| `causal-intervention-counterfactual` | `causal_mechanism_ids` = `2`; `intervention_protocol_ids` = `2`; `counterfactual_robustness_ids` = `2` |
| `selection-multiplicity-reporting` | `selection_function_ids` = `2`; `multiplicity_control_ids` = `2`; `reporting_bias_ids` = `2` |
| `capacity-complexity-generalization` | `model_capacity_ids` = `2`; `complexity_penalty_ids` = `2`; `generalization_validation_ids` = `2` |
| `semantic-ontology-language` | `semantic_term_ids` = `2`; `ontology_commitment_ids` = `2`; `claim_language_permission_ids` = `2` |
| `social-review-consensus` | `social_authority_ids` = `2`; `review_replication_ids` = `2`; `consensus_elicitation_ids` = `2` |
| `computational-numerical-software` | `computational_reproducibility_ids` = `2`; `numerical_stability_ids` = `2`; `software_supply_chain_ids` = `2` |
| `formal-proof-assumption-coverage` | `proof_obligation_ids` = `2`; `assumption_discharge_ids` = `2`; `formalization_coverage_ids` = `2` |
| `idealization-approximation-limit` | `idealization_ids` = `2`; `approximation_error_ids` = `2`; `limit_interchange_ids` = `2` |
| `boundary-initial-sector` | `boundary_condition_ids` = `2`; `initial_data_ids` = `2`; `sector_selection_ids` = `2` |
| `gauge-constraint-observable` | `gauge_symmetry_ids` = `2`; `constraint_closure_ids` = `2`; `observable_quotient_ids` = `2` |
| `regularization-renormalization-matching` | `regularization_scheme_ids` = `2`; `renormalization_flow_ids` = `2`; `matching_condition_ids` = `2` |
| `composition-interface-global` | `composition_law_ids` = `2`; `interface_compatibility_ids` = `2`; `global_consistency_ids` = `2` |
| `unitarity-causality-stability` | `unitarity_check_ids` = `2`; `causality_cone_ids` = `2`; `stability_positivity_ids` = `2` |
| `quantization-classical-semiclassical` | `quantization_map_ids` = `2`; `classical_limit_ids` = `2`; `semiclassical_correspondence_ids` = `2` |
| `information-entropy-no-go` | `information_flow_ids` = `2`; `entropy_accounting_ids` = `2`; `no_go_compliance_ids` = `2` |
| `symmetry-anomaly-conservation` | `symmetry_realization_ids` = `2`; `anomaly_matching_ids` = `2`; `conservation_law_ids` = `2` |
| `topology-dimension-signature` | `spacetime_topology_ids` = `2`; `dimension_realization_ids` = `2`; `signature_structure_ids` = `2` |
| `measure-ensemble-typicality` | `measure_definition_ids` = `2`; `ensemble_sampling_ids` = `2`; `typicality_weighting_ids` = `2` |
| `subsystem-algebra-edge-center` | `algebraic_locality_ids` = `2`; `subsystem_factorization_ids` = `2`; `edge_mode_center_ids` = `2` |
| `matter-spectrum-coupling-mass` | `particle_spectrum_ids` = `2`; `interaction_coupling_ids` = `2`; `mass_hierarchy_ids` = `2` |
| `cosmological-background-vacuum-history` | `cosmological_background_ids` = `2`; `vacuum_energy_ids` = `2`; `thermal_history_ids` = `2` |
| `black-hole-horizon-thermodynamics-evaporation` | `horizon_structure_ids` = `2`; `black_hole_thermodynamics_ids` = `2`; `evaporation_radiation_ids` = `2` |
| `singularity-censorship-hyperbolicity` | `curvature_regime_ids` = `2`; `singularity_resolution_ids` = `2`; `censorship_hyperbolicity_ids` = `2` |
| `stress-energy-backreaction-conditions` | `stress_energy_source_ids` = `2`; `backreaction_consistency_ids` = `2`; `energy_condition_ids` = `2` |
| `classical-gr-recovery` | `equivalence_principle_ids` = `2`; `weak_field_ppn_ids` = `2`; `gravitational_radiation_ids` = `2` |
| `state-preparation-detector-decoherence` | `state_preparation_ids` = `2`; `detector_response_ids` = `2`; `decoherence_pointer_ids` = `2` |
| `asymptotic-ir-scattering` | `asymptotic_state_ids` = `2`; `infrared_dressing_ids` = `2`; `scattering_observable_ids` = `2` |
| `discretization-finite-volume-continuum` | `discretization_regime_ids` = `2`; `finite_volume_scaling_ids` = `2`; `continuum_extrapolation_ids` = `2` |
| `correlation-operator-bootstrap` | `correlation_function_ids` = `2`; `operator_insertion_ids` = `2`; `bootstrap_data_ids` = `2` |
| `phase-order-universality` | `phase_structure_ids` = `2`; `order_parameter_ids` = `2`; `universality_class_ids` = `2` |
| `hilbert-representation-spectrum` | `hilbert_space_ids` = `2`; `representation_map_ids` = `2`; `spectral_reconstruction_ids` = `2` |

### `R-OQ0057-PRIMORDIAL-TENSOR-BMODES`

- State: `S2`
- Ceiling: `S2`
- Earliest blocker: foreground/lensing publicness and many-to-one early-universe inverse

| Family | Route-field counts |
|---|---:|
| `route-state-core` | `promotion_gate_ids` = `3` |
| `public-record-custody` | `public_record_carrier_ids` = `2`; `acquisition_protocol_ids` = `1` |
| `defeat-rollback-severity` | `defeater_ids` = `6`; `rollback_rule_ids` = `6`; `severity_test_ids` = `2` |
| `evidence-credit` | `evidence_unit_ids` = `2`; `independence_assumption_ids` = `3`; `credit_allocation_ids` = `1` |
| `contrast-update-prior` | `contrast_class_ids` = `1`; `likelihood_update_ids` = `1`; `prior_sensitivity_ids` = `1` |
| `measurement-systematics-calibration` | `measurement_model_ids` = `2`; `systematic_uncertainty_ids` = `2`; `calibration_traceability_ids` = `2` |
| `validity-transport-extrapolation` | `validity_domain_ids` = `2`; `transportability_ids` = `2`; `extrapolation_fence_ids` = `2` |
| `causal-intervention-counterfactual` | `causal_mechanism_ids` = `2`; `intervention_protocol_ids` = `2`; `counterfactual_robustness_ids` = `2` |
| `selection-multiplicity-reporting` | `selection_function_ids` = `2`; `multiplicity_control_ids` = `2`; `reporting_bias_ids` = `2` |
| `capacity-complexity-generalization` | `model_capacity_ids` = `2`; `complexity_penalty_ids` = `2`; `generalization_validation_ids` = `2` |
| `semantic-ontology-language` | `semantic_term_ids` = `2`; `ontology_commitment_ids` = `2`; `claim_language_permission_ids` = `2` |
| `social-review-consensus` | `social_authority_ids` = `2`; `review_replication_ids` = `2`; `consensus_elicitation_ids` = `2` |
| `computational-numerical-software` | `computational_reproducibility_ids` = `2`; `numerical_stability_ids` = `2`; `software_supply_chain_ids` = `2` |
| `formal-proof-assumption-coverage` | `proof_obligation_ids` = `2`; `assumption_discharge_ids` = `2`; `formalization_coverage_ids` = `2` |
| `idealization-approximation-limit` | `idealization_ids` = `2`; `approximation_error_ids` = `2`; `limit_interchange_ids` = `2` |
| `boundary-initial-sector` | `boundary_condition_ids` = `2`; `initial_data_ids` = `2`; `sector_selection_ids` = `2` |
| `gauge-constraint-observable` | `gauge_symmetry_ids` = `2`; `constraint_closure_ids` = `2`; `observable_quotient_ids` = `2` |
| `regularization-renormalization-matching` | `regularization_scheme_ids` = `2`; `renormalization_flow_ids` = `2`; `matching_condition_ids` = `2` |
| `composition-interface-global` | `composition_law_ids` = `2`; `interface_compatibility_ids` = `2`; `global_consistency_ids` = `2` |
| `unitarity-causality-stability` | `unitarity_check_ids` = `2`; `causality_cone_ids` = `2`; `stability_positivity_ids` = `2` |
| `quantization-classical-semiclassical` | `quantization_map_ids` = `2`; `classical_limit_ids` = `2`; `semiclassical_correspondence_ids` = `2` |
| `information-entropy-no-go` | `information_flow_ids` = `2`; `entropy_accounting_ids` = `2`; `no_go_compliance_ids` = `2` |
| `symmetry-anomaly-conservation` | `symmetry_realization_ids` = `2`; `anomaly_matching_ids` = `2`; `conservation_law_ids` = `2` |
| `topology-dimension-signature` | `spacetime_topology_ids` = `2`; `dimension_realization_ids` = `2`; `signature_structure_ids` = `2` |
| `measure-ensemble-typicality` | `measure_definition_ids` = `2`; `ensemble_sampling_ids` = `2`; `typicality_weighting_ids` = `2` |
| `subsystem-algebra-edge-center` | `algebraic_locality_ids` = `2`; `subsystem_factorization_ids` = `2`; `edge_mode_center_ids` = `2` |
| `matter-spectrum-coupling-mass` | `particle_spectrum_ids` = `2`; `interaction_coupling_ids` = `2`; `mass_hierarchy_ids` = `2` |
| `cosmological-background-vacuum-history` | `cosmological_background_ids` = `2`; `vacuum_energy_ids` = `2`; `thermal_history_ids` = `2` |
| `black-hole-horizon-thermodynamics-evaporation` | `horizon_structure_ids` = `2`; `black_hole_thermodynamics_ids` = `2`; `evaporation_radiation_ids` = `2` |
| `singularity-censorship-hyperbolicity` | `curvature_regime_ids` = `2`; `singularity_resolution_ids` = `2`; `censorship_hyperbolicity_ids` = `2` |
| `stress-energy-backreaction-conditions` | `stress_energy_source_ids` = `2`; `backreaction_consistency_ids` = `2`; `energy_condition_ids` = `2` |
| `classical-gr-recovery` | `equivalence_principle_ids` = `2`; `weak_field_ppn_ids` = `2`; `gravitational_radiation_ids` = `2` |
| `state-preparation-detector-decoherence` | `state_preparation_ids` = `2`; `detector_response_ids` = `2`; `decoherence_pointer_ids` = `2` |
| `asymptotic-ir-scattering` | `asymptotic_state_ids` = `2`; `infrared_dressing_ids` = `2`; `scattering_observable_ids` = `2` |
| `discretization-finite-volume-continuum` | `discretization_regime_ids` = `2`; `finite_volume_scaling_ids` = `2`; `continuum_extrapolation_ids` = `2` |
| `correlation-operator-bootstrap` | `correlation_function_ids` = `2`; `operator_insertion_ids` = `2`; `bootstrap_data_ids` = `2` |
| `phase-order-universality` | `phase_structure_ids` = `2`; `order_parameter_ids` = `2`; `universality_class_ids` = `2` |
| `hilbert-representation-spectrum` | `hilbert_space_ids` = `2`; `representation_map_ids` = `2`; `spectral_reconstruction_ids` = `2` |


## Non-promotion rule

This generated surface is descriptive only. A route row may not spend higher authority because it appears in this table. Promotion still requires the state-machine entry conditions, public-record custody, observed-sector obligations, negative controls, empirical deltas, residual caps, and every route-support family declared in `LEDGER-FAMILY-REGISTRY.json`.
