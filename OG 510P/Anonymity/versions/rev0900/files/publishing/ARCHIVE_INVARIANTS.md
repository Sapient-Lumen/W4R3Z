# Archive Invariants

Declare semantic archive invariants that should remain stable across future refactors, then check them directly rather than leaving them implicit.

## INV-0001 — Default no-publication posture

Absent a new explicit written decision, the archive defaults to hold / no publication rather than promotion or release.

**Anchor surfaces:** `publishing/CANONICAL_POLICY.json`, `release_queue/LATEST_DECISION.md`, `publishing/TURN_DECISION_PROTOCOL.md`

**Checked by:** `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`

## INV-0002 — Legacy Mathematics links remain canonical

The five Mathematics-era links stay canonical public heads until a later explicit decision says otherwise; they are not retroactively replaced by Anonymity names.

**Anchor surfaces:** `published/CITATION_HEADS.md`, `published/citation_heads.json`, `published/LEGACY_PUBLISHED_LINKS.md`, `published/legacy_published_links.json`, `published/PUBLISHED_COMPILE_TRIAGE.json`, `published/PUBLISHED_COMPILE_TRIAGE.md`, `publishing/check_published_compile_triage.py`

**Checked by:** `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`, `publishing/check_published_compile_triage.py`, `publishing/check_archive_coherence.py`

## INV-0003 — Frozen in repo is not automatically public

A file may be frozen under published/ without becoming a current public citation head, and those categories must remain explicitly distinct.

**Anchor surfaces:** `published/PUBLICATION_CLASSIFICATION.md`, `published/publication_classification.json`, `published/CITATION_HEADS.md`, `published/PUBLIC_SURFACE.json`

**Checked by:** `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`

## INV-0004 — Canonical public heads are TeX; artifact-governance releases may add evidence packs

The canonical public citation head remains the .tex source, while papers that make artifact-governance claims may also require a minimal evidence pack at publication time.

**Anchor surfaces:** `publishing/CANONICAL_POLICY.json`, `PUBLISHING.md`, `publishing/RELEASE_FLOW.md`, `published/citation_heads.json`, `published/PUBLIC_SURFACE.json`

**Checked by:** `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`

## INV-0005 — Compact surfaces must agree or fail closed

If machine-readable control surfaces disagree, the correct response is no publication until the disagreement is repaired.

**Anchor surfaces:** `reports/archive_surface_coherence.json`, `reports/context_pack_contract.json`, `reports/manifest_sha256_verification.json`, `reports/manifest_coverage_audit.json`, `reports/transient_surface_audit.json`, `reports/citation_closure_audit.json`, `reports/release_readiness_audit.json`, `reports/evidence_pack_audit.json`, `reports/research_metadata_integrity.json`, `reports/support_manifest_integrity.json`, `release_queue/HOLD_COMPILE_TRIAGE.json`, `release_queue/HOLD_COMPILE_TRIAGE.md`, `publishing/check_unqueued_compile_triage.py`, `release_queue/UNQUEUED_COMPILE_TRIAGE.md`, `release_queue/UNQUEUED_COMPILE_TRIAGE.json`, `reports/queue_compile_smoke.json`, `publishing/check_queue_compile_smoke.py`, `publishing/run_queue_compile_smoke.sh`, `reports/python_entrypoint_smoke.json`, `publishing/check_python_entrypoint_smoke.py`, `Makefile`, `publishing/run_verify_surfaces.py`, `release_queue/UNQUEUED_SOURCE_INVENTORY.md`

**Checked by:** `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`

## INV-0006 — Shipped archive is source-first and transient-pruned

The shipped bundle should prefer source and control surfaces over stray compile products, caches, and transient byproducts.

**Anchor surfaces:** `PRUNING_POLICY.md`, `PRUNED_TRANSIENT.paths`, `reports/transient_surface_audit.json`

**Checked by:** `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`

## INV-0007 — Revision identity is singular

The bundle should present one coherent revision identity across VERSION, manifest, receipt, queue index, and archive index.

**Anchor surfaces:** `VERSION`, `RELEASE_MANIFEST.json`, `REVISION_RECEIPT.json`, `ARCHIVE_INDEX.json`, `release_queue/QUEUE_INDEX.json`

