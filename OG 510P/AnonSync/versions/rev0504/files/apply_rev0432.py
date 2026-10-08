from pathlib import Path

REQUIRED = [
    'docs/1732-resilio-remedy-substrate-expiry-and-repair-capability-fragmentation-evaluation.md',
    'docs/1733-remedy-substrate-contract-sheet-page-repair-material-expiry-and-cure-capability-interface-spec.md',
    'docs/1734-remedy-capability-review-page-do-we-still-have-enough-substrate-to-repair-this-cleanly-interface-spec.md',
    'docs/1735-remedy-substrate-proof-page-archive-material-source-presence-and-repair-floor-interface-spec.md',
    'docs/1736-remedy-substrate-timeline-page-mutation-archive-expiry-restore-and-cure-collapse-events-interface-spec.md',
    'docs/1737-remedy-substrate-lineage-receipt-page-cure-capability-repair-material-and-blocked-clean-repair-sentences-interface-spec.md',
]

if __name__ == '__main__':
    missing = [pp for pp in REQUIRED if not Path(pp).exists()]
    if missing:
        raise SystemExit('Missing required rev0432 files:\n' + '\n'.join(missing))
    print('rev0432 presence check passed')
