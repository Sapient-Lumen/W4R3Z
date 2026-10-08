from pathlib import Path

REQUIRED = [
    'docs/1708-resilio-promotion-gate-override-and-auto-promotion-fragmentation-evaluation.md',
    'docs/1709-promotion-gate-contract-sheet-page-eligibility-manual-only-and-auto-promotion-interface-spec.md',
    'docs/1710-promotion-review-page-may-the-product-promote-to-the-stronger-sentence-now-interface-spec.md',
    'docs/1711-promotion-proof-page-why-the-stronger-sentence-was-or-was-not-authorized-interface-spec.md',
    'docs/1712-promotion-timeline-page-eligibility-review-promotion-override-and-demotion-events-interface-spec.md',
    'docs/1713-promotion-lineage-receipt-page-gate-basis-override-authority-and-blocked-stronger-sentences-interface-spec.md',
]

if __name__ == '__main__':
    missing = [pp for pp in REQUIRED if not Path(pp).exists()]
    if missing:
        raise SystemExit('Missing required rev0428 files:\n' + '\n'.join(missing))
    print('rev0428 presence check passed')
