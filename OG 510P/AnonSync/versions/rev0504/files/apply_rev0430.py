from pathlib import Path

REQUIRED = [
    'docs/1720-resilio-consumer-uptake-decision-pinning-and-rollback-blast-radius-fragmentation-evaluation.md',
    'docs/1721-consumer-uptake-contract-sheet-page-current-sentence-pins-decision-use-and-rollback-blast-radius-interface-spec.md',
    'docs/1722-consumer-uptake-review-page-who-has-actually-used-this-current-sentence-and-how-hard-is-rollback-interface-spec.md',
    'docs/1723-consumer-uptake-proof-page-which-consumers-pinned-relied-on-or-acted-on-this-sentence-version-interface-spec.md',
    'docs/1724-consumer-uptake-timeline-page-fetch-pin-decide-act-and-rollback-reach-events-interface-spec.md',
    'docs/1725-consumer-uptake-lineage-receipt-page-decision-basis-version-consumer-use-and-rollback-blast-radius-interface-spec.md',
]

if __name__ == '__main__':
    missing = [pp for pp in REQUIRED if not Path(pp).exists()]
    if missing:
        raise SystemExit('Missing required rev0430 files:\n' + '\n'.join(missing))
    print('rev0430 presence check passed')
