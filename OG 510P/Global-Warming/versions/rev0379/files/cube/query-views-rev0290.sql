-- Query views for rev0290: nuclear-positive deployment sequencing and propagation audit

CREATE VIEW IF NOT EXISTS v_nuclear_portfolio_sequence AS
SELECT archetype_id, technology_path, default_sequence_rank, preferred_when, required_evidence, default_cap_if_missing
FROM nuclear_project_archetype
ORDER BY CAST(default_sequence_rank AS INTEGER);

CREATE VIEW IF NOT EXISTS v_nuclear_service_floor_gate_status AS
SELECT m.service_floor_id, m.nuclear_policy_status, m.preferred_nuclear_path,
       m.binding_gate_ids, COUNT(g.nuclear_gap_id) AS open_template_gap_count
FROM nuclear_service_floor_map m
LEFT JOIN nuclear_assurance_gap_backlog g ON m.service_floor_id = g.service_floor_id
GROUP BY m.service_floor_id, m.nuclear_policy_status, m.preferred_nuclear_path, m.binding_gate_ids;

CREATE VIEW IF NOT EXISTS v_nuclear_propagation_backlog AS
SELECT service_floor_id, primary_domain, nuclear_relevance_class, should_route_to_nuclear_assessment,
       route_present_in_source_files, exception_required, preferred_action, source_file_ids
FROM nuclear_preference_propagation_audit
WHERE exception_required = 'true' OR route_present_in_source_files = 'false';

CREATE VIEW IF NOT EXISTS v_nuclear_exception_ledger_open AS
SELECT exception_id, service_floor_id, exception_type, exception_statement, burden_of_proof_owner, review_trigger, status
FROM nuclear_exception_ledger
WHERE status <> 'recorded';

CREATE VIEW IF NOT EXISTS v_nuclear_fuel_cycle_caps AS
SELECT fuel_cycle_id, fuel_stage, applies_to, assurance_question, minimum_evidence, maturity_cap_if_missing
FROM nuclear_fuel_cycle_assurance;

CREATE VIEW IF NOT EXISTS v_nuclear_water_site_screen AS
SELECT screen_id, screen_family, hazards_or_constraints, minimum_condition, maturity_cap_if_missing
FROM nuclear_water_siting_screen;

CREATE VIEW IF NOT EXISTS v_nuclear_grid_load_match AS
SELECT load_match_id, load_family, candidate_loads, nuclear_relevance_rule, minimum_evidence
FROM nuclear_grid_load_match;
