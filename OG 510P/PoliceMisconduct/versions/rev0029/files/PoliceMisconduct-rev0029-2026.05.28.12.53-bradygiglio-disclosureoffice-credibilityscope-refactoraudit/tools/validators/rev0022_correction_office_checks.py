"""Rev0022 correction-office validation facet.

This facet checks correction/right-of-reply definitions while `make lint` remains the stable top-level entrypoint.
"""
from __future__ import annotations
from pathlib import Path
import json


def load(root: Path, rel: str):
    return json.loads((root / rel).read_text(encoding='utf-8'))


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    req = load(root, 'data/corrections/rev0022_correction_request_types.json').get('request_types', [])
    sm = load(root, 'data/corrections/rev0022_correction_state_machine.json')
    states = sm.get('states', [])
    transitions = sm.get('transitions', [])
    gates = load(root, 'data/corrections/rev0022_correction_transition_gates.json').get('gates', [])
    replies = load(root, 'data/corrections/rev0022_right_of_reply_routes.json').get('routes', [])
    counter = load(root, 'data/corrections/rev0022_counterevidence_packet_templates.json').get('templates', [])
    actions = load(root, 'data/corrections/rev0022_update_action_matrix.json').get('actions', [])
    abuse = load(root, 'data/corrections/rev0022_abuse_guardrail_patterns.json').get('patterns', [])
    display = load(root, 'data/corrections/rev0022_public_correction_display_gates.json').get('gates', [])
    rollback = load(root, 'data/corrections/rev0022_rollback_receipt_templates.json').get('templates', [])
    cross = load(root, 'data/corrections/rev0022_source_family_correction_crosswalk.json').get('rows', [])
    fixtures = load(root, 'data/corrections/rev0022_synthetic_correction_fixtures.json').get('fixtures', [])
    expected = [(req,18,'request types'),(states,20,'states'),(transitions,34,'transitions'),(gates,22,'gates'),(replies,12,'reply routes'),(counter,15,'counterevidence templates'),(actions,14,'update actions'),(abuse,13,'abuse patterns'),(display,12,'public display gates'),(rollback,12,'rollback receipt templates'),(cross,24,'source-family correction crosswalk rows'),(fixtures,16,'synthetic correction fixtures')]
    for arr, count, label in expected:
        if len(arr) != count:
            errors.append(f'rev0022 expected {count} {label}, found {len(arr)}')
    for collection, id_key in [(req,'correction_request_type_id'),(gates,'correction_gate_id'),(replies,'right_of_reply_route_id'),(rollback,'rollback_receipt_template_id')]:
        for row in collection:
            if row.get('public_claims_admitted_rev0022') != 0:
                errors.append(f"rev0022 row {row.get(id_key)} admits public claims")
            if row.get('live_records_created_rev0022', 0) != 0:
                errors.append(f"rev0022 row {row.get(id_key)} creates live records")
    for fx in fixtures:
        if fx.get('uses_live_people_or_real_incidents') is not False or fx.get('uses_live_source_payload') is not False:
            errors.append(f"rev0022 fixture {fx.get('fixture_id')} uses live data")
    return errors

