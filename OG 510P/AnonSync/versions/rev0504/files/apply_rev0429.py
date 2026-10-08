from pathlib import Path

REQUIRED = [
    'docs/1714-resilio-current-sentence-commitment-rollout-and-rollback-fragmentation-evaluation.md',
    'docs/1715-current-sentence-contract-sheet-page-authorized-committed-current-and-rollback-scope-interface-spec.md',
    'docs/1716-current-sentence-review-page-is-the-stronger-sentence-actually-live-for-decision-consumers-now-interface-spec.md',
    'docs/1717-current-sentence-proof-page-why-the-stronger-sentence-is-or-is-not-current-and-operative-interface-spec.md',
    'docs/1718-current-sentence-timeline-page-promotion-commit-publish-rollout-and-rollback-events-interface-spec.md',
    'docs/1719-current-sentence-lineage-receipt-page-committed-sentence-consumer-scope-and-rollback-exposure-interface-spec.md',
]

if __name__ == '__main__':
    missing = [pp for pp in REQUIRED if not Path(pp).exists()]
    if missing:
        raise SystemExit('Missing required rev0429 files:\n' + '\n'.join(missing))
    print('rev0429 presence check passed')
