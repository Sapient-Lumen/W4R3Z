import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / 'examples' / 'post-readout-actions'
SCHEMA_PATH = ROOT / 'schemas' / 'post-readout-action.schema.json'
SRC_ORDER = {'SRC0': 0, 'SRC1': 1, 'SRC2': 2, 'SRC3': 3, 'SRC4': 4, 'SRCX': -1}
ACTION_STATES = {'blocked_no_real_readout', 'ready_for_owner_action', 'owner_action_complete', 'quarantined', 'rolled_back', 'closed_no_change'}
LANES = {'blocked_no_real_packet', 'stop', 'rollback_confirmed', 'rerun_narrower', 'continue_same_ceiling', 'quarantine', 'no_change_trim'}
DISPOSITION_TO_LANE = {
    'blocked_no_real_packet': 'blocked_no_real_packet',
    'stopped': 'stop',
    'rolled_back': 'rollback_confirmed',
    'continue_bounded': 'continue_same_ceiling',
    'rerun_narrower': 'rerun_narrower',
    'quarantine': 'quarantine',
    'no_change': 'no_change_trim',
}
FORBIDDEN_NEXT_ASK = [
    'raw learner trace', 'raw learner traces', 'full transcript', 'protected-route facts',
    'accommodation details', 'small-cell', 'raw security payload', 'exploit string',
    'vendor-authored outcome', 'vendor-authored effectiveness'
]
OVERCLAIM_WORDS = {'prove', 'proven', 'effective', 'scale-ready', 'compliant', 'safe for all', 'guarantee'}
FT_LIVE_PUBLIC_LANGUAGE_MARKERS_BY_LANE = {
    'blocked_no_real_packet': {'example-only', 'frozen', 'no pilot', 'no real'},
    'stop': {'suppress', 'remove', 'no public'},
    'rollback_confirmed': {'narrow', 'suppress', 'remove'},
    'rerun_narrower': {'frozen', 'same ceiling', 'example-only', 'no public', 'no stronger'},
    'continue_same_ceiling': {'frozen', 'same ceiling', 'example-only', 'no public', 'no stronger'},
    'quarantine': {'suppress', 'remove', 'quarantine'},
    'no_change_trim': {'no public', 'no change', 'frozen', 'same ceiling'},
}
PUBLIC_LANGUAGE_PROMOTION_TERMS = {
    'upgrade public', 'public claim upgrade', 'promote', 'stronger public',
    'publish outcome', 'scale-ready', 'prove', 'proven', 'guarantee',
}


def has_marker(text: str, markers: set[str]) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in markers)


def load_ids(folder, key):
    ids = {}
    if folder.exists():
        for path in folder.glob('*.json'):
            data = json.loads(path.read_text(encoding='utf-8'))
            ids[data.get(key)] = data
    return ids

service_records = load_ids(ROOT / 'examples' / 'service-records', 'record_id')
live_window_readouts = load_ids(ROOT / 'examples' / 'live-window-readouts', 'readout_id')
ft_items = json.loads((ROOT / 'FOLLOWTHROUGH_QUEUE.json').read_text(encoding='utf-8'))['items']
ft_state = {item['id']: item.get('state') for item in ft_items}


def fail(errors, rel, msg):
    errors.append(f'{rel}: {msg}')


def nonempty(value):
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return len(value) > 0 and all(nonempty(v) for v in value)
    if isinstance(value, dict):
        return bool(value)
    return value is not None


def parse_date(value, errors, rel, field):
    try:
        date.fromisoformat(value)
    except Exception:
        fail(errors, rel, f'{field} must be ISO date')


