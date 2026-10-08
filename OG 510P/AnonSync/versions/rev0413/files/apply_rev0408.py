from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / 'docs'

NEW_FILES = [
    '1588-resilio-promise-capacity-concurrency-and-overcommitment-fragmentation-evaluation.md',
    '1589-commitment-capacity-contract-sheet-page-issuer-budget-concurrent-promises-and-reserve-headroom-interface-spec.md',
    '1590-promise-load-review-page-admit-defer-throttle-and-capacity-reservation-routes-interface-spec.md',
    '1591-commitment-capacity-proof-page-load-envelope-headroom-and-overcommitment-guard-interface-spec.md',
    '1592-promise-capacity-timeline-page-budget-consumed-restored-throttled-and-overcommit-events-interface-spec.md',
    '1593-commitment-capacity-lineage-receipt-page-load-basis-headroom-class-and-blocked-stronger-sentences-interface-spec.md',
]

UPDATED_FILES = [
    'README.md',
    'docs/00-status.md',
    'docs/10-resilio-sync-evaluation.md',
    'docs/11-resilio-borrow-line-and-non-clone-scorecard.md',
    'docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md',
    'docs/20-product-direction.md',
    'docs/sources.md',
]

if __name__ == '__main__':
    print('rev0408 adds:')
    for f in NEW_FILES:
        print(' -', f)
    print('rev0408 updates:')
    for f in UPDATED_FILES:
        print(' -', f)
