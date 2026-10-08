#!/usr/bin/env python3
"""Archive helper for rev0324.

This revision adds the portable-name/canonical-collision/name-plane tranche:
- 1084 Resilio evaluation
- 1085 portable-name contract sheet
- 1086 canonical-name portability review
- 1087 name-plane propagation review
- 1088 rename-scope and byte-reuse proof
- 1089 portable-name lineage receipt

The source archive already contains the applied results; this helper exists to make the
revision boundary explicit in the package history.
"""

from pathlib import Path

DOCS = [
    '1084-resilio-portable-name-collision-alias-propagation-and-move-scope-fragmentation-evaluation.md',
    '1085-portable-name-contract-sheet-page-canonical-collision-alias-planes-and-propagation-scope-interface-spec.md',
    '1086-canonical-name-portability-review-page-case-encoding-invalid-symbol-and-path-budget-interface-spec.md',
    '1087-name-plane-propagation-review-page-disk-name-ui-label-offer-alias-and-local-only-rename-interface-spec.md',
    '1088-rename-scope-and-byte-reuse-proof-page-local-path-move-archive-assisted-remote-reuse-and-symlink-boundary-interface-spec.md',
    '1089-portable-name-lineage-receipt-page-canonicalization-alias-plane-delta-and-blocked-stronger-sentences-interface-spec.md',
]

if __name__ == '__main__':
    docs_root = Path(__file__).resolve().parent / 'docs'
    missing = [name for name in DOCS if not (docs_root / name).exists()]
    if missing:
        raise SystemExit('missing rev0324 docs: ' + ', '.join(missing))
    print('rev0324 tranche present: portable-name/canonical-collision/name-plane family')