**Checked by:** `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`

## INV-0008 — Compared datacube inputs are anchored by name and hash

When this archive claims to have transferred ideas from other datacubes, the compared external bundles should be recorded by exact filename and SHA-256 hash, and that provenance should agree with the transfer ledger.

**Anchor surfaces:** `TRANSFER_SOURCES.json`, `TRANSFER_SOURCES.md`, `TRANSFER_INPUTS.sha256`, `DATACUBE_TRANSFER_LEDGER.json`, `reports/transfer_source_receipt.json`

**Checked by:** `publishing/check_transfer_source_receipt.py`, `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`, `reports/transfer_source_receipt.json`

## INV-0009 — Nested support manifests must verify against shipped bytes

Every nested support_manifest.json file row must resolve from explicit path-base semantics to an in-archive file whose SHA-256 digest matches the manifest claim.

**Anchor surfaces:** `publishing/check_support_manifest_integrity.py`, `reports/support_manifest_integrity.json`, `series/synthesis/paper17_worked_example_receipt_interlock/artifacts/support_manifest.json`

**Checked by:** `publishing/check_support_manifest_integrity.py`, `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`, `reports/support_manifest_integrity.json`

## INV-0010 — Research-object metadata and provenance remain anchored

Root-level citation, research-object metadata, notice/license, and provenance files must exist, be included in the assurance-artifact catalog, and pass the research metadata integrity report.

**Anchor surfaces:** `CITATION.cff`, `codemeta.json`, `ro-crate-metadata.json`, `LICENSE`, `NOTICE`, `release_provenance.intoto.jsonl`, `ASSURANCE_ARTIFACTS.json`, `publishing/check_research_metadata.py`, `reports/research_metadata_integrity.json`

**Checked by:** `publishing/check_research_metadata.py`, `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`, `reports/research_metadata_integrity.json`, `ASSURANCE_ARTIFACTS.json`

## INV-0011 — Paper citation and reference closure is explicit before freeze

Every shipped paper.tex must have static local citation/reference closure, and the aggregate citation graph must have no globally undefined citation keys or malformed bibliography command fragments.

**Anchor surfaces:** `reports/citation_closure_audit.json`, `publishing/check_citation_closure.py`, `publishing/release_preflight.py`

**Checked by:** `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`

## INV-0012 — Published-ready is audited, source-hash-bound, and not self-publishing

Every Published-ready queue item must pass static release-readiness checks and carry the current source SHA-256 in its queue note; Candidate items remain non-release-targets unless promoted; the audit itself must not authorize publication.

**Anchor surfaces:** `reports/release_readiness_audit.json`, `publishing/check_release_readiness.py`, `release_queue/QUEUE_INDEX.json`, `release_queue/published_ready/`

**Checked by:** `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`, `reports/release_readiness_audit.json`

## INV-0013 — Review inventory source identities match shipped bytes

The review inventory must cover the current unpublished paper universe exactly and each sha256_prefix row must match the shipped paper.tex bytes.

**Anchor surfaces:** `release_queue/REVIEW_INVENTORY.json`, `publishing/build_review_inventory.py`, `reports/review_inventory_coverage.json`, `reports/review_inventory_integrity.json`

**Checked by:** `publishing/check_review_inventory_coverage.py`, `publishing/check_review_inventory_integrity.py`, `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`

## INV-0014 — Active operator quick checks are bytecode-safe

Active operator-facing command examples should use python3 -B or make targets so validation commands do not create transient __pycache__ files inside the archive.

**Anchor surfaces:** `START_HERE.md`, `CONTEXT_PACK.json`, `publishing/OPERATOR_STARTUP.md`, `release_queue/STATUS.md`, `reports/operator_command_hygiene.json`, `Makefile`, `publishing/run_verify_surfaces.py`, `release_queue/UNQUEUED_SOURCE_INVENTORY.md`

**Checked by:** `publishing/check_operator_command_hygiene.py`, `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`

## INV-0015 — Evidence-pack gates are explicit and non-authorizing

