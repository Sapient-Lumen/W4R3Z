#!/usr/bin/env python3
"""Archive helper for rev0323.

This revision adds the host-integration/trust/shell-clearance tranche:
- 1078 Resilio evaluation
- 1079 host integration contract sheet
- 1080 installer trust review
- 1081 shell-surface activation proof
- 1082 uninstall clearance review
- 1083 host-integration lineage receipt

The source archive already contains the applied results; this helper exists to make the
revision boundary explicit in the package history.
"""

from pathlib import Path

DOCS = [
    '1078-resilio-host-integration-signer-trust-shell-activation-and-uninstall-clearance-fragmentation-evaluation.md',
    '1079-host-integration-contract-sheet-page-installer-trust-os-consent-shell-surfaces-and-clearance-state-interface-spec.md',
    '1080-installer-trust-review-page-codesign-reputation-uac-consent-and-host-mutation-scope-interface-spec.md',
    '1081-shell-surface-activation-proof-page-finder-explorer-extension-state-filesystem-eligibility-and-registration-truth-interface-spec.md',
    '1082-uninstall-clearance-review-page-program-removal-settings-residue-shell-release-and-shared-data-survivor-interface-spec.md',
    '1083-host-integration-lineage-receipt-page-trust-prompts-shell-surface-state-and-clearance-ceiling-interface-spec.md',
]

if __name__ == '__main__':
    docs_root = Path(__file__).resolve().parent / 'docs'
    missing = [name for name in DOCS if not (docs_root / name).exists()]
    if missing:
        raise SystemExit('missing rev0323 docs: ' + ', '.join(missing))
    print('rev0323 tranche present: host-integration/trust/shell-clearance family')
