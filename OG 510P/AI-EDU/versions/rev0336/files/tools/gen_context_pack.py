import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
assumptions = json.loads((ROOT / 'ASSUMPTION_LEDGER.json').read_text(encoding='utf-8'))['items']
followthrough = json.loads((ROOT / 'FOLLOWTHROUGH_QUEUE.json').read_text(encoding='utf-8'))['items']

def preferred_or_latest(preferred: str, glob_pattern: str) -> str:
    if (ROOT / preferred).exists():
        return preferred
    candidates = sorted((ROOT / 'docs' / '00-meta').glob(glob_pattern))
    if not candidates:
        return preferred
    return candidates[-1].relative_to(ROOT).as_posix()


current_deep_audit = f"docs/00-meta/cube-deep-audit-{receipt['revision']}.md"
current_mission_kernel = f"docs/00-meta/mission-kernel-{receipt['revision']}.md"
current_risk_burndown = f"docs/00-meta/field-execution-risk-burndown-{receipt['revision']}.md"
current_execution_refactor = f"docs/00-meta/pedagogy-forward-execution-refactor-{receipt['revision']}.md"
current_hot_path_burden_audit = f"docs/00-meta/field-handoff-bundle-audit-{receipt['revision']}.md"
current_reask_log_audit = 'docs/00-meta/owner-reask-log-gate-audit-rev0282.md'
current_route_block_audit = 'docs/00-meta/owner-route-block-audit-rev0281.md'
current_contact_clock_audit = 'docs/00-meta/live-window-card-gate-audit-rev0281.md'

startup_path = [
    'START_HERE.md',
    'README.md',
    'AGENTS.md',
    'docs/00-meta/reentry-navigation-map.md',
    current_mission_kernel,
    current_deep_audit,
    current_risk_burndown,
    'docs/30-operations/field-handoff-bundle.md',
    'docs/30-operations/ft0181-owner-contact-send-pack.md',
    'docs/30-operations/teacher-tutor-micro-pilot-run-card.md',
    'docs/30-operations/teacher-tutor-micro-pilot-next-action-router.md',
    'docs/30-operations/teacher-tutor-micro-pilot-result-recorder.md',
]

extended_indexes = [
    'ARCHIVE_INDEX.md',
    'SURFACES.json',
    'BRANCH_FAMILY_INDEX.json',
    'CUBE_TOOLCHAIN_REGISTRY.json',
    'CUBE_SCHEMA_REGISTRY.json',
    'CUBE_SURFACE_CONTRACTS.json',
    'docs/00-meta/bibliography.md',
    'docs/10-core/design-principles.md',
    'docs/10-core/reference-model.md',
    'ASSUMPTION_LEDGER.json',
    'FOLLOWTHROUGH_QUEUE.json',
    'REVISION_RECEIPT.json',
    'CHANGELOG.md',
]

active_assumption_ids = sorted(
    item['id'] for item in assumptions
    if item.get('state', 'active') == 'active'
)
def compact_followthrough(item):
    return {
        'id': item['id'],
        'state': item.get('state'),
        'objective': item.get('objective'),
        'next_surface': item.get('next_surface'),
        'current_blocker': item.get('current_blocker'),
        'current_action': item.get('current_action'),
    }

live_followthrough = [compact_followthrough(item) for item in followthrough if item.get('state') != 'done']
state_counts = Counter(item.get('state', 'active') for item in assumptions)

payload = {
    'project': 'AI-EDU',
    'revision': receipt['revision'],
    'startup_path': startup_path,
    'extended_indexes': extended_indexes,
    'startup_path_policy': 'Compact re-entry path only; carry IDs, counts, and the current execution cards plus the field-handoff bundle, next-action, owner-review, and result-recorder utilities here, then use reentry-navigation-map.md, BRANCH_FAMILY_INDEX.json, SURFACES.json, CUBE_SCHEMA_REGISTRY.json, CUBE_SURFACE_CONTRACTS.json, FOLLOWTHROUGH_QUEUE.json, and ARCHIVE_INDEX.md for expansion rather than embedding branch-history tails, full ledgers, or done followthrough records.',
    'current_summary': receipt['summary'],
    'live_assumptions': active_assumption_ids,
    'live_followthrough': live_followthrough,
    'ledger_counts': {
        'assumptions_total': len(assumptions),
        'active_assumption_ids': len(active_assumption_ids),
        'assumption_states': dict(sorted(state_counts.items())),
        'followthrough_total': len(followthrough),
        'followthrough_live': len(live_followthrough),
        'followthrough_done': sum(1 for item in followthrough if item.get('state') == 'done'),
    },
    'ledger_sources': {
        'full_assumption_ledger': 'ASSUMPTION_LEDGER.json',
        'full_followthrough_queue': 'FOLLOWTHROUGH_QUEUE.json',
    },
    'open_questions': re.findall(
        r'^## (OQ-\d{4})',
        (ROOT / 'docs/20-governance/open-question-registry.md').read_text(encoding='utf-8'),
        flags=re.MULTILINE,
    ),
}
(ROOT / 'context-pack.json').write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
print('gen_context_pack: OK')