Queued sources with artifact-governance language must surface an evidence-pack attachment-or-waiver gate before freeze; the audit must not authorize publication.

**Anchor surfaces:** `reports/evidence_pack_audit.json`, `publishing/check_evidence_pack_policy.py`, `reports/release_readiness_audit.json`

**Checked by:** `publishing/check_evidence_pack_policy.py`, `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`

## INV-0016 — Next release freeze plan is bound and non-authorizing

The dry-run next-release freeze plan must bind the selected source and source SHA-256, expose every pending manual gate as publication-blocking, carry no failed static gates, and never authorize publication. A deliberately unstaged evidence lane is integrity-valid only when the pending evidence gate is explicit and blocking.

**Anchor surfaces:** `release_queue/NEXT_RELEASE_FREEZE_PLAN.json`, `release_queue/NEXT_RELEASE_FREEZE_PLAN.md`, `publishing/build_release_freeze_plan.py`

**Checked by:** `publishing/build_release_freeze_plan.py`, `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`

## INV-0017 — Attached evidence packs are registry-bound and digest-checked

A selected freeze-target evidence pack must be named in the registry, resolve inside the archive, bind the current source SHA-256, and verify all pack file digests without authorizing publication.

**Anchor surfaces:** `release_queue/EVIDENCE_PACK_REGISTRY.json`, `release_queue/evidence_packs/2026.05.21-certified-menus-for-anonymous-dht-lookups/EVIDENCE_PACK_MANIFEST.json`, `publishing/check_evidence_pack_integrity.py`, `reports/evidence_pack_integrity.json`

**Checked by:** `publishing/check_evidence_pack_integrity.py`, `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`, `reports/evidence_pack_integrity.json`

## INV-0018 — Compile witness evidence is source-bound, deterministic when gate-closing, and non-authorizing

A compile-witness surface must bind the selected source hash. It closes the publication compile gate only with current, clean, deterministic multi-pass evidence and compile_gate_status=pass. A carried-forward witness or an explicit no-compile witness for an unstaged evidence lane may pass integrity only while remaining publication-blocking and truthfully reporting that the compile gate is open.

**Anchor surfaces:** `release_queue/FREEZE_COMPILE_WITNESS.json`, `publishing/check_freeze_compile_witness.py`, `publishing/release_preflight.py`, `reports/freeze_compile_witness.json`, `publishing/check_freeze_toolchain.py`, `reports/freeze_toolchain.json`

**Checked by:** `publishing/check_freeze_compile_witness.py`, `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`, `reports/freeze_compile_witness.json`

## INV-0019 — Non-public freeze packets are source-bound and digest-checked

A staged next-release freeze packet must copy the selected source bytes exactly, bind the evidence pack, compile witness, and freeze plan by digest, remain outside published/, and never authorize publication.

**Anchor surfaces:** `release_queue/FREEZE_PACKET_REGISTRY.json`, `release_queue/freeze_packets/`, `publishing/build_release_freeze_packet.py`, `publishing/check_freeze_packet_integrity.py`, `reports/freeze_packet_integrity.json`

**Checked by:** `publishing/check_freeze_packet_integrity.py`, `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`

## INV-0020 — Published boundary is guarded against unclassified new releases

Every published/ .tex file must be classified as a legacy public head, repo-frozen noncanonical entry, or guarded new Anonymity release with receipt, decision, evidence, compile, and freeze-packet bindings.

**Anchor surfaces:** `published/publication_classification.json`, `published/citation_heads.json`, `published/PUBLIC_SURFACE.json`, `publishing/check_publication_boundary.py`, `reports/publication_boundary.json`, `publishing/create_published_entry.py`

**Checked by:** `publishing/check_publication_boundary.py`, `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`

## INV-0021 — Publication decision template names all manual gates

A manual publish decision must name the publish action, selected source, source hash, published name, evidence pack, compile witness, freeze packet, queue note, citation-head update, and publication receipt obligation before the guarded helper may run.

**Anchor surfaces:** `release_queue/PUBLICATION_DECISION_TEMPLATE.md`, `publishing/create_published_entry.py`, `reports/publication_decision_template.json`