def validate(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    data = json.loads(path.read_text(encoding='utf-8'))
    return validate_payload(data, rel)


def validate_payload(data, rel):
    errors = []
    required = [
        'action_id', 'title', 'related_followthrough', 'service_record_id', 'readout_id',
        'action_state', 'dispatch_lane', 'source_truth_class', 'closure_permitted',
        'owner_action', 'allowed_actions_before_next_review',
        'prohibited_actions_before_next_review', 'next_evidence_ask', 'fields_to_reask',
        'fields_to_drop', 'public_language_action', 'due_or_recheck_date',
        'closure_boundary', 'last_reviewed'
    ]
    for field in required:
        if field not in data or not nonempty(data[field]):
            fail(errors, rel, f'missing or empty {field}')
    if errors:
        return errors

    if not data['action_id'].startswith('PRA-'):
        fail(errors, rel, 'action_id must start PRA-')
    if data['related_followthrough'] not in ft_state:
        fail(errors, rel, 'related_followthrough not found')
    if data['service_record_id'] not in service_records:
        fail(errors, rel, f'unknown service_record_id {data["service_record_id"]}')
    if data['readout_id'] not in live_window_readouts:
        fail(errors, rel, f'unknown readout_id {data["readout_id"]}')
    if data['action_state'] not in ACTION_STATES:
        fail(errors, rel, 'action_state invalid')
    if data['dispatch_lane'] not in LANES:
        fail(errors, rel, 'dispatch_lane invalid')
    if data['source_truth_class'] not in SRC_ORDER:
        fail(errors, rel, 'source_truth_class invalid')
    parse_date(data['due_or_recheck_date'], errors, rel, 'due_or_recheck_date')
    parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')

    readout = live_window_readouts.get(data['readout_id'], {})
    expected_lane = DISPOSITION_TO_LANE.get(readout.get('window_disposition'))
    if expected_lane and data['dispatch_lane'] != expected_lane:
        fail(errors, rel, f'dispatch_lane {data["dispatch_lane"]} does not match readout disposition {readout.get("window_disposition")}')
    if SRC_ORDER.get(data['source_truth_class'], -1) > SRC_ORDER.get(readout.get('source_truth_class'), -1):
        fail(errors, rel, 'post-readout action source_truth_class cannot exceed referenced readout')
    if data['closure_permitted']:
        if SRC_ORDER.get(data['source_truth_class'], -1) < 2:
            fail(errors, rel, 'closure requires SRC2+ source truth')
        if data['action_state'] != 'owner_action_complete':
            fail(errors, rel, 'closure requires owner_action_complete')
    else:
        boundary_text = ' '.join([
            data.get('closure_boundary', ''), data.get('public_language_action', ''),
            data.get('owner_action', '')
        ]).lower()
        if data['related_followthrough'] == 'FT-0181' and 'does not close ft-0181' not in boundary_text:
            fail(errors, rel, 'non-closure FT-0181 action must keep closure boundary visible')

    if readout.get('readout_state') == 'blocked_no_real_packet':
        if data['action_state'] != 'blocked_no_real_readout':
            fail(errors, rel, 'blocked readouts require blocked_no_real_readout action state')
        if data['dispatch_lane'] != 'blocked_no_real_packet':
            fail(errors, rel, 'blocked readouts require blocked_no_real_packet dispatch lane')
        if data['source_truth_class'] != 'SRC0':
            fail(errors, rel, 'blocked post-readout actions must use SRC0')
        if data['closure_permitted'] is not False:
            fail(errors, rel, 'blocked post-readout actions cannot permit closure')

    if data['dispatch_lane'] == 'continue_same_ceiling':
        if readout.get('readout_state') != 'readout_complete' or readout.get('window_disposition') != 'continue_bounded':
            fail(errors, rel, 'continue_same_ceiling requires completed continue_bounded readout')
        if SRC_ORDER.get(data['source_truth_class'], -1) < 2:
            fail(errors, rel, 'continue_same_ceiling requires SRC2+ source truth')
        combined = ' '.join(data.get('prohibited_actions_before_next_review', [])).lower()
        for phrase in ['no expansion', 'stronger public', 'schema']:
            if phrase not in combined:
                fail(errors, rel, f'continue_same_ceiling prohibitions must include {phrase}')

    next_ask = data.get('next_evidence_ask', {})
    for field in ['owner_route', 'date_range', 'packet_ceiling', 'decision_question', 'field_minimization_rule', 'fallback_if_unavailable']:
        if field not in next_ask or not nonempty(next_ask[field]):
            fail(errors, rel, f'next_evidence_ask.{field} missing or empty')
    ask_text = json.dumps(next_ask).lower() + ' ' + ' '.join(data.get('fields_to_reask', [])).lower()
    for bad in FORBIDDEN_NEXT_ASK:
        # It is valid to name forbidden material in fields_to_drop/prohibitions, but not in the next ask.
        if bad in ask_text:
            fail(errors, rel, f'next evidence ask appears to request forbidden material: {bad}')
    drop_text = ' '.join(data.get('fields_to_drop', [])).lower()
    for phrase in ['raw learner', 'protected', 'small-cell', 'security', 'vendor']:
        if phrase not in drop_text:
            fail(errors, rel, f'fields_to_drop must explicitly drop {phrase} material')
    public = data.get('public_language_action', '').lower()
    if SRC_ORDER.get(data['source_truth_class'], -1) < 2 and any(word in public for word in OVERCLAIM_WORDS):
        fail(errors, rel, 'public_language_action appears to overclaim weak evidence')
    if data['related_followthrough'] == 'FT-0181' and ft_state.get('FT-0181') != 'done':
        if data.get('closure_permitted') is not False:
            fail(errors, rel, 'live FT-0181 post-readout actions cannot permit closure')
        markers = FT_LIVE_PUBLIC_LANGUAGE_MARKERS_BY_LANE.get(data.get('dispatch_lane'), set())
        if markers and not has_marker(public, markers):
            fail(errors, rel, f'post_readout_action.public_language_action must stay lane-bound for {data.get("dispatch_lane")}: one of {sorted(markers)}')
        for phrase in PUBLIC_LANGUAGE_PROMOTION_TERMS:
            if phrase in public:
                fail(errors, rel, f'post_readout_action.public_language_action contains promotion term while FT-0181 is live: {phrase}')
    boundary = data.get('closure_boundary', '').lower()
    if 'does not close ft-0181' not in boundary:
        fail(errors, rel, 'closure_boundary must say it does not close FT-0181')
    if 'does not prove' not in boundary:
        fail(errors, rel, 'closure_boundary must say it does not prove service claims')

    return errors


schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU post-readout action dispatch':
    raise SystemExit('post-readout action schema title mismatch')

paths = sorted(DIR.glob('*.json'))
if not paths:
    raise SystemExit('no post-readout action dispatches found')

all_errors = []
closure_ready = 0
for path in paths:
    data = json.loads(path.read_text(encoding='utf-8'))
    if data.get('closure_permitted'):
        closure_ready += 1
    all_errors.extend(validate(path))

if paths:
    fixture = json.loads(paths[0].read_text(encoding='utf-8'))
    closure_fixture = dict(fixture)
    closure_fixture['closure_permitted'] = True
    closure_fixture['action_state'] = 'owner_action_complete'
    closure_errors = validate_payload(closure_fixture, 'synthetic/live-ft-closure-leak.json')
    if not any('cannot permit closure' in err for err in closure_errors):
        all_errors.append('synthetic/live-ft-closure-leak.json: live FT closure-permitted regression was not blocked')

    public_fixture = dict(fixture)
    public_fixture['public_language_action'] = 'Promote a stronger public outcome claim from the post-readout action.'
    public_errors = validate_payload(public_fixture, 'synthetic/live-ft-public-promotion-leak.json')
    if not any('lane-bound' in err or 'promotion term' in err for err in public_errors):
        all_errors.append('synthetic/live-ft-public-promotion-leak.json: live FT public-language promotion regression was not blocked')

if ft_state.get('FT-0181') == 'done' and closure_ready == 0:
    all_errors.append('FT-0181 is done but no post-readout action permits closure')

if all_errors:
    raise SystemExit('post-readout action validation errors:\n' + '\n'.join(all_errors))
print(f'check_post_readout_actions: OK ({len(paths)} actions, {closure_ready} closure-ready)')
