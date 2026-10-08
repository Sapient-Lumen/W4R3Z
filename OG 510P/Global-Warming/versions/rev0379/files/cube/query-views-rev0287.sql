
-- Rev0287 query views. CSV table names are converted to snake_case.
CREATE VIEW v_service_floor_gate_failures AS
SELECT service_floor_id, gate_id, status, cap_if_failed, blocking_for, observed_value, threshold, explanation
FROM service_floor_gate_evaluation
WHERE applies = 'true' AND status IN ('fail','template_only')
ORDER BY service_floor_id, gate_id;

CREATE VIEW v_binding_maturity_caps AS
SELECT service_floor_id, high_stakes_flag, current_maturity_ceiling, binding_gate_count,
       template_only_gate_count, failed_gate_count, binding_gate_ids, next_required_action, false_maturity_risk
FROM service_floor_maturity_evaluation
ORDER BY current_maturity_ceiling, service_floor_id;

CREATE VIEW v_owner_templates_not_localized AS
SELECT service_floor_id, gate_id, status, observed_value, explanation
FROM service_floor_gate_evaluation
WHERE gate_id = 'G_OWNER_LOCALIZED' AND applies = 'true' AND status IN ('fail','template_only');

CREATE VIEW v_evidence_semantic_refactor_status AS
SELECT evidence_id, file_id, evidence_class, claim_effect_role, semantic_refactor_status
FROM evidence_item
WHERE claim_effect_role = 'unknown';

CREATE VIEW v_route_self_references AS
SELECT from_id, to_id, inferred_relation_type AS relation_type, route_audit_status
FROM route_edge
WHERE self_loop_flag = 'true';

CREATE VIEW v_route_loose_edges_for_review AS
SELECT from_id, to_id, inferred_relation_type AS relation_type, confidence, inference_rule
FROM route_edge
WHERE inferred_relation_type = 'routes_to';

CREATE VIEW v_gate_coverage_summary AS
SELECT gate_id, gate_family, applies_count, pass_count, template_only_count, fail_count, not_applicable_count, blocking_cap, status
FROM assurance_gate_coverage_summary;
