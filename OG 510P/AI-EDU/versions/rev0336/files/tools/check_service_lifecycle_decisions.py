import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIFECYCLE_DIR = ROOT / 'examples' / 'service-lifecycle-decisions'
SCHEMA_PATH = ROOT / 'schemas' / 'service-lifecycle-decision.schema.json'
STATES = {'SLC0', 'SLC1', 'SLC2', 'SLC3', 'SLC4', 'SLC5', 'SLC6', 'SLC7', 'SLCX'}
DECISIONS = {'idea_only', 'sandbox', 'pilot', 'continue_bounded', 'scale', 'watch', 'deprecate', 'archive_only', 'quarantine'}
AUTHORITY = {f'AA{i}' for i in range(7)}
EXPIRY = {'not_applicable_example', 'current', 'expiring_soon', 'expired', 'blocked', 'unknown'}
PUBLIC_ACTIONS = {'none', 'draft', 'publish_limited', 'revise_claims', 'remove_active_claims', 'suppress'}
TICKET_STATES = {'blocked_no_real_packet', 'blocked_incomplete_board', 'ready_for_real_packet', 'active_change', 'rolled_back', 'quarantined'}
SRC_ORDER = {'SRC0': 0, 'SRC1': 1, 'SRC2': 2, 'SRC3': 3, 'SRC4': 4, 'SRCX': -1}
CLAIM_CEILINGS = {'example_only_no_outcome_claim', 'draft_only', 'limited_process_claim', 'bounded_outcome_claim_with_expiry', 'suppress'}
WINDOW_STATES = {'blocked_no_real_packet', 'blocked_incomplete_ticket', 'staged', 'active', 'paused', 'rolled_back', 'completed_no_closure', 'quarantined'}
READOUT_STATES = {'blocked_no_real_packet', 'blocked_incomplete_window', 'ready_for_readout', 'readout_complete', 'quarantined'}
READOUT_DISPOSITIONS = {'blocked_no_real_packet', 'stopped', 'rolled_back', 'continue_bounded', 'rerun_narrower', 'quarantine', 'no_change'}
ACTION_STATES = {'blocked_no_real_readout', 'ready_for_owner_action', 'owner_action_complete', 'quarantined', 'rolled_back', 'closed_no_change'}
ACTION_LANES = {'blocked_no_real_packet', 'stop', 'rollback_confirmed', 'rerun_narrower', 'continue_same_ceiling', 'quarantine', 'no_change_trim'}
PUBLIC_LANGUAGE_MARKERS_BY_ACTION_LANE = {
    'blocked_no_real_packet': {'example-only', 'frozen', 'no pilot', 'no real'},
    'stop': {'suppress', 'remove', 'no public'},
    'rollback_confirmed': {'narrow', 'suppress', 'remove'},
    'rerun_narrower': {'frozen', 'same ceiling', 'example-only', 'no public', 'no stronger'},
    'continue_same_ceiling': {'frozen', 'same ceiling', 'example-only', 'no public', 'no stronger'},
    'quarantine': {'suppress', 'remove', 'quarantine'},
    'no_change_trim': {'no public', 'no change', 'frozen', 'same ceiling'},
}
PUBLIC_PROMOTION_TERMS = {
    'upgrade public', 'public claim upgrade', 'promote', 'stronger public',
    'publish outcome', 'scale-ready', 'prove', 'proven', 'guarantee',
}
DISPOSITION_TO_ACTION_LANE = {
    'blocked_no_real_packet': 'blocked_no_real_packet',
    'stopped': 'stop',
    'rolled_back': 'rollback_confirmed',
    'continue_bounded': 'continue_same_ceiling',
    'rerun_narrower': 'rerun_narrower',
    'quarantine': 'quarantine',
    'no_change': 'no_change_trim',
}


def load_service_records():
    ids = {}
    for path in (ROOT / 'examples' / 'service-records').glob('*.json'):
        data = json.loads(path.read_text(encoding='utf-8'))
        ids[data.get('record_id')] = data
    return ids

service_records = load_service_records()

def load_readout_ids():
    ids = {}
    readout_dir = ROOT / 'examples' / 'live-window-readouts'
    if not readout_dir.exists():
        return ids
    for path in readout_dir.glob('*.json'):
        data = json.loads(path.read_text(encoding='utf-8'))
        ids[data.get('readout_id')] = data
    return ids

live_window_readouts = load_readout_ids()

