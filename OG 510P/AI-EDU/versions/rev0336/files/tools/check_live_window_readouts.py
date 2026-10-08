import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / 'examples' / 'live-window-readouts'
SCHEMA_PATH = ROOT / 'schemas' / 'live-window-readout.schema.json'
SRC_ORDER = {'SRC0': 0, 'SRC1': 1, 'SRC2': 2, 'SRC3': 3, 'SRC4': 4, 'SRCX': -1}
READOUT_STATES = {'blocked_no_real_packet', 'blocked_incomplete_window', 'ready_for_readout', 'readout_complete', 'quarantined'}
DISPOSITIONS = {'blocked_no_real_packet', 'stopped', 'rolled_back', 'continue_bounded', 'rerun_narrower', 'quarantine', 'no_change'}
CLAIM_EFFECTS = {'strengthen', 'unchanged', 'narrow', 'remove', 'unmade'}
CLAIM_FAMILIES = {'CL-LEARN', 'CL-TASK', 'CL-ACCESS', 'CL-WORKLOAD', 'CL-VALIDITY', 'CL-SAFETY', 'CL-SECURITY', 'CL-CONTEST', 'CL-COMPLIANCE'}
LAUNDERING_WORDS = {'prove', 'proven', 'guarantee', 'scale-ready', 'effective', 'compliant', 'safe for all'}


def fail(errors, rel, msg):
    errors.append(f'{rel}: {msg}')


def parse_date(value, errors, rel, field):
    try:
        date.fromisoformat(value)
    except Exception:
        fail(errors, rel, f'{field} must be ISO date')


def nonempty(value):
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return len(value) > 0
    if isinstance(value, dict):
        return bool(value)
    return value is not None


def load_ids(folder, key):
    ids = set()
    for path in folder.glob('*.json'):
        ids.add(json.loads(path.read_text(encoding='utf-8')).get(key))
    return ids


service_record_ids = load_ids(ROOT / 'examples' / 'service-records', 'record_id')
ft_items = json.loads((ROOT / 'FOLLOWTHROUGH_QUEUE.json').read_text(encoding='utf-8'))['items']
ft_state = {item['id']: item.get('state') for item in ft_items}


