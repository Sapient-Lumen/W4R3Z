import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REENTRY_DOCS = {
    'README.md': 10,
    'START_HERE.md': 8,
    'AGENTS.md': 7,
    'docs/00-meta/reentry-navigation-map.md': 10,
    'docs/00-meta/surface-map-overview.md': 8,
}
RECEIPT = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
CURRENT_REV = RECEIPT['revision']
CURRENT_REQUIRED = [
    f'docs/00-meta/mission-kernel-{CURRENT_REV}.md',
    f'docs/00-meta/cube-deep-audit-{CURRENT_REV}.md',
    f'docs/00-meta/field-execution-risk-burndown-{CURRENT_REV}.md',
]
MAX_CONTEXT_PACK_BYTES = 150_000

STALE_OPERATOR_PATH = 'scratch/pedagogy/teacher-tutor-micro-pilot'
ACTIVE_OPERATOR_PATH_SURFACES = [
    'README.md',
    'START_HERE.md',
    'AGENTS.md',
    'docs/00-meta/reentry-navigation-map.md',
    'docs/30-operations/field-handoff-bundle.md',
    'docs/30-operations/teacher-tutor-augmentation-micro-pilot.md',
    'docs/30-operations/teacher-tutor-micro-pilot-run-card.md',
    'docs/30-operations/teacher-tutor-micro-pilot-readiness-gate.md',
    'docs/30-operations/teacher-tutor-micro-pilot-next-action-router.md',
    'docs/30-operations/teacher-tutor-micro-pilot-owner-review-stop.md',
    'docs/30-operations/teacher-tutor-micro-pilot-result-recorder.md',
    'tools/prepare_teacher_tutor_micro_pilot_pack.py',
    'tools/score_teacher_tutor_micro_pilot_readiness.py',
    'tools/decide_teacher_tutor_micro_pilot_next_action.py',
    'tools/prepare_field_handoff_bundle.py',
]
EXPECTED_OPERATOR_ROOT = f'scratch/field-handoff/{CURRENT_REV}/teacher-tutor-micro-pilot'
LOCAL_LINK = re.compile(r'\[[^\]]+\]\(([^)]+)\)')
errors = []

for rel, max_links in REENTRY_DOCS.items():
    path = ROOT / rel
    if not path.exists():
        errors.append(f'{rel}: missing re-entry document')
        continue
    text = path.read_text(encoding='utf-8')
    links = []
    for raw in LOCAL_LINK.findall(text):
        if raw.startswith(('http://', 'https://', 'mailto:')):
            continue
        links.append(raw.split('#', 1)[0])
    dupes = sorted(k for k, v in Counter(links).items() if v > 1 and k)
    if dupes:
        errors.append(f'{rel}: duplicate local link targets: ' + ', '.join(dupes))
    if len(links) > max_links:
        errors.append(f'{rel}: {len(links)} local links exceeds limit {max_links}; delegate to reentry-navigation-map.md or SURFACES.json')
    if rel in {'README.md', 'START_HERE.md', 'AGENTS.md'}:
        lowered = text.lower()
        for phrase in ['ft-0181', 'src2+', 'real pilot']:
            if phrase not in lowered:
                errors.append(f'{rel}: missing gate phrase {phrase!r}')
        if '--mode ' in text:
            errors.append(f'{rel}: obsolete run_lint_suite.py --mode command found; use --lane')
        for phrase in ['make owner-field-work', 'make owner-field-report', 'make owner-field-next csv=']:
            if phrase not in lowered:
                errors.append(f'{rel}: missing router-first field command {phrase!r}')


for rel in {'README.md', 'START_HERE.md', 'AGENTS.md', 'docs/00-meta/reentry-navigation-map.md'}:
    text = (ROOT / rel).read_text(encoding='utf-8')
    if CURRENT_REV not in text:
        errors.append(f'{rel}: missing current revision {CURRENT_REV}')
for required in CURRENT_REQUIRED:
    if required not in (ROOT / 'docs/00-meta/reentry-navigation-map.md').read_text(encoding='utf-8'):
        errors.append(f'reentry-navigation-map.md: missing current surface {required}')

for rel in ACTIVE_OPERATOR_PATH_SURFACES:
    path = ROOT / rel
    if not path.exists():
        errors.append(f'{rel}: active operator-path surface missing')
        continue
    text = path.read_text(encoding='utf-8')
    if STALE_OPERATOR_PATH in text:
        errors.append(f'{rel}: obsolete operator path {STALE_OPERATOR_PATH!r} found')