def load_post_readout_action_ids():
    ids = {}
    action_dir = ROOT / 'examples' / 'post-readout-actions'
    if not action_dir.exists():
        return ids
    for path in action_dir.glob('*.json'):
        data = json.loads(path.read_text(encoding='utf-8'))
        ids[data.get('action_id')] = data
    return ids

post_readout_actions = load_post_readout_action_ids()


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
        return len(value) > 0 and all(nonempty(v) for v in value)
    return value is not None


def has_marker(text, markers):
    lowered = str(text).lower()
    return any(marker in lowered for marker in markers)


def validate(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    data = json.loads(path.read_text(encoding='utf-8'))
    return validate_payload(data, rel)


def validate_payload(data, rel):
    errors = []
    required = [
        'decision_id', 'service_record_id', 'service_name', 'lifecycle_state', 'decision',
        'evidence_expiry_result', 'authority_ceiling', 'public_summary_action',
        'continuity_plan', 'retirement_or_watch_triggers', 'decision_board_reference',
        'change_ticket', 'live_window_control', 'end_window_readout', 'post_readout_action', 'next_review_date', 'last_reviewed'
    ]
    for field in required:
        if field not in data or not nonempty(data[field]):
            fail(errors, rel, f'missing or empty {field}')
    if errors:
        return errors

    if not data['decision_id'].startswith('SLC-'):
        fail(errors, rel, 'decision_id must start SLC-')
    if data['service_record_id'] not in service_records:
        fail(errors, rel, f'unknown service_record_id {data["service_record_id"]}')
    if data['lifecycle_state'] not in STATES:
        fail(errors, rel, 'lifecycle_state invalid')
    if data['decision'] not in DECISIONS:
        fail(errors, rel, 'decision invalid')
    if data['evidence_expiry_result'] not in EXPIRY:
        fail(errors, rel, 'evidence_expiry_result invalid')
    if data['authority_ceiling'] not in AUTHORITY:
        fail(errors, rel, 'authority_ceiling invalid')
    if data['public_summary_action'] not in PUBLIC_ACTIONS:
        fail(errors, rel, 'public_summary_action invalid')
    parse_date(data['next_review_date'], errors, rel, 'next_review_date')
    parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')

    state_to_decision = {
        'SLC0': {'idea_only'},
        'SLC1': {'sandbox'},
        'SLC2': {'pilot'},
        'SLC3': {'continue_bounded'},
        'SLC4': {'scale'},
        'SLC5': {'watch'},
        'SLC6': {'deprecate'},
        'SLC7': {'archive_only'},
        'SLCX': {'quarantine'},
    }
    if data['decision'] not in state_to_decision[data['lifecycle_state']]:
        fail(errors, rel, 'decision does not match lifecycle_state')

    if data['decision'] in {'deprecate', 'archive_only', 'quarantine'}:
        if data['public_summary_action'] not in {'remove_active_claims', 'suppress', 'revise_claims'}:
            fail(errors, rel, 'retirement/quarantine decisions must remove, suppress, or revise active claims')
    if data['decision'] in {'scale', 'continue_bounded'} and data['evidence_expiry_result'] in {'expired', 'blocked', 'unknown'}:
        fail(errors, rel, 'active recurring/scale decisions cannot rest on expired, blocked, or unknown evidence')
    if len(data.get('retirement_or_watch_triggers', [])) < 2:
        fail(errors, rel, 'retirement_or_watch_triggers needs at least two entries')


    board_ref = data.get('decision_board_reference', '')
    if board_ref:
        if not (ROOT / board_ref).exists():
            fail(errors, rel, f'decision_board_reference does not exist: {board_ref}')
        if 'first-packet-decision-board' not in board_ref:
            fail(errors, rel, 'decision_board_reference must point to first-packet decision board for FT-0181 lifecycle rows')

    ticket = data.get('change_ticket', {})
    if not isinstance(ticket, dict):
        fail(errors, rel, 'change_ticket must be an object')
    else:
        required_ticket = [
            'ticket_id', 'ticket_state', 'source_truth_required', 'decision_delta_required',
            'allowed_changes', 'prohibited_changes', 'rollback_owner', 'rollback_triggers',
            'public_claim_ceiling', 'closure_boundary'
        ]
        for field in required_ticket:
            if field not in ticket or not nonempty(ticket[field]):
                fail(errors, rel, f'change_ticket.{field} missing or empty')
        if ticket.get('ticket_id') and not str(ticket['ticket_id']).startswith('PCT-'):
            fail(errors, rel, 'change_ticket.ticket_id must start PCT-')
        if ticket.get('ticket_state') not in TICKET_STATES:
            fail(errors, rel, 'change_ticket.ticket_state invalid')
        if ticket.get('source_truth_required') not in SRC_ORDER:
            fail(errors, rel, 'change_ticket.source_truth_required invalid')
        if ticket.get('decision_delta_required') is not True:
            fail(errors, rel, 'change_ticket.decision_delta_required must be true')
        if ticket.get('public_claim_ceiling') not in CLAIM_CEILINGS:
            fail(errors, rel, 'change_ticket.public_claim_ceiling invalid')
        if len(ticket.get('allowed_changes', [])) < 1:
            fail(errors, rel, 'change_ticket.allowed_changes needs at least one entry')
        if len(ticket.get('prohibited_changes', [])) < 2:
            fail(errors, rel, 'change_ticket.prohibited_changes needs at least two entries')
        if len(ticket.get('rollback_triggers', [])) < 2:
            fail(errors, rel, 'change_ticket.rollback_triggers needs at least two entries')
        boundary = ticket.get('closure_boundary', '').lower()
        if 'does not close ft-0181' not in boundary:
            fail(errors, rel, 'change_ticket.closure_boundary must say it does not close FT-0181')
        if data['evidence_expiry_result'] == 'not_applicable_example':
            if ticket.get('ticket_state') not in {'blocked_no_real_packet', 'ready_for_real_packet'}:
                fail(errors, rel, 'example-only lifecycle rows must not carry active change tickets')
            if ticket.get('public_claim_ceiling') not in {'example_only_no_outcome_claim', 'suppress'}:
                fail(errors, rel, 'example-only lifecycle rows must cap public claims to example-only or suppress')
        if data['decision'] in {'scale', 'continue_bounded'}:
            if SRC_ORDER.get(ticket.get('source_truth_required'), -1) < 2:
                fail(errors, rel, 'active bounded/scale lifecycle changes require SRC2+ source truth')
            if ticket.get('ticket_state') != 'active_change':
                fail(errors, rel, 'active bounded/scale lifecycle changes require an active_change ticket')


    window = data.get('live_window_control', {})
    if not isinstance(window, dict):
        fail(errors, rel, 'live_window_control must be an object')
    else:
        required_window = [
            'window_id', 'window_state', 'window_scope', 'allowed_during_window',
            'prohibited_during_window', 'stop_triggers', 'rollback_owner', 'rollback_steps',
            'evidence_readouts_required', 'public_claim_freeze', 'no_expansion_rule', 'closure_boundary'
        ]
        for field in required_window:
            if field not in window or not nonempty(window[field]):
                fail(errors, rel, f'live_window_control.{field} missing or empty')
        if window.get('window_id') and not str(window['window_id']).startswith('LWC-'):
            fail(errors, rel, 'live_window_control.window_id must start LWC-')
        if window.get('window_state') not in WINDOW_STATES:
            fail(errors, rel, 'live_window_control.window_state invalid')
        if window.get('public_claim_freeze') is not True:
            fail(errors, rel, 'live_window_control.public_claim_freeze must be true until FT-0181 closes')
        if len(window.get('prohibited_during_window', [])) < 2:
            fail(errors, rel, 'live_window_control.prohibited_during_window needs at least two entries')
        if len(window.get('stop_triggers', [])) < 2:
            fail(errors, rel, 'live_window_control.stop_triggers needs at least two entries')
        if len(window.get('rollback_steps', [])) < 2:
            fail(errors, rel, 'live_window_control.rollback_steps needs at least two entries')
        if len(window.get('evidence_readouts_required', [])) < 2:
            fail(errors, rel, 'live_window_control.evidence_readouts_required needs at least two entries')
        if 'no expansion' not in window.get('no_expansion_rule', '').lower().replace('-', ' '):
            fail(errors, rel, 'live_window_control.no_expansion_rule must state no expansion')
        if 'does not close ft-0181' not in window.get('closure_boundary', '').lower():
            fail(errors, rel, 'live_window_control.closure_boundary must say it does not close FT-0181')
        if data['evidence_expiry_result'] == 'not_applicable_example':
            if window.get('window_state') != 'blocked_no_real_packet':
                fail(errors, rel, 'example-only lifecycle rows must keep live_window_control blocked_no_real_packet')
        if ticket.get('ticket_state') == 'active_change' and window.get('window_state') not in {'staged', 'active'}:
            fail(errors, rel, 'active change tickets require staged or active live-window control')
        if window.get('window_state') in {'active', 'completed_no_closure'}:
            if SRC_ORDER.get(ticket.get('source_truth_required'), -1) < 2:
                fail(errors, rel, 'active/completed live windows require SRC2+ source truth in the change ticket')



    readout = data.get('end_window_readout', {})
    if not isinstance(readout, dict):
        fail(errors, rel, 'end_window_readout must be an object')
    else:
        required_readout = [
            'readout_id', 'readout_state', 'source_truth_class', 'window_disposition',
            'claim_family_effects_required', 'public_language_after_readout', 'closure_boundary'
        ]
        for field in required_readout:
            if field not in readout or not nonempty(readout[field]):
                fail(errors, rel, f'end_window_readout.{field} missing or empty')
        rid = readout.get('readout_id')
        if rid and not str(rid).startswith('LWR-'):
            fail(errors, rel, 'end_window_readout.readout_id must start LWR-')
        if rid and rid not in live_window_readouts:
            fail(errors, rel, f'end_window_readout.readout_id has no matching readout example: {rid}')
        if readout.get('readout_state') not in READOUT_STATES:
            fail(errors, rel, 'end_window_readout.readout_state invalid')
        if readout.get('source_truth_class') not in SRC_ORDER:
            fail(errors, rel, 'end_window_readout.source_truth_class invalid')
        if readout.get('window_disposition') not in READOUT_DISPOSITIONS:
            fail(errors, rel, 'end_window_readout.window_disposition invalid')
        if readout.get('claim_family_effects_required') is not True:
            fail(errors, rel, 'end_window_readout.claim_family_effects_required must be true')
        if 'does not close ft-0181' not in readout.get('closure_boundary', '').lower():
            fail(errors, rel, 'end_window_readout.closure_boundary must say it does not close FT-0181')
        if 'does not prove' not in readout.get('closure_boundary', '').lower():
            fail(errors, rel, 'end_window_readout.closure_boundary must say it does not prove service claims')
        if data['evidence_expiry_result'] == 'not_applicable_example':
            if readout.get('readout_state') != 'blocked_no_real_packet':
                fail(errors, rel, 'example-only lifecycle rows must keep end_window_readout blocked_no_real_packet')
            if readout.get('source_truth_class') != 'SRC0':
                fail(errors, rel, 'example-only lifecycle readouts must use SRC0')
            if readout.get('window_disposition') != 'blocked_no_real_packet':
                fail(errors, rel, 'example-only lifecycle rows must keep end_window_readout disposition blocked_no_real_packet')
        if window.get('window_state') == 'completed_no_closure':
            if readout.get('readout_state') != 'readout_complete':
                fail(errors, rel, 'completed live windows require readout_complete end_window_readout')
            if readout.get('window_disposition') not in {'continue_bounded', 'rerun_narrower', 'stopped', 'rolled_back', 'quarantine', 'no_change'}:
                fail(errors, rel, 'completed live windows require concrete end-window disposition')
        if window.get('window_state') in {'paused', 'rolled_back', 'quarantined'}:
            if readout.get('window_disposition') not in {'stopped', 'rolled_back', 'quarantine', 'rerun_narrower'}:
                fail(errors, rel, 'paused/rolled-back/quarantined windows require stop/rollback/quarantine disposition')
        if readout.get('readout_state') == 'readout_complete':
            if SRC_ORDER.get(readout.get('source_truth_class'), -1) < 2:
                fail(errors, rel, 'completed end-window readouts require SRC2+ source truth')


    action = data.get('post_readout_action', {})
    if not isinstance(action, dict):
        fail(errors, rel, 'post_readout_action must be an object')
    else:
        required_action = [
            'action_id', 'action_state', 'dispatch_lane', 'source_truth_class',
            'owner_action', 'public_language_action', 'closure_boundary'
        ]
        for field in required_action:
            if field not in action or not nonempty(action[field]):
                fail(errors, rel, f'post_readout_action.{field} missing or empty')
        aid = action.get('action_id')
        if aid and not str(aid).startswith('PRA-'):
            fail(errors, rel, 'post_readout_action.action_id must start PRA-')
        if aid and aid not in post_readout_actions:
            fail(errors, rel, f'post_readout_action.action_id has no matching action example: {aid}')
        if action.get('action_state') not in ACTION_STATES:
            fail(errors, rel, 'post_readout_action.action_state invalid')
        if action.get('dispatch_lane') not in ACTION_LANES:
            fail(errors, rel, 'post_readout_action.dispatch_lane invalid')
        if action.get('source_truth_class') not in SRC_ORDER:
            fail(errors, rel, 'post_readout_action.source_truth_class invalid')
        expected_lane = DISPOSITION_TO_ACTION_LANE.get(readout.get('window_disposition'))
        if expected_lane and action.get('dispatch_lane') != expected_lane:
            fail(errors, rel, 'post_readout_action.dispatch_lane must match end_window_readout.window_disposition')
        if SRC_ORDER.get(action.get('source_truth_class'), -1) > SRC_ORDER.get(readout.get('source_truth_class'), -1):
            fail(errors, rel, 'post_readout_action.source_truth_class cannot exceed end_window_readout source truth')
        if 'does not close ft-0181' not in action.get('closure_boundary', '').lower():
            fail(errors, rel, 'post_readout_action.closure_boundary must say it does not close FT-0181')
        if 'does not prove' not in action.get('closure_boundary', '').lower():
            fail(errors, rel, 'post_readout_action.closure_boundary must say it does not prove service claims')
        if data['evidence_expiry_result'] == 'not_applicable_example':
            if action.get('action_state') != 'blocked_no_real_readout':
                fail(errors, rel, 'example-only lifecycle rows must keep post_readout_action blocked_no_real_readout')
            if action.get('dispatch_lane') != 'blocked_no_real_packet':
                fail(errors, rel, 'example-only lifecycle rows must keep post_readout_action dispatch blocked_no_real_packet')
            if action.get('source_truth_class') != 'SRC0':
                fail(errors, rel, 'example-only lifecycle post-readout actions must use SRC0')
        if readout.get('readout_state') == 'readout_complete' and action.get('action_state') == 'blocked_no_real_readout':
            fail(errors, rel, 'completed readouts require a concrete post-readout action')
        if action.get('dispatch_lane') == 'continue_same_ceiling':
            if action.get('source_truth_class') not in {'SRC2', 'SRC3', 'SRC4'}:
                fail(errors, rel, 'continue_same_ceiling post-readout actions require SRC2+ source truth')
            if 'frozen' not in action.get('public_language_action', '').lower() and 'ceiling' not in action.get('public_language_action', '').lower():
                fail(errors, rel, 'continue_same_ceiling must keep public language frozen or ceiling-bound')
        if 'FT0181' in str(action.get('action_id', '')) or 'FT-0181' in str(action.get('closure_boundary', '')):
            public = str(action.get('public_language_action', '')).lower()
            markers = PUBLIC_LANGUAGE_MARKERS_BY_ACTION_LANE.get(action.get('dispatch_lane'), set())
            if markers and not has_marker(public, markers):
                fail(errors, rel, f'post_readout_action.public_language_action must stay lane-bound for {action.get("dispatch_lane")}: one of {sorted(markers)}')
            for phrase in PUBLIC_PROMOTION_TERMS:
                if phrase in public:
                    fail(errors, rel, f'post_readout_action.public_language_action contains promotion term while FT-0181 is live: {phrase}')

    record = service_records.get(data['service_record_id'], {})
    record_auth = record.get('authority', {}).get('max_action_authority')
    if record_auth and record_auth != data['authority_ceiling']:
        # Allow lifecycle ceiling to be lower than the record only if it is a watch/retire decision.
        if data['decision'] not in {'watch', 'deprecate', 'archive_only', 'quarantine'}:
            fail(errors, rel, 'authority_ceiling must match service record for active decisions')

    return errors


schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU service lifecycle decision':
    raise SystemExit('service lifecycle schema title mismatch')

paths = sorted(LIFECYCLE_DIR.glob('*.json'))
if not paths:
    raise SystemExit('no service lifecycle decisions found')

all_errors = []
for path in paths:
    all_errors.extend(validate(path))

if paths:
    fixture = json.loads(paths[0].read_text(encoding='utf-8'))
    action = dict(fixture.get('post_readout_action', {}))
    action['public_language_action'] = 'Promote a stronger public outcome claim from lifecycle after the post-readout action.'
    fixture['post_readout_action'] = action
    regression_errors = validate_payload(fixture, 'synthetic/service-lifecycle-public-promotion-leak.json')
    if not any('lane-bound' in err or 'promotion term' in err for err in regression_errors):
        all_errors.append('synthetic/service-lifecycle-public-promotion-leak.json: public-language promotion regression was not blocked')

if all_errors:
    raise SystemExit('service lifecycle decision validation errors:\n' + '\n'.join(all_errors))
print(f'check_service_lifecycle_decisions: OK ({len(paths)} decisions)')
