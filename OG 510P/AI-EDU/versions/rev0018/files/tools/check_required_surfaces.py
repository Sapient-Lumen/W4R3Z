from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
required = [
    'README.md',
    'START_HERE.md',
    'AGENTS.md',
    'CHANGELOG.md',
    'ARCHIVE_INDEX.md',
    'REVISION_RECEIPT.json',
    'RELEASE-MANIFEST.json',
    'ASSUMPTION_LEDGER.json',
    'FOLLOWTHROUGH_QUEUE.json',
    'FOREIGN_PRESSURE_LEDGER.json',
    'docs/00-meta/charter.md',
    'docs/00-meta/llm-runbook.md',
    'docs/00-meta/trajectory-map.md',
    'docs/00-meta/bibliography.md',
    'docs/10-core/design-principles.md',
    'docs/10-core/minimal-ai-literacy-spine.md',
    'docs/10-core/reference-model.md',
    'docs/20-governance/evidence-and-procurement.md',
    'docs/20-governance/accommodation-aware-disclosure-and-accessibility.md',
    'docs/20-governance/open-question-registry.md',
    'docs/30-operations/phased-adoption-roadmap.md',
    'docs/30-operations/subject-embedded-exemplar-kernel.md',
    'docs/30-operations/course-level-ai-use-grammar.md',
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
    'docs/40-assessment/authentic-assessment-and-proof-of-learning.md',
    'docs/40-assessment/proof-of-learning-bundles.md',
    'docs/90-quarantine/speculations-2026-03-22.md',
]
missing = [p for p in required if not (ROOT / p).exists()]
if missing:
    raise SystemExit('missing required surfaces: ' + ', '.join(missing))
print('check_required_surfaces: OK')
