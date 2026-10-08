from pathlib import Path

ROOT = Path(__file__).resolve().parent

NEW_DOCS = [
    'docs/1342-resilio-effect-direction-bidirectional-backup-and-reverse-lane-fragmentation-evaluation.md',
    'docs/1343-effect-direction-contract-sheet-page-authoring-delete-serve-and-recovery-lanes-interface-spec.md',
    'docs/1344-flow-direction-review-page-bidirectional-storage-only-backup-and-opaque-custody-interface-spec.md',
    'docs/1345-reverse-lane-proof-page-which-side-can-publish-delete-restore-and-reshare-interface-spec.md',
    'docs/1346-effect-direction-timeline-page-enable-backup-disconnect-delete-and-recovery-events-interface-spec.md',
    'docs/1347-effect-direction-lineage-receipt-page-lane-basis-reverse-effects-and-blocked-stronger-sentences-interface-spec.md',
]

if __name__ == '__main__':
    for rel in NEW_DOCS:
        p = ROOT / rel
        status = 'OK' if p.exists() else 'MISSING'
        print(f'{rel}: {status}')
