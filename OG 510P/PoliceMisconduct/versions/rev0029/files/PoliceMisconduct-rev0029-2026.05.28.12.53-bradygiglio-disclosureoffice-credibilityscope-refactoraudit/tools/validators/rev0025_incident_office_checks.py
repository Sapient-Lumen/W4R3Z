from __future__ import annotations
from pathlib import Path
import json


def load(root: Path, rel: str):
    return json.loads((root / rel).read_text(encoding='utf-8'))


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    required = [
        'REV0025-BRANCH-RECONCILIATION-LEDGER.json', 'BRANCH-COLLISION-REPAIR-RECEIPT.json',
        'FOUNDATION-BRANCH-MERGE-INDEX.json', 'INCIDENT-EVENT-SPINE-KERNEL.json',
        'INCIDENT-ROLE-TAXONOMY-LEDGER.json', 'FORCE-AND-CUSTODY-EVENT-TAXONOMY.json',
        'INCIDENT-LIFECYCLE-STATE-MACHINE.json', 'INCIDENT-SOURCE-FAMILY-CROSSWALK.json',
        'INCIDENT-PRIVACY-AND-DUE-PROCESS-GATE.json', 'INCIDENT-PUBLIC-DISPLAY-GATE.json',
        'INCIDENT-MINIMUM-SOURCE-BUNDLE-LEDGER.json', 'INCIDENT-TO-LAWSUIT-SETTLEMENT-BRIDGE.json',
        'SYNTHETIC-INCIDENT-FIXTURE-LEDGER.json', 'ROOT-SURFACE-OFFICE-SHADOW-MAP-REV0025.json',
        'VALIDATOR-BRANCH-MERGE-AUDIT.json', 'INCIDENT-SCHEMA-LINKAGE-AUDIT.json',
        'NAMESPACE-MIGRATION-WAVE1-PLAN-REV0025.json',
        'data/incidents/rev0025_incident_event_types.json',
        'data/incidents/rev0025_incident_roles.json',
        'data/incidents/rev0025_incident_lifecycle_state_machine.json',
        'data/incidents/rev0025_incident_process_link_types.json',
        'data/incidents/rev0025_incident_privacy_due_process_gates.json',
        'data/incidents/rev0025_incident_public_display_gates.json',
        'data/incidents/rev0025_incident_minimum_source_bundle_rules.json',
        'data/incidents/rev0025_incident_source_family_crosswalk.json',
        'data/incidents/rev0025_synthetic_incident_fixtures.json',
        'data/incidents/rev0025_incident_bridge_rules.json',
        'tools/validators/rev0024_identity_office_checks.py',
        'tools/validators/rev0024_civilian_family_dignity_checks.py',
    ]
    for rel in required:
        if not (root / rel).exists():
            errors.append(f'missing rev0025 required file: {rel}')
    if errors:
        return errors

    manifest = load(root, 'RELEASE-MANIFEST.json')
    if manifest.get('branch_collision_resolved_rev0025') is not True:
        errors.append('rev0025 branch collision not marked resolved')
    for key in ['live_incident_records_created_rev0025','live_identity_records_created_rev0025','live_civilian_records_created_rev0025','live_person_records_created_rev0025','live_lawsuit_records_created_rev0025','live_settlement_records_created_rev0025','public_incident_displays_admitted_rev0025','public_claims_admitted_rev0025','destructive_moves_performed_rev0025']:
        if manifest.get(key, 0) != 0:
            errors.append(f'manifest {key} must be 0')
    for key in ['incident_public_display_enabled_rev0025','live_incident_intake_enabled_rev0025']:
        if manifest.get(key) is not False:
            errors.append(f'manifest {key} must be false')

    event_obj = load(root, 'data/incidents/rev0025_incident_event_types.json')
    events = event_obj.get('event_types', [])
    if event_obj.get('event_type_count') != len(events) or len(events) != 40:
        errors.append(f'rev0025 event type count mismatch: {len(events)}')
    roles_obj = load(root, 'data/incidents/rev0025_incident_roles.json')
    roles = roles_obj.get('roles', [])
    if roles_obj.get('role_count') != len(roles) or len(roles) != 28:
        errors.append(f'rev0025 role count mismatch: {len(roles)}')
    sm = load(root, 'data/incidents/rev0025_incident_lifecycle_state_machine.json')
    states = sm.get('states', [])
    transitions = sm.get('transitions', [])
    if sm.get('state_count') != len(states) or len(states) != 22:
        errors.append(f'rev0025 incident state count mismatch: {len(states)}')
    if sm.get('transition_count') != len(transitions) or len(transitions) != 27:
        errors.append(f'rev0025 incident transition count mismatch: {len(transitions)}')
    process = load(root, 'data/incidents/rev0025_incident_process_link_types.json').get('process_link_types', [])
    if len(process) != 24:
        errors.append(f'rev0025 process link count mismatch: {len(process)}')
    privacy = load(root, 'data/incidents/rev0025_incident_privacy_due_process_gates.json').get('gates', [])
    if len(privacy) != 24:
        errors.append(f'rev0025 privacy/due process gate count mismatch: {len(privacy)}')
    display_obj = load(root, 'data/incidents/rev0025_incident_public_display_gates.json')
    display = display_obj.get('gates', [])
    if len(display) != 18 or display_obj.get('public_display_enabled_rev0025') is not False:
        errors.append(f'rev0025 display gate unsafe count/state: {len(display)}')
    bundle = load(root, 'data/incidents/rev0025_incident_minimum_source_bundle_rules.json').get('rules', [])
    if len(bundle) != 14:
        errors.append(f'rev0025 minimum source bundle rule count mismatch: {len(bundle)}')
    fixtures = load(root, 'data/incidents/rev0025_synthetic_incident_fixtures.json').get('fixtures', [])
    if len(fixtures) != 20:
        errors.append(f'rev0025 synthetic incident fixture count mismatch: {len(fixtures)}')
    bridges = load(root, 'data/incidents/rev0025_incident_bridge_rules.json').get('bridge_rules', [])
    if len(bridges) != 12:
        errors.append(f'rev0025 incident bridge count mismatch: {len(bridges)}')
    cross = load(root, 'data/incidents/rev0025_incident_source_family_crosswalk.json').get('rows', [])
    fams = load(root, 'data/source_families/rev0019_source_family_atlas.json').get('source_families', [])
    fam_ids = {f.get('source_family_id') for f in fams}
    if len(cross) != len(fam_ids) or {r.get('source_family_id') for r in cross} != fam_ids:
        errors.append('rev0025 incident source-family crosswalk must cover all and only rev0019 source families')

    all_rows = events + roles + states + transitions + process + privacy + display + bundle + fixtures + bridges + cross
    for row in all_rows:
        if row.get('public_claims_admitted_rev0025', 0) != 0:
            errors.append(f"rev0025 row {row.get('record_kind')} admits public claims")
        if row.get('live_records_created_rev0025', 0) != 0:
            errors.append(f"rev0025 row {row.get('record_kind')} creates live records")
        for k, v in row.items():
            if k.endswith('enabled_rev0025') and v is True and 'fixture' not in k:
                errors.append(f"rev0025 row {row.get('record_kind')} enables {k}")
    for fx in fixtures:
        if fx.get('uses_live_people_or_real_incidents') is not False or fx.get('uses_live_source_payload') is not False:
            errors.append(f"rev0025 fixture {fx.get('synthetic_incident_fixture_id')} uses live data")
    branch = load(root, 'REV0025-BRANCH-RECONCILIATION-LEDGER.json')
    if branch.get('collision_resolved_rev0025') is not True or branch.get('destructive_moves_performed_rev0025') != 0:
        errors.append('rev0025 branch reconciliation unsafe')
    shadow = load(root, 'ROOT-SURFACE-OFFICE-SHADOW-MAP-REV0025.json')
    if shadow.get('root_surface_count') != len(shadow.get('rows', [])):
        errors.append('rev0025 root surface shadow count mismatch')
    if any(r.get('moved_rev0025') is not False for r in shadow.get('rows', [])):
        errors.append('rev0025 root surface shadow performed moves')
    return errors
