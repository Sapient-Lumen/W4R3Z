-- Query views for rev0293: nuclear operations, availability, outage, maintenance and operating-experience audit

DROP VIEW IF EXISTS v_nuclear_operations_gaps;
CREATE VIEW v_nuclear_operations_gaps AS
SELECT service_floor_id, nuclear_gate_id, gap_type, priority, required_action, required_table, maturity_cap_if_unclosed
FROM nuclear_assurance_gap_backlog
WHERE nuclear_gate_id IN ('NG_41','NG_42','NG_43','NG_44','NG_45','NG_46','NG_47','NG_48','NG_49','NG_50','NG_51','NG_52');

DROP VIEW IF EXISTS v_nuclear_operations_service_floors;
CREATE VIEW v_nuclear_operations_service_floors AS
SELECT m.service_floor_id, m.nuclear_policy_status, a.nuclear_relevance_class, a.operations_gate_present, s.maturity_ceiling, s.template_only_gate_count, s.blocking_gate_ids
FROM nuclear_service_floor_map m
LEFT JOIN nuclear_operations_propagation_audit a USING(service_floor_id)
LEFT JOIN service_floor_assurance_scorecard s USING(service_floor_id)
WHERE a.nuclear_relevance_class LIKE '%operations%' OR m.service_floor_id LIKE '%operation%' OR m.service_floor_id LIKE '%outage%' OR m.service_floor_id LIKE '%maintenance%' OR m.service_floor_id LIKE '%performance%';

DROP VIEW IF EXISTS v_nuclear_gate_family_counts;
CREATE VIEW v_nuclear_gate_family_counts AS
SELECT gate_family, COUNT(*) AS gate_count
FROM nuclear_assurance_gate
GROUP BY gate_family;

DROP VIEW IF EXISTS v_nuclear_operations_sources;
CREATE VIEW v_nuclear_operations_sources AS
SELECT source_id, source_title, source_role, used_in_files
FROM nuclear_source_quality_audit
WHERE created_revision='rev0293';

DROP VIEW IF EXISTS v_rev0293_validation;
CREATE VIEW v_rev0293_validation AS
SELECT rule_id, result, detail
FROM validation_report_rev0293;
