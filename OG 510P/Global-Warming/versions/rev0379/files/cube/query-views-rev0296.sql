-- Rev0296 nuclear system-benefit query views
CREATE VIEW IF NOT EXISTS v_rev0296_nuclear_system_benefit_floors AS
SELECT m.service_floor_id, m.nuclear_relevance, m.preferred_nuclear_path, m.nuclear_policy_status, s.primary_domain, s.source_file_ids
FROM nuclear_service_floor_map m
LEFT JOIN service_floor s ON s.service_floor_id = m.service_floor_id
WHERE m.preferred_nuclear_path LIKE '%system_benefit%' OR s.primary_domain = 'nuclear_system_benefit';

CREATE VIEW IF NOT EXISTS v_rev0296_counterfactual_dispatch_backlog AS
SELECT service_floor_id, nuclear_gate_id, required_table, required_action, maturity_cap_if_unclosed
FROM nuclear_system_benefit_gap_backlog
WHERE nuclear_gate_id IN ('NG_85','NG_86','NG_88','NG_89','NG_93','NG_100');

CREATE VIEW IF NOT EXISTS v_rev0296_lifecycle_externality_backlog AS
SELECT service_floor_id, nuclear_gate_id, required_table, required_action, maturity_cap_if_unclosed
FROM nuclear_system_benefit_gap_backlog
WHERE nuclear_gate_id IN ('NG_87','NG_91','NG_98','NG_99');

CREATE VIEW IF NOT EXISTS v_rev0296_public_health_fossil_displacement AS
SELECT public_health_case_id, displacement_case, required_evidence, EJ_distribution_required, fossil_lock_in_exception_required, benefit_claim_status
FROM nuclear_fossil_displacement_public_health_ledger;

CREATE VIEW IF NOT EXISTS v_rev0296_nuclear_benefit_attribution_risk AS
SELECT service_floor_id, benefit_claim, attribution_status, double_counting_risk, challenge_channel, maturity_cap_if_unresolved
FROM nuclear_benefit_attribution_audit
WHERE double_counting_risk = 'high_until_model_or_local_evidence_supplied';

CREATE VIEW IF NOT EXISTS v_rev0296_portfolio_comparison_questions AS
SELECT portfolio_case_id, comparison_type, portfolio_question, anti_blind_spot_rule, anti_overclaim_rule
FROM nuclear_portfolio_comparison_scorecard;
