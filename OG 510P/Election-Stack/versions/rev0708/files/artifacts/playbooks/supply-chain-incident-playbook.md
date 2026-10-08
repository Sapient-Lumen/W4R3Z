# Supply-chain incident playbook (verifier binaries / toolchain compromise)

**Track:** Shared (cross-cutting)


Use this playbook when build/provenance or dependency integrity is in doubt.

## Actions
- Freeze releases; publish an incident comms package with scope.
- Rebuild from known-good toolchain; compare outputs.
- Activate:
  - `CHECK:artifacts/checklists/release-integrity-checklist.md`
  - `CHECK:artifacts/checklists/pqc-migration-checklist.md` (if crypto libs implicated)

## Evidence obligations (North Star aligned)
- Publish provenance statements for rebuilt artifacts and diffs from previous builds.
