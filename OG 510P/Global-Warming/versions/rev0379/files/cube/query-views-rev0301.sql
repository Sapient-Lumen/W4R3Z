
-- rev0301 nuclear climate resilience and compound-hazard query views
CREATE VIEW IF NOT EXISTS v_rev0301_nuclear_climate_resilience_service_floors AS
SELECT service_floor_id, scorecard_family, climate_gate_count, climate_specific_gap_count, maturity_ceiling, next_required_action
FROM nuclear_climate_resilience_scorecard;

CREATE VIEW IF NOT EXISTS v_rev0301_climate_gap_backlog AS
SELECT service_floor_id, nuclear_gate_id, priority, required_action, maturity_cap_if_unclosed
FROM nuclear_climate_resilience_gap_backlog;

CREATE VIEW IF NOT EXISTS v_rev0301_station_blackout_and_spent_fuel_gaps AS
SELECT service_floor_id, nuclear_gate_id, required_action
FROM nuclear_climate_resilience_gap_backlog
WHERE nuclear_gate_id IN ('NG_179','NG_180','NG_181','NG_182');

CREATE VIEW IF NOT EXISTS v_rev0301_emergency_planning_access_gaps AS
SELECT service_floor_id, public_pathway, climate_stress_case, accessibility_requirement, status
FROM nuclear_emergency_planning_climate_access;

CREATE VIEW IF NOT EXISTS v_rev0301_climate_source_authority AS
SELECT source_id, source_title, source_role, authority_tier, use_boundary
FROM nuclear_climate_source_authority_audit;
