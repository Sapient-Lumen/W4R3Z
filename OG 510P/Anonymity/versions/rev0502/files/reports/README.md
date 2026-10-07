# Reports

This directory holds generated trust / drift / posture reports.
Treat them as compact answers, not as substitutes for the underlying source surfaces.

Important reports:

- `reports/surface_schema_validation.json`
- `reports/archive_invariants.json`
- `reports/lifecycle_gate_status.json`
- `reports/archive_surface_coherence.json`
- `reports/context_pack_contract.json`
- `reports/context_pack_budget.json`
- `reports/archive_budget.json`
- `reports/transient_surface_audit.json`
- `reports/manifest_sha256_verification.json`
- `reports/manifest_coverage_audit.json`
- `reports/transfer_source_receipt.json`
- `reports/published_ready_preflight.json`

Interpretation order:

1. structural contract (`surface_schema_validation.json`),
2. semantic invariant (`archive_invariants.json`),
3. stage/gate status (`lifecycle_gate_status.json`),
4. cross-surface agreement (`archive_surface_coherence.json`),
5. then the narrower specialized audits, including transfer-input provenance when the question is “what did we compare against?”.
