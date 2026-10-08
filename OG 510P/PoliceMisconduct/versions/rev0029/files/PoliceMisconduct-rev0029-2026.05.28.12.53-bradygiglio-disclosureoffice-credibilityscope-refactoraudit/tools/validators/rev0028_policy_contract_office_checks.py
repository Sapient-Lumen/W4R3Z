from __future__ import annotations
from pathlib import Path
import json


def load(root: Path, rel: str):
    return json.loads((root / rel).read_text(encoding='utf-8'))


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    required = [
        'POLICY-CONTRACT-GOVERNANCE-KERNEL.json', 'POLICY-ARTIFACT-TAXONOMY-LEDGER.json',
        'POLICY-PROVISION-TAXONOMY-LEDGER.json', 'UNION-CONTRACT-ACCOUNTABILITY-CLAUSE-LEDGER.json',
        'POLICY-CLAUSE-RISK-MATRIX.json', 'POLICY-VERSION-LIFECYCLE-STATE-MACHINE.json',
        'POLICY-EFFECTIVE-DATE-GATE.json', 'POLICY-INCIDENT-BRIDGE-GATE.json',
        'POLICY-EMPLOYMENT-DISCIPLINE-BRIDGE-GATE.json', 'POLICY-LITIGATION-BRIDGE-GATE.json',
        'POLICY-PUBLIC-DISPLAY-GATE.json', 'SOURCE-FAMILY-POLICY-CONTRACT-CROSSWALK.json',
        'POLICY-DECISION-RECEIPT-GRAMMAR.json', 'POLICY-CORRECTION-ROUTE-LEDGER.json',
        'SYNTHETIC-POLICY-CONTRACT-FIXTURE-LEDGER.json', 'POLICY-OFFICE-REENTRY-CARD.json',
        'ROOT-POLICY-SURFACE-SHADOW-MAP-REV0028.json', 'RECORD-KIND-POLICY-OFFICE-MAPPING-AUDIT-REV0028.json',
        'SCHEMA-POINTER-AUDIT-REV0028.json', 'VALIDATOR-FACET-INVENTORY-REV0028.json',
        'VALIDATOR-FACADE-DRIFT-AUDIT-REV0028.json', 'NAMESPACE-MIGRATION-WAVE4-PLAN-REV0028.json',
        'PACKAGE-HYGIENE-AUDIT-REV0028.json', 'REV0028-ROUTE-DECISION-RECEIPT.json', 'REV0028-AUDIT-RECEIPT.json',
        'data/policy/rev0028_policy_artifact_types.json', 'data/policy/rev0028_policy_provision_taxonomy.json',
        'data/policy/rev0028_union_contract_accountability_clauses.json', 'data/policy/rev0028_clause_risk_matrix.json',
        'data/policy/rev0028_policy_version_state_machine.json', 'data/policy/rev0028_effective_date_gates.json',
        'data/policy/rev0028_policy_incident_bridge_gates.json', 'data/policy/rev0028_policy_employment_bridge_gates.json',
        'data/policy/rev0028_policy_litigation_bridge_gates.json', 'data/policy/rev0028_policy_public_display_gates.json',
        'data/policy/rev0028_source_family_policy_routes.json', 'data/policy/rev0028_policy_decision_receipt_templates.json',
        'data/policy/rev0028_policy_correction_routes.json', 'data/policy/rev0028_synthetic_policy_fixtures.json',
        'tools/validators/rev0028_policy_contract_office_checks.py',
    ]
    for rel in required:
        if not (root / rel).exists():
            errors.append(f'missing rev0028 required file: {rel}')
    if errors:
        return errors
    manifest = load(root, 'RELEASE-MANIFEST.json')
    zero_keys = [
        'live_policy_records_created_rev0028','policy_source_rows_created_rev0028','policy_payloads_captured_rev0028',
        'policy_payload_hashes_computed_rev0028','policy_in_effect_claims_admitted_rev0028','department_policy_scores_created_rev0028',
        'policy_incident_links_created_rev0028','policy_employment_links_created_rev0028','policy_litigation_links_created_rev0028',
        'live_officer_records_created_rev0028','person_records_created_rev0028','civilian_records_created_rev0028',
        'public_policy_displays_admitted_rev0028','public_policy_comparisons_admitted_rev0028','public_claims_admitted_rev0028',
        'exports_enabled_count_rev0028','destructive_moves_performed_rev0028'
    ]
    for key in zero_keys:
        if manifest.get(key, 0) != 0:
            errors.append(f'manifest {key} must be 0')
    for key in ['public_policy_display_enabled_rev0028','public_policy_comparison_enabled_rev0028','policy_exports_enabled_rev0028']:
        if manifest.get(key) is not False:
            errors.append(f'manifest {key} must be false')
    tables = [
        ('data/policy/rev0028_policy_artifact_types.json','policy_artifact_types','policy_artifact_type_count',38,'policy_artifact_types_rev0028'),
        ('data/policy/rev0028_policy_provision_taxonomy.json','policy_provisions','policy_provision_count',44,'policy_provision_types_rev0028'),
        ('data/policy/rev0028_union_contract_accountability_clauses.json','union_contract_clauses','union_contract_clause_count',32,'union_contract_accountability_clauses_rev0028'),
        ('data/policy/rev0028_clause_risk_matrix.json','rows','clause_risk_count',24,'policy_clause_risk_rows_rev0028'),
        ('data/policy/rev0028_effective_date_gates.json','gates','effective_date_gate_count',22,'policy_effective_date_gates_rev0028'),
        ('data/policy/rev0028_policy_incident_bridge_gates.json','gates','policy_incident_bridge_gate_count',20,'policy_incident_bridge_gates_rev0028'),
        ('data/policy/rev0028_policy_employment_bridge_gates.json','gates','policy_employment_bridge_gate_count',20,'policy_employment_bridge_gates_rev0028'),
        ('data/policy/rev0028_policy_litigation_bridge_gates.json','gates','policy_litigation_bridge_gate_count',18,'policy_litigation_bridge_gates_rev0028'),
        ('data/policy/rev0028_policy_public_display_gates.json','gates','policy_public_display_gate_count',18,'policy_public_display_gates_rev0028'),
        ('data/policy/rev0028_source_family_policy_routes.json','routes','source_family_policy_route_count',24,'source_family_policy_routes_rev0028'),
        ('data/policy/rev0028_policy_decision_receipt_templates.json','templates','policy_decision_receipt_template_count',14,'policy_decision_receipt_templates_rev0028'),
        ('data/policy/rev0028_policy_correction_routes.json','routes','policy_correction_route_count',12,'policy_correction_routes_rev0028'),
        ('data/policy/rev0028_synthetic_policy_fixtures.json','fixtures','fixture_count',20,'synthetic_policy_fixtures_rev0028'),
    ]
    all_rows = []
    for rel, arr_key, count_key, expected, manifest_key in tables:
        obj = load(root, rel)
        rows = obj.get(arr_key, [])
        all_rows.extend(rows)
        if obj.get(count_key) != len(rows) or len(rows) != expected:
            errors.append(f'{rel} count mismatch: {len(rows)} expected {expected}')
        if manifest.get(manifest_key) != len(rows):
            errors.append(f'manifest {manifest_key} mismatch')
    sm = load(root, 'data/policy/rev0028_policy_version_state_machine.json')
    states, transitions = sm.get('states', []), sm.get('transitions', [])
    all_rows.extend(states + transitions)
    if sm.get('state_count') != len(states) or len(states) != 24:
        errors.append(f'rev0028 policy state count mismatch: {len(states)}')
    if sm.get('transition_count') != len(transitions) or len(transitions) != 42:
        errors.append(f'rev0028 policy transition count mismatch: {len(transitions)}')
    if manifest.get('policy_version_states_rev0028') != len(states):
        errors.append('manifest policy_version_states_rev0028 mismatch')
    if manifest.get('policy_version_transitions_rev0028') != len(transitions):
        errors.append('manifest policy_version_transitions_rev0028 mismatch')
    family_ids = {f.get('source_family_id') for f in load(root, 'data/source_families/rev0019_source_family_atlas.json').get('source_families', [])}
    route_ids = {r.get('source_family_id') for r in load(root, 'data/policy/rev0028_source_family_policy_routes.json').get('routes', [])}
    if route_ids != family_ids:
        errors.append('rev0028 source-family policy routes must cover all and only rev0019 source families')
    for row in all_rows:
        if row.get('public_claims_admitted_rev0028', 0) != 0:
            errors.append(f"rev0028 row {row.get('record_kind')} admits public claims")
        if row.get('live_records_created_rev0028', 0) != 0:
            errors.append(f"rev0028 row {row.get('record_kind')} creates live records")
        if row.get('person_records_created_rev0028', 0) != 0 or row.get('officer_records_created_rev0028', 0) != 0:
            errors.append(f"rev0028 row {row.get('record_kind')} creates person/officer records")
        for k, v in row.items():
            if k.endswith('enabled_rev0028') and v is True and 'synthetic' not in k:
                errors.append(f"rev0028 row {row.get('record_kind')} enables {k}")
    for fx in load(root, 'data/policy/rev0028_synthetic_policy_fixtures.json').get('fixtures', []):
        if fx.get('uses_live_people_or_real_officers') is not False or fx.get('uses_live_source_payload') is not False:
            errors.append(f"rev0028 fixture {fx.get('synthetic_policy_contract_fixture_id')} uses live data")
    display = load(root, 'data/policy/rev0028_policy_public_display_gates.json')
    if display.get('public_display_enabled_rev0028') is not False:
        errors.append('rev0028 policy public display enabled')
    shadow = load(root, 'ROOT-POLICY-SURFACE-SHADOW-MAP-REV0028.json')
    if shadow.get('destructive_moves_performed_rev0028') != 0:
        errors.append('rev0028 root shadow map performed destructive moves')
    schema = load(root, 'SCHEMA-POINTER-AUDIT-REV0028.json')
    if schema.get('machine_schema_enforcement_enabled_rev0028') is not False:
        errors.append('rev0028 schema audit unexpectedly enables universal enforcement')
    vf = load(root, 'VALIDATOR-FACET-INVENTORY-REV0028.json')
    inv = load(root, vf['data_file'])
    if not any(r.get('module_path') == 'tools/validators/rev0028_policy_contract_office_checks.py' and r.get('has_validate_function') is True for r in inv.get('rows', [])):
        errors.append('rev0028 validator inventory does not include rev0028 facet')
    return errors
