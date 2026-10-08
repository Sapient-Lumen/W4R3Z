import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDOFF_DIR = ROOT / 'examples' / 'operator-handoffs'
SCHEMA_PATH = ROOT / 'schemas' / 'operator-handoff.schema.json'
STATES = {'OH0', 'OH1', 'OH2', 'OH3', 'OH4', 'OH5', 'OHX'}

receipt = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
ft_items = json.loads((ROOT / 'FOLLOWTHROUGH_QUEUE.json').read_text(encoding='utf-8'))['items']
live_ft = sorted(item['id'] for item in ft_items if item.get('state') == 'queued')
makefile = (ROOT / 'Makefile').read_text(encoding='utf-8')
CURRENT_LANE_COMMANDS = {
    'python3 tools/run_lint_suite.py --lane owner-reply-field',
    'python3 tools/run_lint_suite.py --lane fast-changed',
    'python3 tools/run_lint_suite.py --lane release-controls',
    'python3 tools/run_lint_suite.py --lane full-release',
}
FIELD_FIRST_ACTIONS = {
    'make owner-field-work',
    'make owner-field-report',
    'make owner-field-next CSV=/path/to/real-owner-return.csv',
}
FORBIDDEN_DIRECT_ACTION_TERMS = (
    'owner-request-packet',
    'owner-returned-reply-work',
    'owner-first-packet-decision',
    'owner-post-decision-change-ticket',
    'owner-activation-receipt',
    'owner-live-window-card',
    'owner-live-window-readout',
    'owner-post-readout-action ',
    'owner-post-readout-recheck ',
    'owner-post-readout-context-receipt',
    'real-import',
    'closeout',
)


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


def validate(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    errors = []
    data = json.loads(path.read_text(encoding='utf-8'))
    required = [
        'handoff_id', 'revision', 'handoff_state', 'remaining_followthrough_ids',
        'required_startup_surfaces', 'required_commands', 'allowed_next_actions',
        'do_not_claim', 'stop_conditions', 'no_fake_import_assertion',
        'first_real_import_unblocker', 'last_reviewed'
    ]
    for field in required:
        if field not in data or not nonempty(data[field]):
            fail(errors, rel, f'missing or empty {field}')
    if errors:
        return errors

    if not data['handoff_id'].startswith('OH-'):
        fail(errors, rel, 'handoff_id must start OH-')
    if data['revision'] != receipt['revision']:
        fail(errors, rel, f'revision {data["revision"]} does not match receipt {receipt["revision"]}')
    if data['handoff_state'] not in STATES:
        fail(errors, rel, 'handoff_state invalid')
    parse_date(data['last_reviewed'], errors, rel, 'last_reviewed')

    if sorted(data['remaining_followthrough_ids']) != live_ft:
        fail(errors, rel, 'remaining_followthrough_ids do not match live queue')

    for surface in data.get('required_startup_surfaces', []):
        if not (ROOT / surface).exists():
            fail(errors, rel, f'required_startup_surface missing: {surface}')

    required_commands = data.get('required_commands', [])
    commands = '\n'.join(required_commands)
    if 'tools/run_lint_suite.py' not in commands:
        fail(errors, rel, 'required_commands must include tools/run_lint_suite.py')
    if '--mode' in commands:
        fail(errors, rel, 'required_commands must use run_lint_suite.py --lane, not obsolete --mode aliases')
    missing_lane_commands = sorted(CURRENT_LANE_COMMANDS - set(required_commands))
    if missing_lane_commands:
        fail(errors, rel, 'required_commands missing current lint lane command(s): ' + '; '.join(missing_lane_commands))
    if 'handoff-release' not in commands:
        fail(errors, rel, 'required_commands must include handoff-release packaging path')
    if 'handoff-release:' not in makefile:
        fail(errors, rel, 'Makefile lacks handoff-release target')

    allowed_next_actions = data.get('allowed_next_actions', [])
    missing_first_actions = sorted(FIELD_FIRST_ACTIONS - set(allowed_next_actions))
    if missing_first_actions:
        fail(errors, rel, 'allowed_next_actions must start from field router/report commands: ' + '; '.join(missing_first_actions))
    for action in allowed_next_actions:
        lowered_action = str(action).lower()
        for term in FORBIDDEN_DIRECT_ACTION_TERMS:
            if term in lowered_action and action not in FIELD_FIRST_ACTIONS:
                fail(errors, rel, f'allowed_next_actions bypasses the router/report first contract: {action}')
                break

    do_not_claim = ' '.join(data.get('do_not_claim', [])).lower()
    for phrase in ['all followthrough', 'real pilot import', 'realistic service records']:
        if phrase not in do_not_claim:
            fail(errors, rel, f'do_not_claim missing phrase: {phrase}')

    if 'FT-0181' in live_ft:
        if data.get('no_fake_import_assertion') is not True:
            fail(errors, rel, 'FT-0181 live requires no_fake_import_assertion=true')
        if 'SRC2+' not in data.get('first_real_import_unblocker', ''):
            fail(errors, rel, 'first_real_import_unblocker must name SRC2+ requirement')
        if data['handoff_state'] not in {'OH2', 'OH3', 'OH4'}:
            fail(errors, rel, 'FT-0181 live should hand off as OH2/OH3/OH4, not closed')

    return errors


schema = json.loads(SCHEMA_PATH.read_text(encoding='utf-8'))
if schema.get('title') != 'AI-EDU operator handoff record':
    raise SystemExit('operator handoff schema title mismatch')

paths = sorted(HANDOFF_DIR.glob('*.json'))
if not paths:
    raise SystemExit('no operator handoff records found')

all_errors = []
for path in paths:
    all_errors.extend(validate(path))

if all_errors:
    raise SystemExit('operator handoff validation errors:\n' + '\n'.join(all_errors))
print(f'check_operator_handoffs: OK ({len(paths)} records, {len(live_ft)} live followthrough)')
