-- Rev0295 nuclear fuel-cycle/backend query views
CREATE VIEW IF NOT EXISTS v_rev0295_nuclear_fuel_cycle_service_floors AS
SELECT service_floor_id, nuclear_relevance, preferred_nuclear_path, nuclear_policy_status, source_file_ids
FROM nuclear_service_floor_map
WHERE preferred_nuclear_path LIKE '%fuel%' OR preferred_nuclear_path LIKE '%backend%' OR source_file_ids LIKE '%459%' OR source_file_ids LIKE '%460%' OR source_file_ids LIKE '%461%' OR source_file_ids LIKE '%462%' OR source_file_ids LIKE '%463%';

CREATE VIEW IF NOT EXISTS v_rev0295_fuel_backend_gate_backlog AS
SELECT service_floor_id, nuclear_gate_id, required_table, required_action, maturity_cap_if_unclosed
FROM nuclear_fuel_cycle_gap_backlog;

CREATE VIEW IF NOT EXISTS v_rev0295_haleu_and_enrichment_risks AS
SELECT service_floor_id, assay_dependency, allocation_or_contract_required, domestic_supply_capacity_evidence_required, alternative_fuel_strategy_required, schedule_cap_if_missing
FROM nuclear_haleu_allocation_ledger;

CREATE VIEW IF NOT EXISTS v_rev0295_spent_fuel_backend_paths AS
SELECT service_floor_id, backend_segment, inventory_record_required, aging_management_required, transport_or_storage_package_required, consent_or_public_docket_required, funding_alignment_required
FROM nuclear_spent_fuel_backend_pathway;

CREATE VIEW IF NOT EXISTS v_rev0295_transport_safeguards_publication_controls AS
SELECT service_floor_id, control_domain, package_or_material_accountancy_required, security_plan_required, emergency_interface_required, public_redaction_rule_required
FROM nuclear_fuel_transport_security_safeguards;

CREATE VIEW IF NOT EXISTS v_rev0295_fuel_cycle_exceptions AS
SELECT service_floor_id, exception_question, negative_evidence_required, owner_role, maturity_effect, status
FROM nuclear_fuel_cycle_backend_exception_ledger;

CREATE VIEW IF NOT EXISTS v_rev0295_fuel_cycle_maturity_caps AS
SELECT service_floor_id, fuel_backend_gate_count, maturity_ceiling, cap_reason, next_required_action
FROM nuclear_fuel_cycle_maturity_cap_execution;
