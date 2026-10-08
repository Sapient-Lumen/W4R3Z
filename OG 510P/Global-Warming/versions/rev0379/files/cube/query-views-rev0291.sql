-- Query views rev0291: nuclear regulatory legitimacy, security, waste, emergency and traceability audit
DROP VIEW IF EXISTS v_nuclear_regulatory_pathway_gaps;
CREATE VIEW v_nuclear_regulatory_pathway_gaps AS
SELECT m.service_floor_id, m.preferred_nuclear_path, g.nuclear_gate_id, g.gate_family, g.minimum_condition, g.evidence_tables
FROM nuclear_service_floor_map m
JOIN nuclear_assurance_gate g ON instr(';' || m.binding_gate_ids || ';', ';' || g.nuclear_gate_id || ';') > 0
WHERE g.nuclear_gate_id IN ('NG_21','NG_26','NG_27');

DROP VIEW IF EXISTS v_nuclear_public_legitimacy_gaps;
CREATE VIEW v_nuclear_public_legitimacy_gaps AS
SELECT service_floor_id, nuclear_gate_id, required_action, required_table, maturity_cap_if_unclosed, status
FROM nuclear_assurance_gap_backlog
WHERE nuclear_gate_id IN ('NG_22','NG_23','NG_28');

DROP VIEW IF EXISTS v_nuclear_security_emergency_gaps;
CREATE VIEW v_nuclear_security_emergency_gaps AS
SELECT service_floor_id, nuclear_gate_id, required_action, required_table, maturity_cap_if_unclosed, status
FROM nuclear_assurance_gap_backlog
WHERE nuclear_gate_id IN ('NG_24','NG_25');

DROP VIEW IF EXISTS v_nuclear_traceability_matrix_required;
CREATE VIEW v_nuclear_traceability_matrix_required AS
SELECT service_floor_id, nuclear_gate_id, claim_id, evidence_tables, source_ids, owner_roles, public_challenge_path, maturity_cap_if_missing, trace_status
FROM nuclear_assurance_traceability_matrix;

DROP VIEW IF EXISTS v_nuclear_source_misuse_risk;
CREATE VIEW v_nuclear_source_misuse_risk AS
SELECT source_id, source_title, source_role, nuclear_source_class, used_in_files, risk_of_misuse, audit_status
FROM nuclear_source_quality_audit
WHERE risk_of_misuse <> '';

DROP VIEW IF EXISTS v_nuclear_publication_sensitive_resources;
CREATE VIEW v_nuclear_publication_sensitive_resources AS
SELECT resource, classification, reason, redaction_rule
FROM publication_control
WHERE resource LIKE '%nuclear%' AND classification <> 'public';

DROP VIEW IF EXISTS v_rev0291_new_nuclear_service_floors;
CREATE VIEW v_rev0291_new_nuclear_service_floors AS
SELECT service_floor_id, label, primary_domain, source_file_ids
FROM service_floor
WHERE source_file_ids LIKE '%439%' OR source_file_ids LIKE '%440%' OR source_file_ids LIKE '%441%' OR source_file_ids LIKE '%442%' OR source_file_ids LIKE '%443%';
