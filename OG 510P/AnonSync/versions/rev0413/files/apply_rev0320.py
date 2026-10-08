#!/usr/bin/env python3
"""Archive helper for rev0320.

This revision adds the directory-admission tranche:
- 1060 Resilio evaluation
- 1061 directory admission contract sheet
- 1062 root-ceiling review
- 1063 picker visibility authority page
- 1064 config-authored subject-set review
- 1065 directory-admission lineage receipt

The source archive already contains the applied results; this helper exists to make the
revision boundary explicit in the package history.
"""

from pathlib import Path

DOCS = [
    '1060-resilio-directory-admission-root-ceiling-whitelist-and-config-authorship-fragmentation-evaluation.md',
    '1061-directory-admission-contract-sheet-page-path-admissibility-root-ceiling-and-authorship-basis-interface-spec.md',
    '1062-root-ceiling-review-page-directory-root-policy-descendant-only-creation-and-direct-root-denial-interface-spec.md',
    '1063-picker-visibility-authority-page-allowlisted-browse-surfaces-hidden-paths-and-direct-entry-boundary-interface-spec.md',
    '1064-config-authored-subject-set-review-page-standard-only-folders-webui-suppression-and-roster-replacement-interface-spec.md',
    '1065-directory-admission-lineage-receipt-page-requested-path-verdict-blocking-authority-and-roster-authorship-delta-interface-spec.md',
]

if __name__ == '__main__':
    docs_root = Path(__file__).resolve().parent / 'docs'
    missing = [name for name in DOCS if not (docs_root / name).exists()]
    if missing:
        raise SystemExit('missing rev0320 docs: ' + ', '.join(missing))
    print('rev0320 tranche present: directory-admission family')
