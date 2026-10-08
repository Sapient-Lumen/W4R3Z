from pathlib import Path

REQUIRED = [
    'docs/1726-resilio-downstream-materialization-compensation-and-unwind-fragmentation-evaluation.md',
    'docs/1727-downstream-consequence-contract-sheet-page-decision-use-world-mutation-and-compensation-debt-interface-spec.md',
    'docs/1728-downstream-consequence-review-page-what-this-sentence-version-already-changed-and-what-unwind-remains-interface-spec.md',
    'docs/1729-downstream-consequence-proof-page-which-world-mutations-fired-and-what-can-still-be-compensated-interface-spec.md',
    'docs/1730-downstream-consequence-timeline-page-decide-emit-mutate-compensate-and-residue-events-interface-spec.md',
    'docs/1731-downstream-consequence-lineage-receipt-page-world-change-compensation-posture-and-blocked-stronger-reversal-sentences-interface-spec.md',
]

if __name__ == '__main__':
    missing = [pp for pp in REQUIRED if not Path(pp).exists()]
    if missing:
        raise SystemExit('Missing required rev0431 files:\n' + '\n'.join(missing))
    print('rev0431 presence check passed')