**Checked by:** `publishing/check_publication_decision_template.py`, `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`

## INV-0022 — Canonical packaging recipe is deterministic and manifest-bound

The next zip should be produced from a checked packaging recipe whose dry run agrees with MANIFEST.json and whose command is exposed through the Makefile, rather than by an implicit hand-packaging step.

**Anchor surfaces:** `publishing/build_archive_zip.py`, `publishing/check_archive_packaging_recipe.py`, `reports/archive_packaging_recipe.json`, `Makefile`

**Checked by:** `publishing/check_archive_packaging_recipe.py`, `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`

## INV-0023 — Freeze-lane TeX toolchain availability is explicit

The archive must report whether the local environment can refresh a clean LaTeX compile witness; absence of TeX is not an integrity failure, but it leaves the publication compile gate pending.

**Anchor surfaces:** `publishing/check_freeze_toolchain.py`, `reports/freeze_toolchain.json`, `publishing/build_freeze_compile_witness.py`

**Checked by:** `publishing/check_freeze_toolchain.py`, `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`

## INV-0024 — Publication rehearsal is bound and non-authorizing

A dry-run publication rehearsal must bind the selected source, queue note, evidence pack, compile-witness state, freeze packet, decision template, boundary guard, and packaging recipe without creating a public citation head or authorizing publication.

**Anchor surfaces:** `publishing/build_publication_rehearsal.py`, `reports/publication_rehearsal.json`, `release_queue/NEXT_RELEASE_FREEZE_PLAN.json`

**Checked by:** `publishing/build_publication_rehearsal.py`, `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`

## INV-0025 — Assurance artifact catalog is current and rendered from JSON

ASSURANCE_ARTIFACTS.json must match the current revision, every cataloged path must resolve, and ASSURANCE_ARTIFACTS.md must be a rendered mirror of the JSON catalog.

**Anchor surfaces:** `ASSURANCE_ARTIFACTS.json`, `ASSURANCE_ARTIFACTS.md`, `reports/assurance_catalog_integrity.json`

**Checked by:** `publishing/check_assurance_catalog.py`, `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`

## INV-0026 — Publishing tool inventory is digest-bound

