-- Rev0294 nuclear integrated-energy query views
CREATE VIEW IF NOT EXISTS v_rev0294_nuclear_integrated_energy_service_floors AS
SELECT service_floor_id, label, primary_domain, source_file_ids
FROM service_floor
WHERE source_file_ids IN ('454','455','456','457','458')
   OR primary_domain LIKE 'nuclear_%';

CREATE VIEW IF NOT EXISTS v_rev0294_nuclear_integrated_energy_gate_backlog AS
SELECT service_floor_id, nuclear_gate_id, gap_type, priority, required_table, required_action, maturity_cap_if_unclosed
FROM nuclear_integrated_energy_gap_backlog;

CREATE VIEW IF NOT EXISTS v_rev0294_nuclear_coproduct_dispatch AS
SELECT service_floor_id, coproducts, normal_priority_rule, stress_priority_rule, curtailment_rule, status
FROM nuclear_coproduct_dispatch_protocol;

CREATE VIEW IF NOT EXISTS v_rev0294_nuclear_data_center_public_value AS
SELECT d.service_floor_id, d.load_type, d.interconnection_study_required, d.curtailment_protocol_required, d.ratepayer_cost_shift_test_required, p.risk_of_private_capture
FROM nuclear_data_center_critical_load_interface d
LEFT JOIN nuclear_co_benefit_public_value_ledger p USING(service_floor_id);

CREATE VIEW IF NOT EXISTS v_rev0294_nuclear_water_hydrogen_heat_paths AS
SELECT service_floor_id, 'heat' AS path_type, status FROM nuclear_cogeneration_heat_market
UNION ALL
SELECT service_floor_id, 'water' AS path_type, status FROM nuclear_desalination_water_security
UNION ALL
SELECT service_floor_id, 'hydrogen_clean_molecules' AS path_type, status FROM nuclear_hydrogen_synthetic_fuels;

CREATE VIEW IF NOT EXISTS v_rev0294_nuclear_sector_coupling_exceptions AS
SELECT service_floor_id, exception_question, negative_evidence_required, owner_role, maturity_effect, status
FROM nuclear_sector_coupling_exception_ledger;
