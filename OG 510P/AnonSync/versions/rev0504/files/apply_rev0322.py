#!/usr/bin/env python3
"""Archive helper for rev0322.

This revision adds the ingress-mutation/port-lease tranche:
- 1072 Resilio evaluation
- 1073 ingress exposure contract sheet
- 1074 port-mapping review
- 1075 router side-effect warning
- 1076 directness proof
- 1077 ingress lineage receipt

The source archive already contains the applied results; this helper exists to make the
revision boundary explicit in the package history.
"""

from pathlib import Path

DOCS = [
    '1072-resilio-automatic-ingress-mutation-port-lease-and-router-side-effect-fragmentation-evaluation.md',
    '1073-ingress-exposure-contract-sheet-page-listening-port-map-authority-and-lease-truth-interface-spec.md',
    '1074-port-mapping-review-page-random-vs-fixed-port-upnp-lease-and-manual-forward-mismatch-interface-spec.md',
    '1075-router-side-effect-warning-page-upnp-nat-pmp-device-fragility-and-rollback-boundary-interface-spec.md',
    '1076-directness-proof-page-open-listener-mapped-ingress-and-relay-fallback-ceiling-interface-spec.md',
    '1077-ingress-lineage-receipt-page-listener-continuity-mutation-attempt-and-blocked-stronger-sentences-interface-spec.md',
]

if __name__ == '__main__':
    docs_root = Path(__file__).resolve().parent / 'docs'
    missing = [name for name in DOCS if not (docs_root / name).exists()]
    if missing:
        raise SystemExit('missing rev0322 docs: ' + ', '.join(missing))
    print('rev0322 tranche present: ingress-mutation/port-lease family')
