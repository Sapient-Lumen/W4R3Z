from __future__ import annotations
from pathlib import Path
import json


def load(root: Path, rel: str):
    return json.loads((root / rel).read_text(encoding='utf-8'))


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    required = [
        'DISCIPLINE-CERTIFICATION-MOBILITY-KERNEL.json', 'EMPLOYMENT-ARTIFACT-TAXONOMY-LEDGER.json',
        'EMPLOYMENT-ROLE-TAXONOMY-LEDGER.json', 'CERTIFICATION-DECERTIFICATION-STATE-MACHINE.json',
        'SEPARATION-REASON-GUARDRAIL.json', 'DISCIPLINE-OUTCOME-TAXONOMY-LEDGER.json',
        'RECORD-DESTRUCTION-CLAUSE-LEDGER.json', 'OFFICER-MOBILITY-INDICATOR-LEDGER.json',
        'POST-SOURCE-INTAKE-GATE.json', 'DECERTIFICATION-APPEAL-GATE-LEDGER.json',
        'WANDERING-DETECTION-GATE-LEDGER.json', 'ARBITRATION-REINSTATEMENT-BRIDGE-LEDGER.json',
        'EMPLOYMENT-IDENTITY-BRIDGE-GATE.json', 'EMPLOYMENT-PUBLIC-DISPLAY-GATE.json',
        'EMPLOYMENT-CORRECTION-ROUTE-LEDGER.json', 'SOURCE-FAMILY-EMPLOYMENT-CERTIFICATION-CROSSWALK.json',
        'EMPLOYMENT-DECISION-RECEIPT-GRAMMAR.json', 'PERSONLESS-MOBILITY-PATH-TEMPLATE-LEDGER.json',
        'SYNTHETIC-EMPLOYMENT-MOBILITY-FIXTURE-LEDGER.json', 'EMPLOYMENT-OFFICE-REENTRY-CARD.json',
        'ROOT-EMPLOYMENT-SURFACE-SHADOW-MAP-REV0027.json', 'RECORD-KIND-OFFICE-MAPPING-AUDIT-REV0027.json',
        'SCHEMA-POINTER-AUDIT-REV0027.json', 'VALIDATOR-FACET-INVENTORY-REV0027.json',
        'VALIDATOR-FACADE-DRIFT-AUDIT-REV0027.json', 'NAMESPACE-MIGRATION-WAVE3-PLAN-REV0027.json',
        'PACKAGE-HYGIENE-AUDIT-REV0027.json', 'REV0027-ROUTE-DECISION-RECEIPT.json', 'REV0027-AUDIT-RECEIPT.json',
        'data/employment/rev0027_employment_artifact_types.json', 'data/employment/rev0027_employment_roles.json',
        'data/employment/rev0027_certification_state_machine.json', 'data/employment/rev0027_separation_reason_taxonomy.json',
        'data/employment/rev0027_discipline_outcome_taxonomy.json', 'data/employment/rev0027_record_destruction_clause_taxonomy.json',
        'data/employment/rev0027_mobility_indicator_taxonomy.json', 'data/employment/rev0027_post_source_intake_gates.json',
        'data/employment/rev0027_decertification_appeal_gates.json', 'data/employment/rev0027_wandering_detection_gates.json',
        'data/employment/rev0027_arbitration_reinstatement_bridge_rules.json',
        'data/employment/rev0027_employment_identity_bridge_gates.json',
        'data/employment/rev0027_employment_public_display_gates.json', 'data/employment/rev0027_employment_correction_routes.json',
        'data/employment/rev0027_source_family_employment_routes.json', 'data/employment/rev0027_employment_decision_receipt_templates.json',
        'data/employment/rev0027_personless_mobility_path_templates.json', 'data/employment/rev0027_synthetic_employment_fixtures.json',
        'tools/validators/rev0027_employment_office_checks.py',
    ]
    for rel in required:
        if not (root / rel).exists():
            errors.append(f'missing rev0027 required file: {rel}')
    if errors:
        return errors
    manifest = load(root, 'RELEASE-MANIFEST.json')
    for key in [
        'live_employment_records_created_rev0027','live_certification_records_created_rev0027','live_discipline_records_created_rev0027',
        'live_decertification_records_created_rev0027','live_mobility_path_records_created_rev0027','live_wandering_alerts_created_rev0027',
        'live_identity_links_created_rev0027','live_officer_records_created_rev0027','person_records_created_rev0027','public_employment_displays_admitted_rev0027',
        'public_wandering_displays_admitted_rev0027','public_claims_admitted_rev0027','payloads_captured_rev0027','payload_hashes_computed_rev0027',
        'destructive_moves_performed_rev0027'
    ]:
        if manifest.get(key, 0) != 0:
            errors.append(f'manifest {key} must be 0')
    for key in ['exports_enabled_rev0027','public_mobility_display_enabled_rev0027','public_wandering_alerts_enabled_rev0027']:
        if manifest.get(key) is not False:
            errors.append(f'manifest {key} must be false')
    tables = [
        ('data/employment/rev0027_employment_artifact_types.json','employment_artifact_types','employment_artifact_type_count',38,'employment_artifact_types_rev0027'),
        ('data/employment/rev0027_employment_roles.json','employment_roles','employment_role_count',24,'employment_roles_rev0027'),
        ('data/employment/rev0027_separation_reason_taxonomy.json','separation_reasons','separation_reason_count',32,'separation_reason_definitions_rev0027'),
        ('data/employment/rev0027_discipline_outcome_taxonomy.json','discipline_outcomes','discipline_outcome_count',34,'discipline_outcome_definitions_rev0027'),
        ('data/employment/rev0027_record_destruction_clause_taxonomy.json','record_destruction_clauses','record_destruction_clause_count',18,'record_destruction_clause_definitions_rev0027'),
        ('data/employment/rev0027_mobility_indicator_taxonomy.json','mobility_indicators','mobility_indicator_count',34,'mobility_indicator_definitions_rev0027'),
        ('data/employment/rev0027_post_source_intake_gates.json','gates','post_source_intake_gate_count',22,'post_source_intake_gates_rev0027'),
        ('data/employment/rev0027_decertification_appeal_gates.json','gates','decertification_appeal_gate_count',18,'decertification_appeal_gates_rev0027'),
        ('data/employment/rev0027_wandering_detection_gates.json','gates','wandering_detection_gate_count',28,'wandering_detection_gates_rev0027'),
        ('data/employment/rev0027_arbitration_reinstatement_bridge_rules.json','rules','arbitration_bridge_rule_count',18,'arbitration_reinstatement_bridge_rules_rev0027'),
        ('data/employment/rev0027_employment_identity_bridge_gates.json','gates','employment_identity_bridge_gate_count',22,'employment_identity_bridge_gates_rev0027'),
        ('data/employment/rev0027_employment_public_display_gates.json','gates','employment_public_display_gate_count',18,'employment_public_display_gates_rev0027'),
        ('data/employment/rev0027_employment_correction_routes.json','routes','employment_correction_route_count',14,'employment_correction_routes_rev0027'),
        ('data/employment/rev0027_source_family_employment_routes.json','routes','source_family_employment_route_count',24,'source_family_employment_routes_rev0027'),
        ('data/employment/rev0027_employment_decision_receipt_templates.json','templates','employment_decision_receipt_template_count',14,'employment_decision_receipt_templates_rev0027'),
        ('data/employment/rev0027_personless_mobility_path_templates.json','templates','personless_mobility_path_template_count',12,'personless_mobility_path_templates_rev0027'),
        ('data/employment/rev0027_synthetic_employment_fixtures.json','fixtures','fixture_count',22,'synthetic_employment_fixtures_rev0027'),
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
    sm = load(root, 'data/employment/rev0027_certification_state_machine.json')
    states, transitions = sm.get('states', []), sm.get('transitions', [])
    all_rows.extend(states + transitions)
    if sm.get('state_count') != len(states) or len(states) != 28:
        errors.append(f'rev0027 certification state count mismatch: {len(states)}')
    if sm.get('transition_count') != len(transitions) or len(transitions) != 40:
        errors.append(f'rev0027 certification transition count mismatch: {len(transitions)}')
    if manifest.get('certification_state_definitions_rev0027') != len(states):
        errors.append('manifest certification_state_definitions_rev0027 mismatch')
    if manifest.get('certification_state_transitions_rev0027') != len(transitions):
        errors.append('manifest certification_state_transitions_rev0027 mismatch')
    family_ids = {f.get('source_family_id') for f in load(root, 'data/source_families/rev0019_source_family_atlas.json').get('source_families', [])}
    route_ids = {r.get('source_family_id') for r in load(root, 'data/employment/rev0027_source_family_employment_routes.json').get('routes', [])}
    if route_ids != family_ids:
        errors.append('rev0027 source-family employment routes must cover all and only rev0019 source families')
    for row in all_rows:
        if row.get('public_claims_admitted_rev0027', 0) != 0:
            errors.append(f"rev0027 row {row.get('record_kind')} admits public claims")
        if row.get('live_records_created_rev0027', 0) != 0:
            errors.append(f"rev0027 row {row.get('record_kind')} creates live records")
        if row.get('person_records_created_rev0027', 0) != 0 or row.get('officer_records_created_rev0027', 0) != 0:
            errors.append(f"rev0027 row {row.get('record_kind')} creates person/officer records")
        for k, v in row.items():
            if k.endswith('enabled_rev0027') and v is True and 'synthetic' not in k:
                errors.append(f"rev0027 row {row.get('record_kind')} enables {k}")
    for fx in load(root, 'data/employment/rev0027_synthetic_employment_fixtures.json').get('fixtures', []):
        if fx.get('uses_live_people_or_real_officers') is not False or fx.get('uses_live_source_payload') is not False:
            errors.append(f"rev0027 fixture {fx.get('synthetic_employment_fixture_id')} uses live data")
    display = load(root, 'data/employment/rev0027_employment_public_display_gates.json')
    if display.get('public_display_enabled_rev0027') is not False:
        errors.append('rev0027 employment public display enabled')
    shadow = load(root, 'ROOT-EMPLOYMENT-SURFACE-SHADOW-MAP-REV0027.json')
    if shadow.get('destructive_moves_performed_rev0027') != 0:
        errors.append('rev0027 root shadow map performed destructive moves')
    schema = load(root, 'SCHEMA-POINTER-AUDIT-REV0027.json')
    if schema.get('machine_schema_enforcement_enabled_rev0027') is not False:
        errors.append('rev0027 schema audit unexpectedly enables universal enforcement')
    vf = load(root, 'VALIDATOR-FACET-INVENTORY-REV0027.json')
    inv = load(root, vf['data_file'])
    if not any(r.get('module_path') == 'tools/validators/rev0027_employment_office_checks.py' and r.get('has_validate_function') is True for r in inv.get('rows', [])):
        errors.append('rev0027 validator inventory does not include rev0027 facet')
    return errors
