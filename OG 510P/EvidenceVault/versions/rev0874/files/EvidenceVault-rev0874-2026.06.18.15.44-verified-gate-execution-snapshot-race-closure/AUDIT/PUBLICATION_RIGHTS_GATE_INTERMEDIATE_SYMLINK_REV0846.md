# Publication Rights Gate Intermediate Symlink Rev0846

- Status: `publication_rights_gate_intermediate_symlink_target_closure_validated`
- Revision context: `rev0846-overlay-over-rev0845-over-rev0840`
- Created UTC: `2026-06-13T06:43:30Z`

## Purpose
Close the remaining local rights-reference symlink boundary by rejecting LICENSE/COPYING/NOTICE targets reached through a symlinked intermediate archive path component.

## Risk reduced
A rights-ready future tree cannot satisfy a local license/notice reference through docs/link/LICENSE when docs/link is a symlink, even when the resolved target points back inside the archive.

## Dynamic cases
- clean nested local LICENSE reference remains allowed
- intermediate symlink to an archive-internal directory is rejected and reports the first symlink component
- intermediate symlink to an outside directory remains blocking rather than silently treated as a resolved local target

## Validator
- Command: `/opt/pyvenv/bin/python3 scripts/validate_publication_rights_gate_intermediate_symlink_rev0846.py`
- Return code: `0`
- Stdout: `publication-rights-gate-intermediate-symlink-rev0846: OK`

## Limits
- This audit validates local-reference integrity only; it does not determine license compatibility or legal sufficiency.
- The overlay bundle is a partial surface, so the full canonical tree still needs a final rights-ledger refresh after owner-approved license/notice content exists.
