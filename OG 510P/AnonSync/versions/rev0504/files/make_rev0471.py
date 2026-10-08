from pathlib import Path

root = Path('/mnt/data/work_rev0470')
docs = root / 'docs'

expected = [
    '1966-resilio-remedy-hardening-attestation-postcondition-realization-effectuation-and-settlement-fragmentation-evaluation.md',
    '1967-remedy-hardening-attestation-postcondition-realization-contract-sheet-page-target-state-observation-quorum-and-settlement-window-interface-spec.md',
    '1968-remedy-hardening-attestation-postcondition-realization-review-page-did-the-mandate-actually-make-the-intended-state-true-here-interface-spec.md',
    '1969-remedy-hardening-attestation-postcondition-realization-proof-page-outcome-witnesses-slice-coverage-and-rollback-ceiling-interface-spec.md',
    '1970-remedy-hardening-attestation-postcondition-realization-timeline-page-route-observe-settle-rollback-and-reconfirm-events-interface-spec.md',
    '1971-remedy-hardening-attestation-postcondition-realization-lineage-receipt-page-target-state-settlement-window-and-blocked-stronger-sentences-interface-spec.md',
]

for name in expected:
    if not (docs / name).exists():
        raise SystemExit(f'missing expected document: {name}')

for rel in ['README.md', 'docs/00-status.md', 'docs/10-resilio-sync-evaluation.md', 'docs/sources.md']:
    if not (root / rel).exists():
        raise SystemExit(f'missing expected file: {rel}')

print('rev0471 tranche present')
