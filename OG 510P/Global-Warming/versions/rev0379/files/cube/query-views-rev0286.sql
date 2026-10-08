
-- Rev0286 query views. Tables are imported from cube CSVs with hyphenated names converted to snake_case.
CREATE VIEW v_high_stakes_assurance_gaps AS
SELECT service_floor_id, primary_domain, gap_count, gap_flags, maturity_ceiling, owner_assignment_count,
       localized_owner_assignment_count, access_test_count, recorded_access_test_count, audit_redress_count,
       localized_audit_or_redress_count, control_test_count, dated_control_test_count, contracting_process_count,
       contract_instance_count
FROM service_floor_assurance_scorecard
WHERE high_stakes_flag = 'true' AND CAST(gap_count AS INTEGER) > 0;

CREATE VIEW v_gap_backlog_p1 AS
SELECT gap_id, service_floor_id, gap_type, severity, priority, required_table, required_action, blocking_rule
FROM evidence_gap_backlog
WHERE priority = 'P1';

CREATE VIEW v_referential_integrity_failures AS
SELECT check_id, table_name, field_name, referenced_table, referenced_field, missing_reference_count, sample_missing_values
FROM referential_integrity_report
WHERE status <> 'pass';

CREATE VIEW v_typed_route_summary AS
SELECT relation_type, COUNT(*) AS edge_count
FROM route_edge_table
GROUP BY relation_type
ORDER BY edge_count DESC;

CREATE VIEW v_publication_sensitive_resources AS
SELECT resource, classification, redaction_rule
FROM publication_control
WHERE classification <> 'public';
