from __future__ import annotations
from pathlib import Path
import json


def load(root: Path, rel: str):
    return json.loads((root / rel).read_text(encoding='utf-8'))


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    required = [
        'LITIGATION-SETTLEMENT-SPINE-KERNEL.json', 'LAWSUIT-RECORD-TAXONOMY-LEDGER.json',
        'CASE-PARTY-ROLE-TAXONOMY.json', 'CASE-LIFECYCLE-STATE-MACHINE.json',
        'LEGAL-CLAIM-TYPE-CROSSWALK-LEDGER.json', 'DISPOSITION-AND-RELIEF-TAXONOMY.json',
        'SETTLEMENT-FINANCE-GATE-LEDGER.json', 'SETTLEMENT-NO-ADMISSION-GUARDRAIL.json',
        'PLAINTIFF-PRIVACY-GATE-LEDGER.json', 'QUALIFIED-IMMUNITY-SIGNAL-GATE.json',
        'LITIGATION-INCIDENT-BRIDGE-GATE.json', 'LITIGATION-PUBLIC-DISPLAY-GATE.json',
        'LITIGATION-CORRECTION-ROUTE-LEDGER.json', 'SOURCE-FAMILY-LAWSUIT-SETTLEMENT-CROSSWALK.json',
        'SYNTHETIC-LITIGATION-FIXTURE-LEDGER.json', 'PACKAGE-HYGIENE-AUDIT-REV0026.json',
        'PYCACHE-EXCLUSION-RECEIPT-REV0026.json', 'LITIGATION-SCHEMA-LINKAGE-AUDIT.json',
        'ROOT-LITIGATION-SURFACE-SHADOW-MAP-REV0026.json', 'VALIDATOR-FACET-INVENTORY-REV0026.json',
        'NAMESPACE-MIGRATION-WAVE2-PLAN-REV0026.json', 'REV0026-AUDIT-RECEIPT.json',
        'LITIGATION-OFFICE-REENTRY-CARD.json',
        'data/litigation/rev0026_case_artifact_types.json', 'data/litigation/rev0026_case_party_roles.json',
        'data/litigation/rev0026_case_lifecycle_state_machine.json', 'data/litigation/rev0026_legal_claim_type_taxonomy.json',
        'data/litigation/rev0026_disposition_relief_taxonomy.json', 'data/litigation/rev0026_settlement_finance_field_contracts.json',
        'data/litigation/rev0026_settlement_no_admission_guardrails.json', 'data/litigation/rev0026_plaintiff_privacy_gates.json',
        'data/litigation/rev0026_qualified_immunity_procedural_signal_gates.json', 'data/litigation/rev0026_litigation_incident_bridge_gates.json',
        'data/litigation/rev0026_litigation_public_display_gates.json', 'data/litigation/rev0026_litigation_correction_routes.json',
        'data/litigation/rev0026_source_family_litigation_routes.json', 'data/litigation/rev0026_synthetic_litigation_fixtures.json',
        'tools/validators/rev0026_litigation_office_checks.py',
    ]
    for rel in required:
        if not (root / rel).exists():
            errors.append(f'missing rev0026 required file: {rel}')
    if errors:
        return errors

    manifest = load(root, 'RELEASE-MANIFEST.json')
    for key in [
        'live_lawsuit_records_created_rev0026', 'live_settlement_records_created_rev0026',
        'live_case_party_records_created_rev0026', 'live_finance_records_created_rev0026',
        'live_incident_links_created_rev0026', 'live_identity_links_created_rev0026',
        'settlement_amount_records_admitted_rev0026', 'public_case_displays_admitted_rev0026',
        'public_settlement_displays_admitted_rev0026', 'public_claims_admitted_rev0026',
        'payloads_captured_rev0026', 'payload_hashes_computed_rev0026', 'destructive_moves_performed_rev0026'
    ]:
        if manifest.get(key, 0) != 0:
            errors.append(f'manifest {key} must be 0')
    for key in ['exports_enabled_rev0026', 'public_litigation_display_enabled_rev0026']:
        if manifest.get(key) is not False:
            errors.append(f'manifest {key} must be false')

    tables = [
        ('data/litigation/rev0026_case_artifact_types.json','case_artifact_types','case_artifact_type_count',34,'case_artifact_types_rev0026'),
        ('data/litigation/rev0026_case_party_roles.json','case_party_roles','case_party_role_count',30,'case_party_roles_rev0026'),
        ('data/litigation/rev0026_legal_claim_type_taxonomy.json','legal_claim_types','legal_claim_type_count',41,'legal_claim_types_rev0026'),
        ('data/litigation/rev0026_disposition_relief_taxonomy.json','disposition_relief_types','disposition_relief_count',30,'disposition_relief_types_rev0026'),
        ('data/litigation/rev0026_settlement_finance_field_contracts.json','settlement_finance_fields','settlement_finance_field_count',26,'settlement_finance_fields_rev0026'),
        ('data/litigation/rev0026_settlement_no_admission_guardrails.json','guardrails','no_admission_guardrail_count',18,'settlement_no_admission_guardrails_rev0026'),
        ('data/litigation/rev0026_plaintiff_privacy_gates.json','gates','plaintiff_privacy_gate_count',22,'plaintiff_privacy_gates_rev0026'),
        ('data/litigation/rev0026_qualified_immunity_procedural_signal_gates.json','gates','procedural_signal_gate_count',18,'qualified_immunity_signal_gates_rev0026'),
        ('data/litigation/rev0026_litigation_incident_bridge_gates.json','gates','litigation_incident_bridge_gate_count',18,'litigation_incident_bridge_gates_rev0026'),
        ('data/litigation/rev0026_litigation_public_display_gates.json','gates','litigation_public_display_gate_count',16,'litigation_public_display_gates_rev0026'),
        ('data/litigation/rev0026_litigation_correction_routes.json','routes','litigation_correction_route_count',14,'litigation_correction_routes_rev0026'),
        ('data/litigation/rev0026_source_family_litigation_routes.json','routes','source_family_route_count',24,'source_family_litigation_routes_rev0026'),
        ('data/litigation/rev0026_synthetic_litigation_fixtures.json','fixtures','fixture_count',18,'synthetic_litigation_fixtures_rev0026'),
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

    sm = load(root, 'data/litigation/rev0026_case_lifecycle_state_machine.json')
    states = sm.get('states', [])
    transitions = sm.get('transitions', [])
    all_rows.extend(states + transitions)
    if sm.get('state_count') != len(states) or len(states) != 28:
        errors.append(f'rev0026 case lifecycle state count mismatch: {len(states)}')
    if sm.get('transition_count') != len(transitions) or len(transitions) != 40:
        errors.append(f'rev0026 case lifecycle transition count mismatch: {len(transitions)}')
    if manifest.get('case_lifecycle_states_rev0026') != len(states):
        errors.append('manifest case_lifecycle_states_rev0026 mismatch')
    if manifest.get('case_lifecycle_transitions_rev0026') != len(transitions):
        errors.append('manifest case_lifecycle_transitions_rev0026 mismatch')

    family_ids = {f.get('source_family_id') for f in load(root, 'data/source_families/rev0019_source_family_atlas.json').get('source_families', [])}
    route_ids = {r.get('source_family_id') for r in load(root, 'data/litigation/rev0026_source_family_litigation_routes.json').get('routes', [])}
    if route_ids != family_ids:
        errors.append('rev0026 source family litigation routes must cover all and only rev0019 source families')

    for row in all_rows:
        if row.get('public_claims_admitted_rev0026', 0) != 0:
            errors.append(f"rev0026 row {row.get('record_kind')} admits public claims")
        if row.get('live_records_created_rev0026', 0) != 0:
            errors.append(f"rev0026 row {row.get('record_kind')} creates live records")
        for k, v in row.items():
            if k.endswith('enabled_rev0026') and v is True and 'fixture' not in k:
                errors.append(f"rev0026 row {row.get('record_kind')} enables {k}")
    for fx in load(root, 'data/litigation/rev0026_synthetic_litigation_fixtures.json').get('fixtures', []):
        if fx.get('uses_live_people_or_real_cases') is not False or fx.get('uses_live_source_payload') is not False:
            errors.append(f"rev0026 fixture {fx.get('synthetic_litigation_fixture_id')} uses live data")

    display = load(root, 'data/litigation/rev0026_litigation_public_display_gates.json')
    if display.get('public_display_enabled_rev0026') is not False:
        errors.append('rev0026 litigation display enabled')
    hygiene = load(root, 'PACKAGE-HYGIENE-AUDIT-REV0026.json')
    if hygiene.get('destructive_moves_performed_rev0026') != 0:
        errors.append('rev0026 package hygiene performed destructive moves')
    shadow = load(root, 'ROOT-LITIGATION-SURFACE-SHADOW-MAP-REV0026.json')
    if shadow.get('root_surface_count') != len(shadow.get('rows', [])):
        errors.append('rev0026 root shadow map count mismatch')
    if any(r.get('moved_rev0026') is not False for r in shadow.get('rows', [])):
        errors.append('rev0026 root shadow map moved surfaces')
    schema = load(root, 'LITIGATION-SCHEMA-LINKAGE-AUDIT.json')
    if schema.get('schema_linkage_row_count') != len(schema.get('rows', [])) or len(schema.get('rows', [])) != 15:
        errors.append('rev0026 schema linkage row count mismatch')
    if schema.get('machine_schema_enforcement_enabled_rev0026') is not False:
        errors.append('rev0026 schema linkage enabled machine enforcement unexpectedly')
    vf = load(root, 'VALIDATOR-FACET-INVENTORY-REV0026.json')
    if not any(r.get('module_path') == 'tools/validators/rev0026_litigation_office_checks.py' and r.get('has_validate_function') is True for r in vf.get('rows', [])):
        errors.append('rev0026 validator inventory does not include rev0026 facet')
    pyc = load(root, 'PYCACHE-EXCLUSION-RECEIPT-REV0026.json')
    if pyc.get('packaging_excludes_pycache_rev0026') is not True:
        errors.append('rev0026 pycache exclusion receipt not set')
    return errors
