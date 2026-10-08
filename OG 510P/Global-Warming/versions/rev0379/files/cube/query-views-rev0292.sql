-- Query views for rev0292: nuclear bankability/buildability and market-design audit

DROP VIEW IF EXISTS v_nuclear_finance_buildability_gaps;
CREATE VIEW v_nuclear_finance_buildability_gaps AS
SELECT service_floor_id, nuclear_gate_id, gap_type, priority, required_action, required_table, maturity_cap_if_unclosed
FROM nuclear_assurance_gap_backlog
WHERE nuclear_gate_id IN ('NG_29','NG_30','NG_31','NG_32','NG_33','NG_34','NG_35','NG_36','NG_37','NG_38','NG_39','NG_40');

DROP VIEW IF EXISTS v_nuclear_service_floor_bankability;
CREATE VIEW v_nuclear_service_floor_bankability AS
SELECT m.service_floor_id, m.nuclear_policy_status, a.bankability_gate_present, a.offtake_gate_present, a.construction_gate_present, a.public_value_gate_present, s.maturity_ceiling, s.gap_flags
FROM nuclear_service_floor_map m
LEFT JOIN nuclear_finance_buildability_propagation_audit a USING(service_floor_id)
LEFT JOIN service_floor_assurance_scorecard s USING(service_floor_id);

DROP VIEW IF EXISTS v_nuclear_large_load_match;
CREATE VIEW v_nuclear_large_load_match AS
SELECT match_id, service_floor_id, load_type, nuclear_fit, required_grid_study, required_flexibility, cost_allocation_test, public_benefit_test, status
FROM nuclear_large_load_nuclear_match;

DROP VIEW IF EXISTS v_nuclear_project_controls;
CREATE VIEW v_nuclear_project_controls AS
SELECT scorecard_id, service_floor_id, cost_baseline_status, schedule_baseline_status, contingency_status, earned_value_status, change_order_status, independent_estimate_status, maturity_cap_if_missing
FROM nuclear_project_controls_scorecard;

DROP VIEW IF EXISTS v_nuclear_public_value_safeguards;
CREATE VIEW v_nuclear_public_value_safeguards AS
SELECT safeguard_id, service_floor_id, rate_impact_test, taxpayer_exposure_test, host_community_benefit, workforce_benefit, public_value_condition, audit_or_redress_path
FROM nuclear_ratepayer_public_value_safeguard;
