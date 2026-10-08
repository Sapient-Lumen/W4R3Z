-- Query views for rev0289

CREATE VIEW IF NOT EXISTS v_nuclear_service_floor_status AS
SELECT sf.service_floor_id, sf.label, sf.primary_domain,
       sc.maturity_ceiling, sc.gap_count, sc.blocking_gate_ids,
       nmap.preferred_nuclear_path, nmap.nuclear_policy_status
FROM service_floor sf
LEFT JOIN service_floor_assurance_scorecard sc ON sf.service_floor_id = sc.service_floor_id
LEFT JOIN nuclear_service_floor_map nmap ON sf.service_floor_id = nmap.service_floor_id
WHERE sf.service_floor_id LIKE 'nuclear_%';

CREATE VIEW IF NOT EXISTS v_nuclear_gate_backlog AS
SELECT g.nuclear_gap_id, g.service_floor_id, g.nuclear_gate_id,
       ag.gate_family, g.priority, g.required_action, g.maturity_cap_if_unclosed
FROM nuclear_assurance_gap_backlog g
LEFT JOIN nuclear_assurance_gate ag ON g.nuclear_gate_id = ag.nuclear_gate_id;

CREATE VIEW IF NOT EXISTS v_nuclear_counterarguments AS
SELECT counterargument_id, risk_family, counterargument, pro_nuclear_response_requirement,
       blocking_gate_id, closure_status
FROM nuclear_risk_counterargument_ledger;

CREATE VIEW IF NOT EXISTS v_nuclear_policy_preference AS
SELECT preference_id, preference_statement, preference_strength, burden_of_proof_shift,
       guardrail_summary, status
FROM nuclear_policy_preference_ledger;

CREATE VIEW IF NOT EXISTS v_nuclear_route_edges AS
SELECT from_id, from_title, to_id, to_title, inferred_relation_type, edge_status
FROM route_edge
WHERE inferred_relation_type IN ('prioritizes_nuclear_default','requires_nuclear_safety_guardrails',
 'governs_nuclear_delivery','routes_to_nuclear_loadcase','audits_nuclear_preference','nuclearizes');
