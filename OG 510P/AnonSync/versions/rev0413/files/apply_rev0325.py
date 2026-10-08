#!/usr/bin/env python3
"""Archive helper for rev0325.

This revision adds the self-edge/local-derivation tranche:
- 1090 Resilio evaluation
- 1091 self-edge derivation contract sheet
- 1092 self-edge topology review
- 1093 derived-rights and lifecycle review
- 1094 self-edge materialization and entitlement watch
- 1095 self-edge lineage receipt

The source archive already contains the applied results; this helper exists to make the
revision boundary explicit in the package history.
"""

from pathlib import Path

DOCS = [
    '1090-resilio-self-edge-local-derivation-loop-rights-and-license-cliff-evaluation.md',
    '1091-self-edge-derivation-contract-sheet-page-source-self-peer-loop-ceiling-and-lifecycle-coupling-interface-spec.md',
    '1092-self-edge-topology-review-page-parent-child-loop-ban-and-fanout-boundary-interface-spec.md',
    '1093-derived-rights-and-lifecycle-review-page-owner-ceiling-source-downgrade-and-reattach-requirement-interface-spec.md',
    '1094-self-edge-materialization-and-entitlement-watch-page-placeholder-dependence-discovery-bypass-and-license-cliff-interface-spec.md',
    '1095-self-edge-lineage-receipt-page-source-target-self-peer-and-suspension-boundary-interface-spec.md',
]

if __name__ == '__main__':
    docs_root = Path(__file__).resolve().parent / 'docs'
    missing = [name for name in DOCS if not (docs_root / name).exists()]
    if missing:
        raise SystemExit('missing rev0325 docs: ' + ', '.join(missing))
    print('rev0325 tranche present: self-edge/local-derivation family')
