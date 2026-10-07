# Control Surfaces

Use this file when you remember the question but not the file.

## Reentry and bundle identity

- Fastest human reentry: `START_HERE.md`
- Fastest machine reentry: `CONTEXT_PACK.json`
- One-line shipped revision identity: `VERSION`
- Intended shipped bundle name / revision / timestamp / slug: `RELEASE_MANIFEST.json`
- Compact summary of what this revision changed and why: `REVISION_RECEIPT.json`
- Recent archive-shape/control-surface history: `ARCHIVE_INDEX.md` / `ARCHIVE_INDEX.json`
- Cross-datacube transfer history: `DATACUBE_TRANSFER_LEDGER.md` / `DATACUBE_TRANSFER_LEDGER.json`
- Exact compared-datacube input provenance: `TRANSFER_SOURCES.md` / `TRANSFER_SOURCES.json` / `TRANSFER_INPUTS.sha256`
- Grouped assurance-artifact catalog: `ASSURANCE_ARTIFACTS.md` / `ASSURANCE_ARTIFACTS.json`

## Current publication / citation questions

- What may be cited publicly right now?: `published/CITATION_HEADS.md` / `published/citation_heads.json`
- Which old public links are canonical and must remain valid?: `published/LEGACY_PUBLISHED_LINKS.md` / `published/legacy_published_links.json`
- Which files are frozen in-repo but not current public citation heads?: `published/PUBLICATION_CLASSIFICATION.md` / `published/publication_classification.json`
- What is the compact machine-readable stable published boundary?: `published/PUBLIC_SURFACE.json`

## Queue and decisions

- Current queue counts and item lists: `release_queue/QUEUE_INDEX.json`
- Current queue prose summary (generated): `release_queue/STATUS.md`
- Queue semantics / state meanings (generated): `release_queue/QUEUE.md`
- Latest written decision (human-generated from machine state): `release_queue/LATEST_DECISION.md`
- Latest written decision (machine): `release_queue/LATEST_DECISION.json`
- Decision history (human): `release_queue/DECISION_INDEX.md`
- Decision history (machine): `release_queue/DECISION_INDEX.json`
- Full timestamped decision notes: `release_queue/decisions/`
- Reviewable paper universe: `release_queue/REVIEW_INVENTORY.md` / `release_queue/REVIEW_INVENTORY.json`

## Structural contracts and invariants

- Are the core JSON control surfaces well-formed?: `reports/surface_schema_validation.json`
- Which archive truths should survive refactors?: `publishing/ARCHIVE_INVARIANTS.md` / `publishing/archive_invariants.json`
- Are those archive truths currently holding?: `reports/archive_invariants.json`
- Has `CONTEXT_PACK.json` stayed small enough to remain a real reentry packet?: `reports/context_pack_budget.json`
- Has the archive stayed under its size/file/root/report/schema budgets and avoided shipping `series/.../renderNNN/` review-render clutter?: `publishing/ARCHIVE_BUDGET.md` / `publishing/archive_budget_policy.json` / `reports/archive_budget.json`
- Where are the JSON schemas for the compact surfaces?: `schemas/README.md` and `schemas/*.schema.json`

## Review priority and policy

- Coarse family triage: `publishing/FAMILY_TRIAGE.md`
- Recommended review order: `publishing/REVIEW_ORDER.md`
- Per-paper review rubric: `publishing/REVIEW_RUBRIC.md`
- Conservative release policy: `publishing/CONSERVATIVE_RELEASE_POLICY.md`
- Release-state meanings and transitions: `publishing/RELEASE_FLOW.md`
- Turn-level decision protocol: `publishing/TURN_DECISION_PROTOCOL.md`
- Lifecycle gate map: `publishing/LIFECYCLE_GATES.md` / `publishing/lifecycle_gates.json`
- Current lifecycle gate statuses: `reports/lifecycle_gate_status.json`
- Compact machine policy surface: `publishing/CANONICAL_POLICY.json`

## Trust / integrity / drift checks

- Structural validation of the compact JSON surfaces: `publishing/check_surface_schemas.py` -> `reports/surface_schema_validation.json`
- Semantic archive invariants: `publishing/check_archive_invariants.py` -> `reports/archive_invariants.json`
- Context-pack compactness budget: `publishing/check_context_pack_budget.py` -> `reports/context_pack_budget.json`
- Archive size / file-count / review-render hygiene budget: `publishing/check_archive_budget.py` -> `reports/archive_budget.json`

- Cross-surface agreement report: `reports/archive_surface_coherence.json`
- Coherence checker: `publishing/check_archive_coherence.py`
- Context-pack contract report: `reports/context_pack_contract.json`
- Context-pack contract checker: `publishing/check_context_pack_contract.py`
- Transient-surface audit report: `reports/transient_surface_audit.json`
- Transient-surface audit checker: `publishing/check_transient_surface.py`
- Exact-checksum verification report: `reports/manifest_sha256_verification.json`
- Exact-checksum verifier: `publishing/verify_manifest_sha256.py`
- Manifest coverage report: `reports/manifest_coverage_audit.json`
- Manifest coverage checker: `publishing/check_manifest_coverage.py`
- Transfer-source receipt report: `reports/transfer_source_receipt.json`
- Transfer-source receipt checker: `publishing/check_transfer_source_receipt.py`

## Regeneration / repair

- Queue markdown renderer: `publishing/render_queue_surfaces.py`
- One-command rebuild of compact surfaces: `python3 publishing/rebuild_archive_surfaces.py --root .`
- Make shortcut for the same rebuild: `make rebuild-surfaces`
- Verification-only shortcut: `make verify-surfaces`

## Precedence rule

1. Citation questions -> `published/CITATION_HEADS.md`
2. Public-vs-frozen boundary -> `published/PUBLICATION_CLASSIFICATION.md`
3. Queue state -> `release_queue/QUEUE_INDEX.json`
4. Latest no-release / publish rationale -> `release_queue/LATEST_DECISION.md`
5. Stage-specific control-surface question -> `reports/lifecycle_gate_status.json` then `publishing/LIFECYCLE_GATES.md`
6. Cross-datacube transfer question -> `DATACUBE_TRANSFER_LEDGER.md` then `TRANSFER_SOURCES.md`
7. Assurance-artifact grouping question -> `ASSURANCE_ARTIFACTS.md`
8. Exact shipped revision / integrity / drift questions -> `VERSION`, `RELEASE_MANIFEST.json`, `REVISION_RECEIPT.json`, `reports/archive_surface_coherence.json`, `reports/context_pack_contract.json`, `reports/archive_budget.json`, `reports/transient_surface_audit.json`, `reports/manifest_sha256_verification.json`, `reports/manifest_coverage_audit.json`, `reports/transfer_source_receipt.json`, and `MANIFEST.sha256`
