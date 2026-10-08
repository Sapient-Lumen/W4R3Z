from pathlib import Path

ROOT = Path(__file__).resolve().parent

NEW_DOCS = [
    'docs/1348-resilio-governance-plane-ui-poweruser-config-and-service-override-fragmentation-evaluation.md',
    'docs/1349-governance-plane-contract-sheet-page-ui-poweruser-config-service-and-override-basis-interface-spec.md',
    'docs/1350-policy-authorship-review-page-global-default-share-override-and-manual-detach-interface-spec.md',
    'docs/1351-mutation-authority-proof-page-which-surface-can-set-see-and-override-this-value-interface-spec.md',
    'docs/1352-governance-plane-timeline-page-default-adoption-manual-override-restart-and-service-world-events-interface-spec.md',
    'docs/1353-governance-plane-lineage-receipt-page-authorship-plane-override-basis-and-blocked-stronger-sentences-interface-spec.md',
]

if __name__ == '__main__':
    for rel in NEW_DOCS:
        p = ROOT / rel
        status = 'OK' if p.exists() else 'MISSING'
        print(f'{rel}: {status}')