def validate(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    errors = []
    data = json.loads(path.read_text(encoding='utf-8'))
    required = [
        'readout_id', 'title', 'related_followthrough', 'service_record_id',
        'live_window_card_id', 'readout_state', 'source_truth_class',
        'window_disposition', 'closure_permitted', 'aggregate_evidence_read',
        'claim_family_effects', 'decision_delta_allowed',
        'fields_to_trim_before_next_request', 'rollback_or_stop_outcome',
        'public_language_after_readout', 'next_action', 'reviewer_calibration',
        'closure_boundary', 'last_reviewed'
    ]
    for field in required:
        if field not in data or not nonempty(data[field]):
            fail(errors, rel, f'missing or empty {field}')
    if errors:
        return errors

    if not data['readout_id'].startswith('LWR-'):
        fail(errors, rel, 'readout_id must start LWR-')
    if not data['live_window_card_id'].startswith('LWC-'):
        fail(errors, rel, 'live_window_card_id must start LWC-')
    if data['related_followthrough'] not in ft_state:
        fail(errors, rel, 'related_followthrough not found')
    if data['service_record_id'] not in service_record_ids:
        fail(errors, rel, f'unknown service_record_id {data["service_record_id"]}')
    if data['readout_state'] not in READOUT_STATES:
        fail(errors, rel, 'readout_state invalid')
    if data['source_truth_class'] not in SRC_ORDER:
        fail(errors, rel, 'source_truth_class invalid')
    if data['window_disposition'] not in DISPOSITIONS:
        fail(errors, rel, 'window_disposition invalid')
    parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')

    aggregate = data.get('aggregate_evidence_read', {})
    for field in [
        'attempted_before_hint', 'answer_giving_or_construct', 'fallback_or_opt_out',
        'stop_trigger_counts', 'workload_minutes', 'notice_and_non_ai_route', 'field_survival'
    ]:
        if field not in aggregate or not nonempty(aggregate[field]):
            fail(errors, rel, f'aggregate_evidence_read.{field} missing or empty')

    seen_claims = set()
    for idx, row in enumerate(data.get('claim_family_effects', [])):
        prefix = f'claim_family_effects[{idx}]'
        for field in [
            'claim_family', 'pre_window_claim_ceiling', 'aggregate_evidence_read',
            'decision_effect', 'public_phrase_after_readout', 'what_this_does_not_prove'
        ]:
            if field not in row or not nonempty(row[field]):
                fail(errors, rel, f'{prefix}.{field} missing or empty')
        claim = row.get('claim_family')
        if claim in seen_claims:
            fail(errors, rel, f'duplicate claim_family {claim}')
        seen_claims.add(claim)
        if claim not in CLAIM_FAMILIES:
            fail(errors, rel, f'{prefix}.claim_family invalid')
        if row.get('decision_effect') not in CLAIM_EFFECTS:
            fail(errors, rel, f'{prefix}.decision_effect invalid')
        limits = row.get('what_this_does_not_prove', '').lower()
        if 'does not prove' not in limits:
            fail(errors, rel, f'{prefix}.what_this_does_not_prove must say does not prove')
        public = row.get('public_phrase_after_readout', '').lower()
        if SRC_ORDER.get(data['source_truth_class'], -1) < 2 and any(word in public for word in LAUNDERING_WORDS):
            fail(errors, rel, f'{prefix}.public phrase appears to launder weak evidence')
        if row.get('decision_effect') == 'strengthen' and SRC_ORDER.get(data['source_truth_class'], -1) < 2:
            fail(errors, rel, f'{prefix}.strengthen requires SRC2+ source truth')

    calibration = data.get('reviewer_calibration', {})
    for field in ['reviewer_count', 'unresolved_disagreements', 'calibration_required_before_closure']:
        if field not in calibration:
            fail(errors, rel, f'reviewer_calibration.{field} missing')
    if calibration.get('reviewer_count', 0) < 1:
        fail(errors, rel, 'reviewer_calibration.reviewer_count must be at least 1')

    closure = data.get('closure_permitted')
    if closure:
        if SRC_ORDER.get(data['source_truth_class'], -1) < 2:
            fail(errors, rel, 'closure requires source_truth_class SRC2 or stronger')
        if data['readout_state'] != 'readout_complete':
            fail(errors, rel, 'closure requires readout_complete')
        if data['window_disposition'] != 'continue_bounded':
            fail(errors, rel, 'closure can only be considered after continue_bounded disposition')
        if calibration.get('calibration_required_before_closure') is True:
            fail(errors, rel, 'closure cannot be permitted while calibration is still required')
        if calibration.get('unresolved_disagreements'):
            fail(errors, rel, 'closure requires no unresolved reviewer disagreements')
        if any(row.get('decision_effect') == 'unmade' for row in data.get('claim_family_effects', [])):
            fail(errors, rel, 'closure cannot rely on unmade claim-family effects')
    else:
        if data['related_followthrough'] == 'FT-0181':
            text = ' '.join([
                data.get('closure_boundary', ''), data.get('next_action', ''),
                data.get('public_language_after_readout', '')
            ]).lower()
            if 'does not close ft-0181' not in text and 'no real' not in text:
                fail(errors, rel, 'non-closure FT-0181 readout must keep closure boundary visible')

    if data['readout_state'] == 'blocked_no_real_packet':
        if data['source_truth_class'] != 'SRC0':
            fail(errors, rel, 'blocked_no_real_packet readouts must use SRC0')
        if data['window_disposition'] != 'blocked_no_real_packet':
            fail(errors, rel, 'blocked_no_real_packet readouts must use blocked_no_real_packet disposition')
        if data['closure_permitted'] is not False:
            fail(errors, rel, 'blocked readouts cannot permit closure')
        if not calibration.get('calibration_required_before_closure'):
            fail(errors, rel, 'blocked readouts must require calibration before closure')

    boundary = data.get('closure_boundary', '').lower()
    if 'does not close ft-0181' not in boundary:
        fail(errors, rel, 'closure_boundary must say it does not close FT-0181')
    if 'does not prove' not in boundary:
        fail(errors, rel, 'closure_boundary must say it does not prove service claims')
    return errors


schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU live-window readout':
    raise SystemExit('live-window readout schema title mismatch')

paths = sorted(DIR.glob('*.json'))
if not paths:
    raise SystemExit('no live-window readouts found')

all_errors = []
closure_ready = 0
for path in paths:
    data = json.loads(path.read_text(encoding='utf-8'))
    if data.get('closure_permitted'):
        closure_ready += 1
    all_errors.extend(validate(path))

if ft_state.get('FT-0181') == 'done' and closure_ready == 0:
    all_errors.append('FT-0181 is done but no live-window readout permits closure')

if all_errors:
    raise SystemExit('live-window readout validation errors:\n' + '\n'.join(all_errors))
print(f'check_live_window_readouts: OK ({len(paths)} readouts, {closure_ready} closure-ready)')
