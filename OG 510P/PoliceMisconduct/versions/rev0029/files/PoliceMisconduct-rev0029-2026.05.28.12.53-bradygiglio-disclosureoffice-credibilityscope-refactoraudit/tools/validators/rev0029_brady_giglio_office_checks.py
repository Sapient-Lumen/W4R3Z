from __future__ import annotations
from pathlib import Path
import json


def load(root: Path, rel: str):
    return json.loads((root / rel).read_text(encoding='utf-8'))


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    required = [
        'BRADY-GIGLIO-DISCLOSURE-KERNEL.json', 'DISCLOSURE-ARTIFACT-TAXONOMY-LEDGER.json',
        'DISCLOSURE-SIGNAL-TAXONOMY-LEDGER.json', 'CREDIBILITY-ISSUE-TAXONOMY-LEDGER.json',
        'DISCLOSURE-LIFECYCLE-STATE-MACHINE.json', 'BRADY-GIGLIO-SCOPE-GATE.json',
        'TESTIMONY-CASE-LINK-GATE.json', 'PROSECUTOR-OFFICE-BOUNDARY-GATE.json',
        'DEFENSE-WORKBENCH-ROUTE-LEDGER.json', 'BRADY-GIGLIO-PUBLIC-DISPLAY-GATE.json',
        'PROTECTIVE-ORDER-SEALING-GUARDRAIL.json', 'BRADY-GIGLIO-ACCESS-BOUNDARY-LEDGER.json',
        'SOURCE-FAMILY-BRADY-GIGLIO-CROSSWALK.json', 'BRADY-GIGLIO-DECISION-RECEIPT-GRAMMAR.json',
        'BRADY-GIGLIO-CORRECTION-ROUTE-LEDGER.json', 'SYNTHETIC-BRADY-GIGLIO-FIXTURE-LEDGER.json',
        'BRADY-GIGLIO-OFFICE-REENTRY-CARD.json', 'ROOT-BRADY-SURFACE-SHADOW-MAP-REV0029.json',
        'RECORD-KIND-BRADY-OFFICE-MAPPING-AUDIT-REV0029.json', 'SCHEMA-POINTER-AUDIT-REV0029.json',
        'VALIDATOR-FACET-INVENTORY-REV0029.json', 'VALIDATOR-FACADE-DRIFT-AUDIT-REV0029.json',
        'NAMESPACE-MIGRATION-WAVE5-PLAN-REV0029.json', 'PACKAGE-HYGIENE-AUDIT-REV0029.json',
        'ARCHIVE-HEAD-REPAIR-RECEIPT-REV0029.json', 'REV0029-ROUTE-DECISION-RECEIPT.json', 'REV0029-AUDIT-RECEIPT.json',
        'data/brady_giglio/rev0029_disclosure_artifact_types.json',
        'data/brady_giglio/rev0029_disclosure_signal_taxonomy.json',
        'data/brady_giglio/rev0029_credibility_issue_taxonomy.json',
        'data/brady_giglio/rev0029_disclosure_lifecycle_state_machine.json',
        'data/brady_giglio/rev0029_scope_gates.json',
        'data/brady_giglio/rev0029_testimony_case_link_gates.json',
        'data/brady_giglio/rev0029_prosecutor_office_boundary_gates.json',
        'data/brady_giglio/rev0029_defense_workbench_routes.json',
        'data/brady_giglio/rev0029_public_display_gates.json',
        'data/brady_giglio/rev0029_correction_routes.json',
        'data/brady_giglio/rev0029_protective_order_sealing_guardrails.json',
        'data/brady_giglio/rev0029_access_boundary_rows.json',
        'data/brady_giglio/rev0029_source_family_brady_routes.json',
        'data/brady_giglio/rev0029_decision_receipt_templates.json',
        'data/brady_giglio/rev0029_synthetic_disclosure_fixtures.json',
        'tools/validators/rev0029_brady_giglio_office_checks.py',
        'docs/40-model/rev0029-brady-giglio-disclosure-office.md', 'docs/00-meta/rev0029-handoff.md',
    ]
    for rel in required:
        if not (root / rel).exists():
            errors.append(f'missing rev0029 required file: {rel}')
    if errors:
        return errors

    manifest = load(root, 'RELEASE-MANIFEST.json')
    zero_keys = [
        'live_brady_giglio_records_created_rev0029', 'officer_list_status_records_created_rev0029',
        'case_specific_nondisclosure_claims_admitted_rev0029', 'testimony_case_links_created_rev0029',
        'public_credibility_labels_admitted_rev0029', 'public_brady_displays_admitted_rev0029',
        'defense_workbench_accounts_created_rev0029', 'payloads_captured_rev0029', 'payload_hashes_computed_rev0029',
        'public_claims_admitted_rev0029', 'live_officer_records_created_rev0029', 'person_records_created_rev0029',
        'civilian_records_created_rev0029', 'destructive_moves_performed_rev0029'
    ]
    for key in zero_keys:
        if manifest.get(key, 0) != 0:
            errors.append(f'manifest {key} must be 0')
    for key in ['law_enforcement_special_access_enabled_rev0029', 'bulk_brady_exports_enabled_rev0029', 'public_display_enabled_rev0029', 'exports_enabled_rev0029']:
        if manifest.get(key) is not False:
            errors.append(f'manifest {key} must be false')

    tables = [
        ('data/brady_giglio/rev0029_disclosure_artifact_types.json','disclosure_artifact_types','disclosure_artifact_type_count',36,'brady_disclosure_artifact_types_rev0029'),
        ('data/brady_giglio/rev0029_disclosure_signal_taxonomy.json','signals','disclosure_signal_count',42,'brady_disclosure_signals_rev0029'),
        ('data/brady_giglio/rev0029_credibility_issue_taxonomy.json','credibility_issues','credibility_issue_count',34,'credibility_issue_categories_rev0029'),
        ('data/brady_giglio/rev0029_scope_gates.json','gates','scope_gate_count',24,'brady_scope_gates_rev0029'),
        ('data/brady_giglio/rev0029_testimony_case_link_gates.json','gates','testimony_case_link_gate_count',20,'testimony_case_link_gates_rev0029'),
        ('data/brady_giglio/rev0029_prosecutor_office_boundary_gates.json','gates','prosecutor_office_boundary_gate_count',18,'prosecutor_office_boundary_gates_rev0029'),
        ('data/brady_giglio/rev0029_defense_workbench_routes.json','routes','defense_workbench_route_count',16,'defense_workbench_routes_rev0029'),
        ('data/brady_giglio/rev0029_public_display_gates.json','gates','public_display_gate_count',18,'brady_public_display_gates_rev0029'),
        ('data/brady_giglio/rev0029_correction_routes.json','routes','correction_route_count',12,'brady_correction_routes_rev0029'),
        ('data/brady_giglio/rev0029_protective_order_sealing_guardrails.json','guardrails','protective_order_guardrail_count',16,'protective_order_guardrails_rev0029'),
        ('data/brady_giglio/rev0029_access_boundary_rows.json','rows','access_boundary_row_count',18,'brady_access_boundary_rows_rev0029'),
        ('data/brady_giglio/rev0029_source_family_brady_routes.json','routes','source_family_brady_route_count',24,'source_family_brady_routes_rev0029'),
        ('data/brady_giglio/rev0029_decision_receipt_templates.json','templates','decision_receipt_template_count',14,'brady_decision_receipt_templates_rev0029'),
        ('data/brady_giglio/rev0029_synthetic_disclosure_fixtures.json','fixtures','fixture_count',22,'synthetic_brady_fixtures_rev0029'),
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

    sm = load(root, 'data/brady_giglio/rev0029_disclosure_lifecycle_state_machine.json')
    states, transitions = sm.get('states', []), sm.get('transitions', [])
    all_rows.extend(states + transitions)
    if sm.get('state_count') != len(states) or len(states) != 26:
        errors.append(f'rev0029 disclosure lifecycle state count mismatch: {len(states)}')
    if sm.get('transition_count') != len(transitions) or len(transitions) != 42:
        errors.append(f'rev0029 disclosure lifecycle transition count mismatch: {len(transitions)}')
    if manifest.get('brady_disclosure_lifecycle_states_rev0029') != len(states):
        errors.append('manifest brady_disclosure_lifecycle_states_rev0029 mismatch')
    if manifest.get('brady_disclosure_lifecycle_transitions_rev0029') != len(transitions):
        errors.append('manifest brady_disclosure_lifecycle_transitions_rev0029 mismatch')

    family_ids = {f.get('source_family_id') for f in load(root, 'data/source_families/rev0019_source_family_atlas.json').get('source_families', [])}
    route_ids = {r.get('source_family_id') for r in load(root, 'data/brady_giglio/rev0029_source_family_brady_routes.json').get('routes', [])}
    if route_ids != family_ids:
        errors.append('rev0029 source-family Brady/Giglio routes must cover all and only rev0019 source families')

    for row in all_rows:
        if row.get('public_claims_admitted_rev0029', 0) != 0:
            errors.append(f"rev0029 row {row.get('record_kind')} admits public claims")
        if row.get('live_records_created_rev0029', 0) != 0:
            errors.append(f"rev0029 row {row.get('record_kind')} creates live records")
        if row.get('person_records_created_rev0029', 0) != 0 or row.get('officer_records_created_rev0029', 0) != 0:
            errors.append(f"rev0029 row {row.get('record_kind')} creates person/officer records")
        for k, v in row.items():
            if k.endswith('enabled_rev0029') and v is True and 'synthetic' not in k:
                errors.append(f"rev0029 row {row.get('record_kind')} enables {k}")

    for fx in load(root, 'data/brady_giglio/rev0029_synthetic_disclosure_fixtures.json').get('fixtures', []):
        if fx.get('uses_live_people_or_real_officers') is not False or fx.get('uses_live_source_payload') is not False:
            errors.append(f"rev0029 fixture {fx.get('synthetic_brady_giglio_fixture_id')} uses live data")

    display = load(root, 'data/brady_giglio/rev0029_public_display_gates.json')
    if display.get('public_display_enabled_rev0029') is not False:
        errors.append('rev0029 public Brady/Giglio display enabled')
    access = load(root, 'data/brady_giglio/rev0029_access_boundary_rows.json')
    if any(r.get('person_specific_access_enabled_rev0029') is True or r.get('aggregate_access_enabled_rev0029') is True for r in access.get('rows', [])):
        errors.append('rev0029 access boundaries unexpectedly enable access')
    shadow = load(root, 'ROOT-BRADY-SURFACE-SHADOW-MAP-REV0029.json')
    if shadow.get('destructive_moves_performed_rev0029') != 0:
        errors.append('rev0029 root shadow map performed destructive moves')
    schema = load(root, 'SCHEMA-POINTER-AUDIT-REV0029.json')
    if schema.get('machine_schema_enforcement_enabled_rev0029') is not False:
        errors.append('rev0029 schema audit unexpectedly enables universal enforcement')
    vf = load(root, 'VALIDATOR-FACET-INVENTORY-REV0029.json')
    inv = load(root, vf['data_file'])
    if not any(r.get('module_path') == 'tools/validators/rev0029_brady_giglio_office_checks.py' and r.get('has_validate_function') is True for r in inv.get('rows', [])):
        errors.append('rev0029 validator inventory does not include rev0029 facet')
    return errors
