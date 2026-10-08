from pathlib import Path

REQUIRED = [
    'docs/1702-resilio-stability-window-regression-and-reopen-fragmentation-evaluation.md',
    'docs/1703-stability-window-contract-sheet-page-freshly-attained-observation-and-stable-promotion-interface-spec.md',
    'docs/1704-stability-review-page-did-the-effect-stick-long-enough-for-the-stronger-sentence-interface-spec.md',
    'docs/1705-stability-proof-page-observation-window-regression-events-and-earned-finality-interface-spec.md',
    'docs/1706-stability-timeline-page-attained-observed-stable-reopened-and-decayed-events-interface-spec.md',
    'docs/1707-stability-lineage-receipt-page-dwell-window-regression-basis-and-blocked-stable-sentences-interface-spec.md',
]

if __name__ == '__main__':
    missing = [p for p in REQUIRED if not Path(p).exists()]
    if missing:
        raise SystemExit('Missing required rev0427 files:\n' + '\n'.join(missing))
    print('rev0427 presence check passed')