for rel in [
    'README.md',
    'START_HERE.md',
    'docs/30-operations/field-handoff-bundle.md',
    'tools/prepare_teacher_tutor_micro_pilot_pack.py',
    'tools/score_teacher_tutor_micro_pilot_readiness.py',
]:
    text = (ROOT / rel).read_text(encoding='utf-8')
    if EXPECTED_OPERATOR_ROOT not in text and "'scratch' / 'field-handoff'" not in text:
        errors.append(f'{rel}: missing revision-scoped operator root {EXPECTED_OPERATOR_ROOT}')

ctx_path = ROOT / 'context-pack.json'
if ctx_path.exists():
    ctx_size = ctx_path.stat().st_size
    if ctx_size > MAX_CONTEXT_PACK_BYTES:
        errors.append(
            f'context-pack.json: {ctx_size} bytes exceeds compact limit {MAX_CONTEXT_PACK_BYTES}; '
            'carry IDs/counts and use ledger_sources for expansion'
        )
    data = json.loads(ctx_path.read_text(encoding='utf-8'))
    startup = data.get('startup_path', [])
    if not isinstance(startup, list) or not startup:
        errors.append('context-pack.json: startup_path must be a non-empty list')
    else:
        if len(startup) > 12:
            errors.append(f'context-pack.json: startup_path length {len(startup)} exceeds compact limit 12')
        dupes = sorted(k for k, v in Counter(startup).items() if v > 1)
        if dupes:
            errors.append('context-pack.json: duplicate startup_path entries: ' + ', '.join(dupes))
        for rel in startup:
            if not (ROOT / rel).exists():
                errors.append(f'context-pack.json: startup_path missing file {rel}')
    policy = data.get('startup_path_policy', '').lower()
    if 'compact' not in policy or 'reentry-navigation-map' not in policy:
        errors.append('context-pack.json: startup_path_policy must explain compact navigation via reentry-navigation-map')

    live_assumptions = data.get('live_assumptions', [])
    if not isinstance(live_assumptions, list):
        errors.append('context-pack.json: live_assumptions must be a compact list of assumption IDs')
    elif any(isinstance(item, dict) for item in live_assumptions):
        errors.append('context-pack.json: live_assumptions must not embed full assumption objects')
    elif any(not isinstance(item, str) or not re.match(r'^AS-\d{4}$', item) for item in live_assumptions):
        errors.append('context-pack.json: live_assumptions must contain AS-#### strings')

    live_followthrough = data.get('live_followthrough', [])
    if not isinstance(live_followthrough, list):
        errors.append('context-pack.json: live_followthrough must be a list')
    else:
        for idx, item in enumerate(live_followthrough):
            if not isinstance(item, dict):
                errors.append(f'context-pack.json: live_followthrough[{idx}] must be a compact followthrough object')
                continue
            if item.get('state') == 'done':
                errors.append(f'context-pack.json: live_followthrough[{idx}] embeds done item {item.get("id", "<missing>")}')
            if not re.match(r'^FT-\d{4}$', str(item.get('id', ''))):
                errors.append(f'context-pack.json: live_followthrough[{idx}] missing FT-#### id')
            if 'why_live' in item:
                errors.append(f'context-pack.json: live_followthrough[{idx}] embeds why_live history; use current_blocker/current_action')
            if len(json.dumps(item)) > 1400:
                errors.append(f'context-pack.json: live_followthrough[{idx}] exceeds compact row limit')

    counts = data.get('ledger_counts', {})
    if not isinstance(counts, dict) or 'followthrough_done' not in counts:
        errors.append('context-pack.json: ledger_counts must summarize omitted done followthrough records')
    else:
        state_counts = counts.get('assumption_states', {})
        if not isinstance(state_counts, dict) or 'active' not in state_counts:
            errors.append('context-pack.json: ledger_counts.assumption_states must summarize assumption triage states')
        if counts.get('active_assumption_ids') != len(live_assumptions):
            errors.append('context-pack.json: ledger_counts.active_assumption_ids must match live_assumptions length')
        if len(live_assumptions) > 90:
            errors.append('context-pack.json: live_assumptions exceeds decision-bearing cap of 90 IDs; triage the ledger instead of re-growing startup')
    sources = data.get('ledger_sources', {})
    if sources.get('full_assumption_ledger') != 'ASSUMPTION_LEDGER.json':
        errors.append('context-pack.json: ledger_sources.full_assumption_ledger must point to ASSUMPTION_LEDGER.json')
    if sources.get('full_followthrough_queue') != 'FOLLOWTHROUGH_QUEUE.json':
        errors.append('context-pack.json: ledger_sources.full_followthrough_queue must point to FOLLOWTHROUGH_QUEUE.json')
else:
    errors.append('context-pack.json missing')

if errors:
    raise SystemExit('re-entry navigation validation errors:\n' + '\n'.join(errors))
print(f'check_reentry_navigation: OK ({len(REENTRY_DOCS)} docs)')
