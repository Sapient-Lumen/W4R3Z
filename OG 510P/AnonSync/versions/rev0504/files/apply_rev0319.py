#!/usr/bin/env python3
"""Archive helper for rev0319.

This revision adds the pre-login/headless-runtime tranche:
- 1054 Resilio evaluation
- 1055 pre-login runtime contract sheet
- 1056 headless launch review
- 1057 group-write discipline proof
- 1058 pre-login mode caveat page
- 1059 pre-login lineage receipt

The source archive already contains the applied results; this helper exists to make the
revision boundary explicit in the package history.
"""

from pathlib import Path

DOCS = [
    '1054-resilio-prelogin-launchd-principal-groupwrite-and-headless-webui-fragmentation-evaluation.md',
    '1055-prelogin-runtime-contract-sheet-page-session-boundary-launch-class-and-principal-world-interface-spec.md',
    '1056-headless-launch-review-page-launchd-user-storage-home-webui-audience-and-delay-interface-spec.md',
    '1057-group-write-discipline-proof-page-umask-delivery-ownership-and-sync-stop-risk-interface-spec.md',
    '1058-prelogin-mode-caveat-page-placeholders-link-handoff-and-session-losses-interface-spec.md',
    '1059-prelogin-lineage-receipt-page-launch-class-principal-webui-exposure-and-posix-contract-interface-spec.md',
]

if __name__ == '__main__':
    docs_root = Path(__file__).resolve().parent / 'docs'
    missing = [name for name in DOCS if not (docs_root / name).exists()]
    if missing:
        raise SystemExit('missing rev0319 docs: ' + ', '.join(missing))
    print('rev0319 tranche present: pre-login/headless-runtime family')
