# Audit/refactor notes — rev0041

The audit/refactor work this turn was intentionally narrow.

## Refactored checks

- `tools/evidence_integrity_audit.py` now distinguishes resolved source-level defects from remaining known blockers instead of requiring every quarantined lane to stay quarantined forever.
- `tools/current_scientific_run_audit.py` audits only current-revision scientific artifacts, checks run provenance, checks source-hash consistency where possible, samples guard fields, and verifies that the old GVR and gate duplicate patterns are absent.
- `tools/smoke_validate.py` now has a `scientific_repair` path requiring the three fresh rev0041 artifacts, the run manifest, and current-run audit outputs.

## Substance preserved

The audit does not promote the project. It records that rev0041 has inspectable current evidence and that two old code defects were removed. The remaining blockers are still explicit: bridge forward annealing, block-index observability/timing, and measured cost.
