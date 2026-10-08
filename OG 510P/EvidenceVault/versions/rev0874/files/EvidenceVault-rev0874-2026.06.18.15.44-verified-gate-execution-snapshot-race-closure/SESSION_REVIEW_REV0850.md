# Session review — rev0850

- Created: `2026-06-13T16:47:00Z`
- Role: overlay/patch refactor bundle, not a canonical signed release
- Derived from: `EvidenceVault-rev0849-2026.06.13.14.21-authorized-snapshot-html-rights-hardening.zip`

## Risk focus

- Make the overlay series executable as a continuous chain from the rev0840 handoff instead of relying on manual patch choreography.
- Reject publication-rights readiness evidence that is read through symlinked or non-regular rights-critical files.
- Keep the overlay artifact self-check honest by requiring a seed handoff patch and a continuous patch chain through the current revision.

## Substantive changes

- Added `PATCHES/rev0840-to-rev0841-overlay.patch`, recovered by diffing the archived rev0840 and rev0841 overlay bundles while excluding self-referential packaging surfaces.
- Added `scripts/apply_overlay_stack_rev0850.py`, which validates overlay patch names and payload paths, rejects binary/path-traversing patches, refuses symlinked target trees, performs a temporary-copy dry run, and only then optionally applies to the target tree.
- Hardened `scripts/publication_rights_gate.py` so `RIGHTS/component_license_ledger.json` and root `LICENSE`, `COPYING`, or `NOTICE` sentinels must be archive-local regular files without symlinked components.
- Updated `scripts/validate_overlay_bundle_integrity_rev0848.py` so the self-integrity check now requires the recovered rev0840-to-rev0841 seed patch and a continuous one-step overlay chain through rev0850.

## New evidence

- `AUDIT/OVERLAY_STACK_APPLICATION_HARNESS_REV0850.*`
- `AUDIT/PUBLICATION_RIGHTS_GATE_LEDGER_ROOT_RIGHTS_BOUNDARY_REV0850.*`
- `scripts/validate_overlay_stack_application_harness_rev0850.py`
- `scripts/validate_publication_rights_gate_ledger_root_rights_boundary_rev0850.py`
- `VALIDATION/rev0850_targeted_validation.txt`

## Deliberately unchanged

Publication remains blocked. This revision does not invent root `LICENSE`, `COPYING`, `NOTICE`, component license conclusions, SPDX rights assertions, or RO-Crate rights metadata.

The rev0840 canonical patch streams remain unchanged.