Every publishing/*.py script must appear in TOOLING_INVENTORY.json with its current SHA-256, role, and side-effect classification; drift is publication-blocking until regenerated.

**Anchor surfaces:** `publishing/TOOLING_INVENTORY.json`, `reports/tooling_inventory_integrity.json`

**Checked by:** `publishing/build_tooling_inventory.py`, `publishing/check_tooling_inventory_integrity.py`, `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`

## INV-0027 — All report JSON surfaces are schema-visible

Every reports/*.json surface must be included in surface schema validation, either by a bespoke schema or by the generic report schema; no report may silently escape schema coverage.

**Anchor surfaces:** `reports/surface_schema_validation.json`, `reports/report_schema_coverage.json`, `schemas/generic_report.schema.json`

**Checked by:** `publishing/check_surface_schemas.py`, `publishing/check_report_schema_coverage.py`, `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`

## INV-0028 — Rebuild fixed-point tail targets cover tail-mutated outputs

Every manifest, report, ledger, and provenance surface mutated by the rebuild tail loop must be declared in TAIL_TARGETS and exist before the archive trusts a settled rebuild pass.

**Anchor surfaces:** `publishing/rebuild_archive_surfaces.py`, `publishing/check_rebuild_fixed_point_coverage.py`, `reports/rebuild_fixed_point_coverage.json`

**Checked by:** `publishing/check_rebuild_fixed_point_coverage.py`, `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`

## INV-0029 — Real publication decisions require complete authorization

Decision notes are scanned for explicit publish actions; any real publication authorization must be complete, current, source-hash-bound, and aligned with evidence, compile, freeze-packet, public-head, and receipt requirements before the guarded publication helper may execute.

**Anchor surfaces:** `release_queue/decisions/`, `release_queue/PUBLICATION_DECISION_TEMPLATE.md`, `publishing/check_publication_decision_authorization.py`, `reports/publication_decision_authorization.json`

**Checked by:** `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`

## INV-0030 — Archive index narrative matches current revision identity

The JSON and Markdown archive index, release manifest, NOTICE, and CodeMeta description must agree on the current revision, bundle, and revision-focus narrative.

**Anchor surfaces:** `ARCHIVE_INDEX.json`, `ARCHIVE_INDEX.md`, `RELEASE_MANIFEST.json`, `NOTICE`, `codemeta.json`, `publishing/check_archive_index_integrity.py`, `reports/archive_index_integrity.json`

**Checked by:** `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`

## INV-0031 — Machine reports are revision- and bundle-bound

Every reports/*.json surface must carry the current revision, current bundle, non-authorizing publication posture, and a passing status; permissive generic schemas are not sufficient identity evidence.

**Anchor surfaces:** `reports/report_identity_coverage.json`, `publishing/check_report_identity_coverage.py`

**Checked by:** `publishing/check_report_identity_coverage.py`, `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`

## INV-0032 — Compiled publication artifacts remain quarantined

The shipped datacube must not silently include built PDFs, release zips, TeX byproducts, build-tree files, or files matching the recorded freeze-compile PDF digest unless a future explicit receipt policy allows them.

**Anchor surfaces:** `reports/publication_artifact_quarantine.json`, `publishing/check_publication_artifact_quarantine.py`, `release_queue/FREEZE_COMPILE_WITNESS.json`

**Checked by:** `publishing/check_publication_artifact_quarantine.py`, `publishing/check_archive_invariants.py`, `reports/archive_invariants.json`

## INV-0033 — Portable archive paths

All shipped file paths remain relative, NFC-normalized, free of casefold collisions and common zip/filesystem portability hazards.

**Anchor surfaces:** `reports/path_portability.json`, `publishing/check_path_portability.py`

**Checked by:** `publishing/check_archive_invariants.py`, `publishing/check_path_portability.py`

## INV-0034 — Deterministic packaging reproducibility

The canonical archive packager produces byte-identical zips in independent trials with sorted members, fixed timestamps, fixed compression, and manifest-matching membership.

**Anchor surfaces:** `reports/archive_packaging_reproducibility.json`, `publishing/check_archive_packaging_reproducibility.py`, `publishing/build_archive_zip.py`

**Checked by:** `publishing/check_archive_invariants.py`, `publishing/check_archive_packaging_reproducibility.py`

## INV-0035 — Classified JSON surface universe

Every JSON file is either schema-checked, a schema document, or explicitly governed by a named validator, registry, metadata, ledger, or legacy-reference classification.

**Anchor surfaces:** `reports/json_surface_catalog.json`, `publishing/check_json_surface_catalog.py`, `publishing/check_surface_schemas.py`

**Checked by:** `publishing/check_archive_invariants.py`, `publishing/check_json_surface_catalog.py`

## INV-0036 — All queue notes are source-hash bound

Every Candidate, Published-ready, and Hold queue note must name exactly one Source paper line and exactly one Queue-bound source SHA-256 that matches the current shipped paper bytes; queue index paths and queue-note directories must agree.

**Anchor surfaces:** `release_queue/QUEUE_INDEX.json`, `release_queue/candidates/`, `release_queue/published_ready/`, `release_queue/hold/`, `publishing/check_queue_note_source_binding.py`, `reports/queue_note_source_binding.json`

**Checked by:** `publishing/check_queue_note_source_binding.py`, `publishing/check_archive_invariants.py`, `reports/queue_note_source_binding.json`, `reports/archive_invariants.json`

## INV-0037 — Invariant catalog IDs are unique and mirrored

The invariant catalog must use unique, contiguous invariant IDs; the checker report must implement exactly the declared IDs; and the Markdown invariant surface must be rendered from the JSON catalog.

**Anchor surfaces:** `publishing/archive_invariants.json`, `publishing/ARCHIVE_INVARIANTS.md`, `publishing/render_archive_invariants.py`, `publishing/check_invariant_catalog_integrity.py`, `reports/invariant_catalog_integrity.json`

**Checked by:** `publishing/check_archive_invariants.py`, `publishing/check_invariant_catalog_integrity.py`, `reports/archive_invariants.json`, `reports/invariant_catalog_integrity.json`

## INV-0038 — Shipped text contains no local environment path leakage

Portable shipped text surfaces must not contain local workspace paths, user home paths, temporary build paths, sandbox links, or absolute file URIs from the build environment.

**Anchor surfaces:** `publishing/check_content_leakage.py`, `reports/content_leakage.json`

**Checked by:** `publishing/check_content_leakage.py`, `publishing/check_archive_invariants.py`, `reports/content_leakage.json`, `reports/archive_invariants.json`

## INV-0039 — Schema catalog integrity is checked before schema trust

Every shipped JSON Schema document must be a valid Draft 2020-12 schema, and every schema referenced by the surface-schema target set must exist before schema-validation results are trusted.

**Anchor surfaces:** `publishing/check_schema_catalog_integrity.py`, `reports/schema_catalog_integrity.json`, `schemas/schema_catalog_integrity.schema.json`, `publishing/check_surface_schemas.py`

**Checked by:** `publishing/check_schema_catalog_integrity.py`, `publishing/check_archive_invariants.py`, `reports/schema_catalog_integrity.json`, `reports/archive_invariants.json`

## INV-0040 — JSON machine surfaces must be parser-unambiguous standard JSON

Every shipped JSON file must parse with duplicate object keys and non-finite numeric literals rejected so archive governance cannot depend on last-key-wins or non-portable reader behavior.

**Anchor surfaces:** `publishing/check_json_key_integrity.py`, `reports/json_key_integrity.json`, `schemas/json_key_integrity.schema.json`

**Checked by:** `publishing/check_json_key_integrity.py`, `publishing/check_archive_invariants.py`, `reports/json_key_integrity.json`, `reports/archive_invariants.json`

## INV-0041 — Text surfaces are UTF-8, LF-normalized, and final-LF complete

Every shipped text surface must decode as UTF-8, contain no NUL or carriage-return bytes, and end with a final line feed; missing final line feeds are blocking failures, not warnings.

**Anchor surfaces:** `publishing/check_text_surface_normalization.py`, `reports/text_surface_normalization.json`, `schemas/text_surface_normalization.schema.json`

**Checked by:** `publishing/check_text_surface_normalization.py`, `publishing/check_archive_invariants.py`, `reports/text_surface_normalization.json`, `reports/archive_invariants.json`

## INV-0042 — Publishing tools have static and byte-compile entrypoint integrity

Every publishing/*.py tool must be syntactically valid, carry the standard annotations future import, avoid unexpected top-level execution and duplicate literal dictionary keys, and pass the Python byte-compile/publishing-entrypoint smoke gate.

**Anchor surfaces:** `publishing/check_tooling_static_integrity.py`, `reports/tooling_static_integrity.json`, `schemas/tooling_static_integrity.schema.json`, `publishing/TOOLING_INVENTORY.json`, `publishing/check_python_entrypoint_smoke.py`, `reports/python_entrypoint_smoke.json`, `schemas/python_entrypoint_smoke.schema.json`

**Checked by:** `publishing/check_tooling_static_integrity.py`, `publishing/check_archive_invariants.py`, `reports/tooling_static_integrity.json`, `reports/archive_invariants.json`, `publishing/check_python_entrypoint_smoke.py`, `reports/python_entrypoint_smoke.json`

## INV-0043 — Decision-note ledger is indexed, non-authorizing, and source-visible

Every decision note must be structurally legible, present in the decision index, explicit about no publication, aligned with the latest-decision pointer, and any Subject path it names must exist in the shipped source tree.

**Anchor surfaces:** `release_queue/decisions/`, `release_queue/DECISION_INDEX.json`, `release_queue/LATEST_DECISION.json`, `publishing/check_decision_note_integrity.py`, `reports/decision_note_integrity.json`, `schemas/decision_note_integrity.schema.json`

**Checked by:** `publishing/check_decision_note_integrity.py`, `publishing/check_archive_invariants.py`, `reports/decision_note_integrity.json`, `reports/archive_invariants.json`

## INV-0044 — Passing machine reports carry no warning debt

Every reports/*.json machine report must either pass with zero top-level warnings and zero positive warning-count fields or fail closed; warning-only pass states are not allowed.

**Anchor surfaces:** `publishing/check_report_warning_policy.py`, `reports/report_warning_policy.json`, `schemas/report_warning_policy.schema.json`

**Checked by:** `publishing/check_report_warning_policy.py`, `publishing/check_archive_invariants.py`, `reports/report_warning_policy.json`, `reports/archive_invariants.json`

## INV-0045 — Prospective publication targets are portable before materialization

Every future published target carried by readiness, freeze, blocker, rehearsal, evidence, or compile-witness surfaces must use the portable published/YYYY-MM-DD_slug_title contract before any publication helper can materialize it.

**Anchor surfaces:** `publishing/publication_target.py`, `publishing/check_publication_target_portability.py`, `reports/publication_target_portability.json`, `schemas/publication_target_portability.schema.json`, `release_queue/NEXT_RELEASE_FREEZE_PLAN.json`, `release_queue/FREEZE_PACKET_REGISTRY.json`

**Checked by:** `publishing/check_publication_target_portability.py`, `publishing/check_archive_invariants.py`, `reports/publication_target_portability.json`, `reports/archive_invariants.json`

## INV-0046 — Archive filesystem and zip entries are regular safe payloads

The shipped tree and deterministic package must contain no symlinks, special files, hardlinks, unexpected executables, duplicate zip members, directory entries, encrypted members, unsafe zip paths, comments, or extra metadata fields.

**Anchor surfaces:** `publishing/check_archive_entry_security.py`, `reports/archive_entry_security.json`, `schemas/archive_entry_security.schema.json`, `publishing/build_archive_zip.py`

**Checked by:** `publishing/check_archive_entry_security.py`, `publishing/check_archive_invariants.py`, `reports/archive_entry_security.json`, `reports/archive_invariants.json`

## INV-0047 — Bundle identity is singular across root control surfaces

VERSION, RELEASE_MANIFEST, REVISION_RECEIPT, REVISION_LINEAGE, ARCHIVE_INDEX, CONTEXT_PACK, QUEUE_INDEX, and LATEST_DECISION must all name the same revision, timestamped bundle, and no-publication posture.

**Anchor surfaces:** `VERSION`, `RELEASE_MANIFEST.json`, `REVISION_RECEIPT.json`, `REVISION_LINEAGE.json`, `ARCHIVE_INDEX.json`, `CONTEXT_PACK.json`, `reports/bundle_identity_consistency.json`, `schemas/bundle_identity_consistency.schema.json`

**Checked by:** `publishing/check_bundle_identity_consistency.py`, `publishing/check_archive_invariants.py`, `reports/bundle_identity_consistency.json`, `reports/archive_invariants.json`

## INV-0048 — Control-plane JSON path references resolve or are explicitly prospective

Compact control-plane JSON surfaces must not point to missing, unsafe, or nonportable archive paths; non-materialized publication targets must be detected as prospective target references.

**Anchor surfaces:** `publishing/CANONICAL_POLICY.json`, `publishing/control_surfaces.json`, `CONTEXT_PACK.json`, `ASSURANCE_ARTIFACTS.json`, `reports/control_surface_path_integrity.json`, `schemas/control_surface_path_integrity.schema.json`

**Checked by:** `publishing/check_control_surface_path_integrity.py`, `publishing/check_archive_invariants.py`, `reports/control_surface_path_integrity.json`, `reports/archive_invariants.json`

## INV-0049 — Exact duplicate content is explicitly classified

Every exact duplicate SHA-256 file group in the shipped tree must either be absent or match an explicit freeze-evidence allowlist entry.

**Anchor surfaces:** `publishing/check_duplicate_content_policy.py`, `reports/duplicate_content_policy.json`, `schemas/duplicate_content_policy.schema.json`, `release_queue/freeze_packets/2026.05.21-certified-menus-for-anonymous-dht-lookups/`

**Checked by:** `publishing/check_duplicate_content_policy.py`, `publishing/check_archive_invariants.py`, `reports/duplicate_content_policy.json`, `reports/archive_invariants.json`

## INV-0050 — TeX source safety is publication-blocking

Every shipped TeX source, including freeze-packet snapshots, must be free of shell-escape primitives and unsafe absolute, URL, pipe, or external input patterns before publication can be considered.

**Anchor surfaces:** `publishing/check_tex_source_safety.py`, `reports/tex_source_safety.json`, `schemas/tex_source_safety.schema.json`

**Checked by:** `publishing/check_tex_source_safety.py`, `publishing/check_archive_invariants.py`, `reports/tex_source_safety.json`, `reports/archive_invariants.json`

## INV-0051 — Secret-like text material is quarantined

Text surfaces must not contain obvious private-key markers or high-confidence token-like secret material, and any finding must be reported without echoing matched secret bytes.

**Anchor surfaces:** `publishing/check_secret_material_quarantine.py`, `reports/secret_material_quarantine.json`, `schemas/secret_material_quarantine.schema.json`

**Checked by:** `publishing/check_secret_material_quarantine.py`, `publishing/check_archive_invariants.py`, `reports/secret_material_quarantine.json`, `reports/archive_invariants.json`

## INV-0052 — Makefile targets remain bytecode-safe and non-bypassing

The root Makefile must expose canonical rebuild, verify, and package targets; Python commands must use bytecode suppression; verify-surfaces must remain non-mutating; and package must delegate to the deterministic archive builder.

**Anchor surfaces:** `Makefile`, `publishing/check_makefile_target_integrity.py`, `reports/makefile_target_integrity.json`, `schemas/makefile_target_integrity.schema.json`

**Checked by:** `publishing/check_makefile_target_integrity.py`, `publishing/check_archive_invariants.py`, `reports/makefile_target_integrity.json`, `reports/archive_invariants.json`

## INV-0053 — Manifests are canonical and mutually consistent

MANIFEST.json and MANIFEST.sha256 must be sorted, duplicate-free, path-safe, byte-canonical, tree-complete, and digest-consistent before packaging.

**Anchor surfaces:** `MANIFEST.json`, `MANIFEST.sha256`, `reports/manifest_canonicality.json`, `publishing/check_manifest_canonicality.py`

**Checked by:** `publishing/check_manifest_canonicality.py`, `publishing/check_archive_invariants.py`, `reports/manifest_canonicality.json`, `reports/archive_invariants.json`

## INV-0054 — Freeze preflight warnings must be resolved

Static freeze preflight warnings may not remain implicit warning debt; each warning must be classified and resolved by a later gate or explicit waiver before publication can proceed.

**Anchor surfaces:** `release_queue/NEXT_RELEASE_FREEZE_PLAN.json`, `reports/freeze_warning_resolution.json`, `publishing/check_freeze_warning_resolution.py`

**Checked by:** `publishing/check_freeze_warning_resolution.py`, `publishing/check_archive_invariants.py`, `reports/freeze_warning_resolution.json`, `reports/archive_invariants.json`

## INV-0055 — Clean compile witnesses carry toolchain fingerprints

A closed clean-compile gate must bind the observed TeX command path and version-output fingerprint so compile evidence is not detached from the toolchain that produced it.

**Anchor surfaces:** `reports/freeze_toolchain.json`, `release_queue/FREEZE_COMPILE_WITNESS.json`, `reports/toolchain_fingerprint.json`, `publishing/check_toolchain_fingerprint.py`

**Checked by:** `publishing/check_toolchain_fingerprint.py`, `publishing/check_archive_invariants.py`, `reports/toolchain_fingerprint.json`, `reports/archive_invariants.json`

## INV-0056 — Hidden Unicode and control characters are publication-blocking

Text surfaces must not contain C0/C1 controls beyond LF/TAB, bidirectional control characters, invisible format controls, surrogate code points, or Unicode noncharacters; findings must identify code points without echoing surrounding text.

**Anchor surfaces:** `publishing/check_unicode_control_hygiene.py`, `reports/unicode_control_hygiene.json`, `schemas/unicode_control_hygiene.schema.json`

**Checked by:** `publishing/check_unicode_control_hygiene.py`, `publishing/check_archive_invariants.py`, `reports/unicode_control_hygiene.json`, `reports/archive_invariants.json`
