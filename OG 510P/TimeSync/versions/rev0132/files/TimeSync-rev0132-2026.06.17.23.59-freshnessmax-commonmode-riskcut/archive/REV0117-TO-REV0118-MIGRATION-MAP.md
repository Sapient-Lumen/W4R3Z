# Migration map — rev0117 to rev0118

## Added

- `AUDIT-2026.06.13-rev0118.md`
- `archive/REV0118-AUDIT-EVIDENCE-WITNESS-MUTATOR-REFACTOR.md`
- `archive/REV0117-TO-REV0118-MIGRATION-MAP.md`
- `examples/negative/evidence-summary-minimum-profile-default-ignored-invalid.json`
- `examples/negative/evidence-summary-minimum-policy-acceptance-stale-invalid.json`
- `examples/negative/replay-transparency-witness-status-unchecked-invalid.json`
- `examples/negative/replay-transparency-witness-split-unchecked-invalid.json`
- fixture derivations `DF-0118-001` through `DF-0118-004`
- semantic vectors `TV-N328` through `TV-N331`
- mutation probes `MP-0118-001` through `MP-0118-004`

## Changed

- `tools/evidence_summary_semantics.py` now distinguishes name coverage from usable minimum-summary coverage for satisfied profile conclusions.
- `tools/validate_archive.py` now rejects witness/monitor checked-status downgrades that preserve a positive basis and threshold evidence.
- `tools/mutation_survivor_audit.py` now runs 18 probes.
- Current-facing revision documents now identify rev0118.
- `REVISION-RECEIPT.json`, `CHANGELOG.md`, `frontier-ticket.json`, `VALIDATION-REPORT.md`, and `MANIFEST.json` were regenerated or updated for rev0118.

## Compatibility notes

The TimeState core, schemas, profile catalog, transport adapters, and evidence class catalog are unchanged. The behavioral tightening affects only invalid combinations: satisfied summaries with unusable minimum items, and positive witness/monitor postures that have been downgraded to unchecked or split-view-unknown states.
