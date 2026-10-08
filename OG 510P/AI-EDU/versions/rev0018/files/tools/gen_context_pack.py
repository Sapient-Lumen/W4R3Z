import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))
assumptions = json.loads((ROOT / 'ASSUMPTION_LEDGER.json').read_text(encoding='utf-8'))['items']
followthrough = json.loads((ROOT / 'FOLLOWTHROUGH_QUEUE.json').read_text(encoding='utf-8'))['items']

payload = {
    'project': 'AI-EDU',
    'revision': receipt['revision'],
    'startup_path': [
        'START_HERE.md',
        'AGENTS.md',
        'docs/10-core/minimal-ai-literacy-spine.md',
        'docs/10-core/reference-model.md',
        'docs/30-operations/subject-embedded-exemplar-kernel.md',
        'docs/30-operations/course-level-ai-use-grammar.md',
        'docs/20-governance/accommodation-aware-disclosure-and-accessibility.md',
        'docs/30-operations/lifelong-public-ai-learning-stack.md',
        'docs/30-operations/minimum-public-entitlement-and-handoff-standard.md',
        'docs/30-operations/portable-public-learning-packet-and-recognition-profile.md',
        'docs/30-operations/sector-defaults-for-public-ai-learning-recognition.md',
        'docs/30-operations/standing-equivalency-lists-and-review-governance.md',
        'docs/30-operations/standing-list-publication-profile-and-recency-windows.md',
        'docs/30-operations/standing-recognition-exception-profile-and-local-overrides.md',
        'docs/30-operations/appeal-feedback-and-standing-list-maintenance.md',
        'docs/30-operations/public-maintenance-history-and-trust-signals.md',
        'docs/30-operations/partner-consumption-and-grandfathering-rules.md',
        'docs/30-operations/in-flight-teach-out-and-substitute-equivalent-rules.md',
        'docs/30-operations/documented-reliance-and-burden-thresholds.md',
        'docs/20-governance/evidence-and-procurement.md',
        'docs/40-assessment/authentic-assessment-and-proof-of-learning.md'
    ],
    'current_summary': receipt['summary'],
    'live_assumptions': assumptions,
    'live_followthrough': followthrough,
    'open_questions': [
        'OQ-0001', 'OQ-0002', 'OQ-0003', 'OQ-0004', 'OQ-0005', 'OQ-0006', 'OQ-0008'
    ],
}
(ROOT / 'context-pack.json').write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
print('gen_context_pack: OK')
