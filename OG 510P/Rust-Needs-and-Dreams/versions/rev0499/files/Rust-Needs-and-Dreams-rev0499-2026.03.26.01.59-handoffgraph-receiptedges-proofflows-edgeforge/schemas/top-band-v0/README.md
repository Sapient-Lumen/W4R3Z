# Top-band kernel artifact schemas (rev0488)

This folder holds the archive's first **artifact schema pack** for the top-band kernels that already earned:
- a live decision packet,
- a bounded v0 kernel brief,
- a slice-0 milestone,
- a contract0 note,
- a witness/example bundle,
- and a replay fixture.

Current schema set:
- `build-session-pack.schema.json`
- `build-diff.schema.json`
- `debug-session-pack.schema.json`
- `debug-tuple-card.schema.json`
- `debug-replay-result.schema.json`
- `route-profile.schema.json`
- `intake-receipt.schema.json`
- `waiver-receipt.schema.json`
- `quarantine-receipt.schema.json`
- `incident-drill-report.schema.json`
- `readiness-card.schema.json`
- `readiness-pack.schema.json`
- `readiness-lint-report.schema.json`
- `readiness-diff.schema.json`
- `unsupported-state-receipt.schema.json`
- `stale-card-receipt.schema.json`
- `schema-pack-hygiene-checks.json`

Read with:
- `design/epic-contribution-kernel-artifact-schemas-2026Q1.md`
- `meta/KERNEL_ARTIFACT_SCHEMA_PROTOCOL.md`
- `specimens/kernel-contract-witnesses-v0/README.md`

Working rule:
- use schemas to validate the first machine-readable JSON artifact families for already-earned kernels;
- keep shared receipts shared;
- keep additive compatibility visible by requiring only the minimum fields the archive actually depends on;
- and do not treat these schemas as upstream Rust standards.
