-- rev0302 nuclear cyber, digital I&C, AI, OT and security-publication query views
CREATE VIEW IF NOT EXISTS v_rev0302_nuclear_cyber_service_floors AS
SELECT service_floor_id, scorecard_family, cyber_gate_count, cyber_specific_gap_count, maturity_ceiling, next_required_action
FROM nuclear_cyber_scorecard;

CREATE VIEW IF NOT EXISTS v_rev0302_cyber_gap_backlog AS
SELECT service_floor_id, nuclear_gate_id, priority, required_action, maturity_cap_if_unclosed
FROM nuclear_cyber_gap_backlog;

CREATE VIEW IF NOT EXISTS v_rev0302_cyber_sensitive_publication_controls AS
SELECT resource_or_evidence_type, classification, public_release_allowed, redaction_rule
FROM nuclear_cyber_sensitive_publication_control;

CREATE VIEW IF NOT EXISTS v_rev0302_ai_autonomy_boundary AS
SELECT service_floor_id, control_family, minimum_evidence, publication_control, status
FROM nuclear_ai_autonomy_safety_case
WHERE service_floor_id LIKE '%ai%' OR service_floor_id LIKE '%digital_twin%' OR service_floor_id LIKE '%cloud%';

CREATE VIEW IF NOT EXISTS v_rev0302_vendor_remote_access_controls AS
SELECT service_floor_id, control_family, minimum_evidence, owner_role, publication_control, status
FROM nuclear_vendor_remote_access_control
WHERE service_floor_id LIKE '%remote%' OR service_floor_id LIKE '%vendor%' OR service_floor_id LIKE '%grid%' OR service_floor_id LIKE '%telecom%';

CREATE VIEW IF NOT EXISTS v_rev0302_cyber_source_authority AS
SELECT source_id, source_title, authority_tier, use_boundary, security_or_context_limit
FROM nuclear_cyber_source_authority_audit;
