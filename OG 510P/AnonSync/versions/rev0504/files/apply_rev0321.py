#!/usr/bin/env python3
"""Archive helper for rev0321.

This revision adds the same-host multi-instance tranche:
- 1066 Resilio evaluation
- 1067 instance namespace contract sheet
- 1068 second-instance bringup review
- 1069 same-path claim-collision warning
- 1070 shared external-storage review
- 1071 instance lineage receipt

The source archive already contains the applied results; this helper exists to make the
revision boundary explicit in the package history.
"""

from pathlib import Path

DOCS = [
    '1066-resilio-same-host-multi-instance-port-namespace-storage-world-and-claim-collision-evaluation.md',
    '1067-instance-namespace-contract-sheet-page-runtime-identity-listener-storage-and-claim-ceiling-interface-spec.md',
    '1068-second-instance-bringup-review-page-port-separation-storage-root-identity-and-ui-audience-interface-spec.md',
    '1069-same-path-claim-collision-warning-page-hidden-state-corruption-and-branch-vs-reattach-interface-spec.md',
    '1070-shared-external-storage-review-page-removable-world-reuse-and-safe-ownership-handoff-interface-spec.md',
    '1071-instance-lineage-receipt-page-runtime-namespace-storage-root-subject-ownership-and-blocked-stronger-sentences-interface-spec.md',
]

if __name__ == '__main__':
    docs_root = Path(__file__).resolve().parent / 'docs'
    missing = [name for name in DOCS if not (docs_root / name).exists()]
    if missing:
        raise SystemExit('missing rev0321 docs: ' + ', '.join(missing))
    print('rev0321 tranche present: same-host multi-instance family')
