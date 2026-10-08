# Cargo Plumbing Interop Kit fixtures

These fixtures are for **P-0432 Cargo Plumbing Interop Kit**.

They freeze the phase-and-receipt layer above evolving Cargo plumbing commands:

- phase input intent,
- manifest / lockfile / feature-resolution / build-plan snapshots,
- and blocker-aware receipts.

These fixtures should help keep plumbing interop distinct from:

- fix-campaign orchestration,
- resolver explanation bundles,
- and workspace-boundary doctoring.

Scenario families in this pass:
- `edited_manifest_not_preserved/`
- `phase_roundtrip_build_plan/`
