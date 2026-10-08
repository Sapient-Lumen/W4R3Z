-- Query views for Global Warming Archive rev0288
-- Generated 2026-05-26T03:15:00-04:00

CREATE VIEW IF NOT EXISTS v_global_maturity_distribution AS
SELECT maturity_ceiling, COUNT(*) AS service_floor_count
FROM service_floor_assurance_scorecard
GROUP BY maturity_ceiling
ORDER BY service_floor_count DESC;

CREATE VIEW IF NOT EXISTS v_global_gate_blockers AS
SELECT service_floor_id, maturity_ceiling, gap_count, gap_flags, blocking_gate_ids
FROM service_floor_assurance_scorecard
WHERE blocking_gate_ids <> ''
ORDER BY CAST(gap_count AS INTEGER) DESC, service_floor_id;

CREATE VIEW IF NOT EXISTS v_local_fixture_scorecard AS
SELECT service_floor_id, global_template_maturity, local_fixture_maturity, local_gate_pass_count, local_gate_partial_or_missing_count, local_blocking_gate_ids, fixture_status
FROM service_floor_local_assurance_scorecard
ORDER BY CASE WHEN fixture_status='synthetic_not_real_world_evidence' THEN 0 ELSE 1 END, service_floor_id;

CREATE VIEW IF NOT EXISTS v_local_fixture_gaps AS
SELECT service_floor_id, gate_id, gap_type, priority, required_action, fixture_status
FROM local_evidence_gap_backlog
ORDER BY priority, service_floor_id, gate_id;

CREATE VIEW IF NOT EXISTS v_data_quality_failures AS
SELECT rule_id, severity, checked_records, failed_records, details
FROM data_quality_result_rev0288
WHERE passed <> 'true'
ORDER BY severity, rule_id;

CREATE VIEW IF NOT EXISTS v_tag_alias_collisions AS
SELECT tag_id, tag_type, alias_value, canonical_value, alias_kind, status
FROM tag_alias
ORDER BY tag_type, tag_id, alias_value;

CREATE VIEW IF NOT EXISTS v_table_nullability_hotspots AS
SELECT table_name, column_name, blank_count, nonblank_count, distinct_count, inferred_type
FROM table_column_catalog
WHERE CAST(blank_count AS INTEGER) > 0
ORDER BY CAST(blank_count AS INTEGER) DESC, table_name, column_name;

CREATE VIEW IF NOT EXISTS v_referential_integrity_failures AS
SELECT * FROM referential_integrity_report WHERE status <> 'pass';
