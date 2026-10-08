
-- rev0298 query views: nuclear human-capital and institutional-capacity refactor
DROP VIEW IF EXISTS v_rev0298_nuclear_human_capital_floors;
CREATE VIEW v_rev0298_nuclear_human_capital_floors AS
SELECT service_floor_id, human_capital_relevance, current_ceiling, next_action
FROM nuclear_human_capital_scorecard
WHERE human_capital_relevance IN ('primary','binding_cross_cutting_gate');

DROP VIEW IF EXISTS v_rev0298_operator_licensing_pipeline;
CREATE VIEW v_rev0298_operator_licensing_pipeline AS
SELECT role_family, candidate_pipeline_required, facility_training_required, requalification_required, maturity_cap_if_missing
FROM nuclear_operator_licensing_pipeline;

DROP VIEW IF EXISTS v_rev0298_regulator_capacity_risk;
CREATE VIEW v_rev0298_regulator_capacity_risk AS
SELECT regulator_capacity_domain, risk_if_missing, required_evidence, status
FROM nuclear_regulator_workforce_capacity;

DROP VIEW IF EXISTS v_rev0298_quality_culture_controls;
CREATE VIEW v_rev0298_quality_culture_controls AS
SELECT assessment_area, minimum_condition, evidence_required, claim_effect
FROM nuclear_quality_culture_assessment;

DROP VIEW IF EXISTS v_rev0298_workforce_gap_backlog;
CREATE VIEW v_rev0298_workforce_gap_backlog AS
SELECT service_floor_id, nuclear_gate_id, priority, required_action, maturity_cap_if_unclosed
FROM nuclear_workforce_gap_backlog;

DROP VIEW IF EXISTS v_rev0298_human_capital_maturity_caps;
CREATE VIEW v_rev0298_human_capital_maturity_caps AS
SELECT service_floor_id, current_ceiling, binding_reason, next_action
FROM nuclear_human_capital_maturity_cap_execution;
