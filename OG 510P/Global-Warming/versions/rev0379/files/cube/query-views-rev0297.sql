-- Rev0297 nuclear geopolitical-resilience query views
CREATE VIEW IF NOT EXISTS v_rev0297_nuclear_geopolitical_floors AS
SELECT m.service_floor_id, s.primary_domain, m.preferred_nuclear_path, m.nuclear_policy_status, g.maturity_ceiling
FROM nuclear_service_floor_map m
LEFT JOIN service_floor s ON s.service_floor_id = m.service_floor_id
LEFT JOIN service_floor_assurance_scorecard g ON g.service_floor_id = m.service_floor_id
WHERE s.primary_domain = 'nuclear_geopolitical_resilience' OR m.preferred_nuclear_path LIKE '%geopolitical%';

CREATE VIEW IF NOT EXISTS v_rev0297_allied_supply_chain_risk AS
SELECT service_floor_id, supply_chain_segment, allied_capacity_status, import_dependence_status, qualified_supplier_status, strategic_inventory_status, substitution_plan_status, maturity_cap
FROM nuclear_allied_supply_chain_scorecard;

CREATE VIEW IF NOT EXISTS v_rev0297_export_finance_diplomacy AS
SELECT service_floor_id, agreement_or_finance_element, required_documentation, public_value_guardrail, debt_sustainability_guardrail, nonproliferation_guardrail, maturity_cap
FROM nuclear_export_finance_diplomacy_ledger;

CREATE VIEW IF NOT EXISTS v_rev0297_sanctions_vendor_lockin AS
SELECT service_floor_id, risk_category, risk_statement, continuity_test, exit_rights_required, qualified_substitution_required, maturity_cap
FROM nuclear_sanctions_vendor_lockin_risk_register;

CREATE VIEW IF NOT EXISTS v_rev0297_sensitive_publication_control AS
SELECT resource, classification, reason, redaction_rule
FROM nuclear_geopolitical_sensitive_publication_control;

CREATE VIEW IF NOT EXISTS v_rev0297_source_authority_audit AS
SELECT source_id, authority_class, source_role, appropriate_use, misuse_risk, audit_status
FROM nuclear_source_authority_audit;

CREATE VIEW IF NOT EXISTS v_rev0297_geopolitical_gap_backlog AS
SELECT service_floor_id, nuclear_gate_id, priority, required_action, required_table, maturity_cap_if_unclosed, status
FROM nuclear_geopolitical_gap_backlog;
