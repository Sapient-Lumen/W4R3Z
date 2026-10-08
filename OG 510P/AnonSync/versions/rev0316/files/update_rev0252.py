from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / 'docs'

ADDED = [
    '686-resilio-hydration-engine-shell-lane-and-history-ceiling-evaluation.md',
    '687-hydration-engine-posture-page-engine-kind-action-lane-and-history-guarantee-interface-spec.md',
    '688-hydration-mode-change-review-page-platform-prerequisite-history-ceiling-and-cotenant-risk-interface-spec.md',
    '689-hydration-evidence-page-engine-proof-lane-health-and-history-collision-witness-interface-spec.md',
    '690-hydration-receipt-page-engine-basis-lane-result-and-history-collision-ceiling-interface-spec.md',
]

UPDATED = [
    'README.md',
    'docs/00-status.md',
    'docs/10-resilio-sync-evaluation.md',
    'docs/11-resilio-borrow-line-and-non-clone-scorecard.md',
    'docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md',
    'docs/20-product-direction.md',
    'docs/39-interface-pattern-language.md',
    'docs/50-roadmap.md',
    'docs/64-critical-open-questions.md',
    'docs/sources.md',
]

print('rev0252 hydration-engine tranche')
print('added:')
for p in ADDED:
    print(' -', p)
print('updated:')
for p in UPDATED:
    print(' -', p)
