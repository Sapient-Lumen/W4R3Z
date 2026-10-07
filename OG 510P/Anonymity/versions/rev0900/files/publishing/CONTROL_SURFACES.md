# Control Surfaces

Use this map when a question is really about archive state rather than paper content.
The machine-readable companion is `publishing/control_surfaces.json`.

## Highest-use surfaces

- Current public citation heads: `published/CITATION_HEADS.md` / `published/citation_heads.json`
- Queue state: `release_queue/QUEUE_INDEX.json`, `release_queue/STATUS.md`, `release_queue/QUEUE.md`
- Reviewable paper universe, queue coverage, and source hashes: `release_queue/REVIEW_INVENTORY.json` plus `reports/review_inventory_coverage.json` and `reports/review_inventory_integrity.json`
- Latest written decision: `release_queue/LATEST_DECISION.md` / `release_queue/LATEST_DECISION.json`
- Archive coherence: `reports/archive_surface_coherence.json`
- Operator command hygiene: `reports/operator_command_hygiene.json`
- Evidence-pack release gate: `reports/evidence_pack_audit.json`
- Next release dry-run freeze plan: `release_queue/NEXT_RELEASE_FREEZE_PLAN.md` / `release_queue/NEXT_RELEASE_FREEZE_PLAN.json`
- Non-public freeze packet: `release_queue/FREEZE_PACKET_REGISTRY.json` / `reports/freeze_packet_integrity.json`
- Freeze compile/toolchain state: `reports/freeze_compile_witness.json` / `reports/freeze_toolchain.json`
- Publication rehearsal: `reports/publication_rehearsal.json`
- Published-boundary guard: `reports/publication_boundary.json` / `publishing/check_publication_boundary.py`
- One-command rebuild of compact surfaces: `python3 -B publishing/rebuild_archive_surfaces.py --root .` or `make rebuild-surfaces`
- Report identity coverage: `reports/report_identity_coverage.json` / `publishing/check_report_identity_coverage.py`
- Publication artifact quarantine: `reports/publication_artifact_quarantine.json` / `publishing/check_publication_artifact_quarantine.py`
- Queue note source binding: `reports/queue_note_source_binding.json` / `publishing/check_queue_note_source_binding.py`
- Invariant catalog integrity: `reports/invariant_catalog_integrity.json` / `publishing/check_invariant_catalog_integrity.py`
- Content leakage guard: `reports/content_leakage.json` / `publishing/check_content_leakage.py`
- Decision-note ledger integrity: `reports/decision_note_integrity.json` / `publishing/check_decision_note_integrity.py`
- Report warning policy: `reports/report_warning_policy.json` / `publishing/check_report_warning_policy.py`
- Publication target portability: `reports/publication_target_portability.json` / `publishing/check_publication_target_portability.py`
- Manifest canonicality: `reports/manifest_canonicality.json` / `publishing/check_manifest_canonicality.py`
- Freeze warning resolution: `reports/freeze_warning_resolution.json` / `publishing/check_freeze_warning_resolution.py`
- Toolchain fingerprint: `reports/toolchain_fingerprint.json` / `publishing/check_toolchain_fingerprint.py`

## Precedence rule

When surfaces disagree, default to no publication and repair the compact machine state before making a queue or release move.
For the full question map, read `publishing/control_surfaces.json`.

## rev0811 additions

- Current-revision compile-witness builder: `publishing/build_freeze_compile_witness.py` plus `release_queue/FREEZE_COMPILE_WITNESS.json` and `reports/freeze_compile_witness.json`
- Manual publication decision template: `release_queue/PUBLICATION_DECISION_TEMPLATE.md` plus `reports/publication_decision_template.json`
- Deterministic archive packaging recipe: `publishing/build_archive_zip.py`, `reports/archive_packaging_recipe.json`, and the `make package` target

These surfaces are non-authorizing. They make stale compile witnesses, incomplete decision notes, and ad hoc packaging fail closed before a public move.

## rev0812 additions

- Toolchain-aware compile-gate status: `publishing/check_freeze_toolchain.py` and `reports/freeze_toolchain.json`
- Non-authorizing publication rehearsal: `publishing/build_publication_rehearsal.py` and `reports/publication_rehearsal.json`

These surfaces keep the archive coherent when a TeX toolchain is unavailable, while making clear that publication remains blocked until the current compile gate is refreshed.


### rev0814 — rebuild fixed-point guard

The archive now includes `publishing/check_rebuild_fixed_point_coverage.py` and `reports/rebuild_fixed_point_coverage.json` so tail-mutated rebuild surfaces cannot escape the declared convergence target set. No publication was authorized.

## rev0815 additions

- Publication decision authorization scan: `publishing/check_publication_decision_authorization.py`, `reports/publication_decision_authorization.json`.
- Archive-index narrative integrity: `publishing/check_archive_index_integrity.py`, `reports/archive_index_integrity.json`.

## rev0816 additions

- Report identity coverage: `publishing/check_report_identity_coverage.py`, `reports/report_identity_coverage.json`.
- Publication artifact quarantine: `publishing/check_publication_artifact_quarantine.py`, `reports/publication_artifact_quarantine.json`.

These surfaces make stale generic reports and silently shipped compiled artifacts publication-blocking while preserving the no-publication posture.

## rev0817 additions

- Portable path guard: `publishing/check_path_portability.py`, `reports/path_portability.json`, and `schemas/path_portability.schema.json`.
- Packaging reproducibility guard: `publishing/check_archive_packaging_reproducibility.py`, `reports/archive_packaging_reproducibility.json`, and `schemas/archive_packaging_reproducibility.schema.json`.
- JSON surface catalog: `publishing/check_json_surface_catalog.py`, `reports/json_surface_catalog.json`, and `schemas/json_surface_catalog.schema.json`.

These surfaces make archive movement, zip packaging, and JSON payload governance fail closed before a release action. They do not authorize publication.

## rev0818 additions

- All-queue source-hash binding: `publishing/check_queue_note_source_binding.py`, `reports/queue_note_source_binding.json`, and `schemas/queue_note_source_binding.schema.json`.
- Invariant catalog / Markdown mirror integrity: `publishing/render_archive_invariants.py`, `publishing/check_invariant_catalog_integrity.py`, `reports/invariant_catalog_integrity.json`, and `schemas/invariant_catalog_integrity.schema.json`.
- Text-content local path leakage guard: `publishing/check_content_leakage.py`, `reports/content_leakage.json`, and `schemas/content_leakage.schema.json`.

These surfaces make queue-note drift, stale invariant mirrors, and local build-path leakage fail closed. They do not authorize publication.
## rev0819 additions

- Schema catalog integrity: `publishing/check_schema_catalog_integrity.py`, `reports/schema_catalog_integrity.json`, and `schemas/schema_catalog_integrity.schema.json`.
- Duplicate/portable JSON parser integrity: `publishing/check_json_key_integrity.py`, `reports/json_key_integrity.json`, and `schemas/json_key_integrity.schema.json`.
- Text-surface normalization: `publishing/check_text_surface_normalization.py`, `reports/text_surface_normalization.json`, and `schemas/text_surface_normalization.schema.json`.
- Publishing-tool static integrity: `publishing/check_tooling_static_integrity.py`, `reports/tooling_static_integrity.json`, and `schemas/tooling_static_integrity.schema.json`.
- Decision-note ledger integrity: `publishing/check_decision_note_integrity.py`, `reports/decision_note_integrity.json`, and `schemas/decision_note_integrity.schema.json`.

These surfaces make ambiguous JSON, invalid schema documents, non-normalized text bytes, broken publishing-tool source, and ambiguous decision-note history fail closed. They do not authorize publication.

## rev0820 additions

- Strict final-LF text normalization: `publishing/check_text_surface_normalization.py` now treats missing final line feeds as blocking failures.
- Machine-report warning policy: `publishing/check_report_warning_policy.py`, `reports/report_warning_policy.json`, and `schemas/report_warning_policy.schema.json`.

These surfaces remove warning-only pass states. They do not authorize publication.

## rev0821 additions

- Portable future publication target contract: `publishing/publication_target.py`, `publishing/check_publication_target_portability.py`, `reports/publication_target_portability.json`, and `schemas/publication_target_portability.schema.json`.

These surfaces make path-unsafe prospective published targets fail closed before the publication helper materializes them. They do not authorize publication.

## rev0822 additions

- Bundle identity consistency: `publishing/check_bundle_identity_consistency.py`, `reports/bundle_identity_consistency.json`, and `schemas/bundle_identity_consistency.schema.json`.
- Control-plane path-reference integrity: `publishing/check_control_surface_path_integrity.py`, `reports/control_surface_path_integrity.json`, and `schemas/control_surface_path_integrity.schema.json`.
- Duplicate-content policy: `publishing/check_duplicate_content_policy.py`, `reports/duplicate_content_policy.json`, and `schemas/duplicate_content_policy.schema.json`.

These surfaces make root identity drift, operator-navigation path drift, and unclassified exact duplicate bytes fail closed. They do not authorize publication.

## rev0823 source and command-surface safety

- TeX source safety: `publishing/check_tex_source_safety.py` / `reports/tex_source_safety.json`
- Secret-material quarantine: `publishing/check_secret_material_quarantine.py` / `reports/secret_material_quarantine.json`
- Makefile target integrity: `publishing/check_makefile_target_integrity.py` / `reports/makefile_target_integrity.json`

These gates are publication-blocking but never publication-authorizing.

## rev0824 additions

- Manifest canonicality: `publishing/check_manifest_canonicality.py`, `reports/manifest_canonicality.json`, and `schemas/manifest_canonicality.schema.json`.
- Freeze warning resolution: `publishing/check_freeze_warning_resolution.py`, `reports/freeze_warning_resolution.json`, and `schemas/freeze_warning_resolution.schema.json`.
- Toolchain fingerprint: `publishing/check_toolchain_fingerprint.py`, `reports/toolchain_fingerprint.json`, and `schemas/toolchain_fingerprint.schema.json`.

These gates make manifest drift, unresolved freeze warnings, and detached compile-toolchain evidence fail closed. They do not authorize publication.


## rev0825 addition

- `reports/unicode_control_hygiene.json` / `publishing/check_unicode_control_hygiene.py`: fail-closed text-control hygiene for C0/C1 controls beyond LF/TAB, bidi controls, invisible format controls, noncharacters, and surrogates.
