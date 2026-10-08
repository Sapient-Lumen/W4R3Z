# 162 — Release gates and CI evidence pipeline

**Track:** Shared


This doc defines a **minimum release gate** for this archive so it does not silently drift under
human or LLM edits.

The gate is intentionally boring: it enforces that artifacts remain **internally consistent** and
that external references do not change without notice.

## 162.1 Required checks (MUST pass for any release tag)

Canonical child-step order is defined by `scripts/release_gate_steps.py` and executed by `scripts/release_gate.py` (treat the shared inventory as authoritative to avoid runner/doc drift; see `docs/662-release-gate-single-source-step-inventory-and-list-contract.md`). Each top-level step is bounded by a fail-closed subprocess timeout; set `ELECTION_STACK_RELEASE_STEP_TIMEOUT=<seconds>` only when intentionally running a slower local audit, not to normalize a hanging check (see `docs/654-release-gate-subprocess-timeouts-and-ambient-environment-fail-closed-discipline.md`). The runner fails fast by default, reserves `--keep-going` for diagnostics, and skips manifest write/check after any prior failure so a known-bad tree cannot be sealed by `--write-manifest` (see `docs/655-release-gate-failure-locality-failfast-and-manifest-write-quarantine.md`). For localizing slow or stalled sections, maintainers may use `--list`, `--only`, `--from-step`, `--to-step`, `--profile`, `--progress`, `--step-timeout`, and `--skip-manifest`; these are diagnostic controls, and manifest writing remains a full-gate-only action (see `docs/657-release-gate-resumability-profiled-diagnostics-and-process-group-timeouts.md`). Child stdout/stderr capture is file-backed rather than pipe-backed, child stdin is closed, child `cwd` is pinned to the repo root, and POSIX slices clean up descendants that outlive the named child step (see `docs/661-release-gate-file-backed-child-capture-and-daemonization-firewall.md`). Release ZIP member modes are canonical `0644`, and a stdlib extraction/rebuild probe must remain byte-identical (see `docs/663-release-zip-permission-canonicalization-and-extraction-rebuild-invariance.md`). Release path syntax is governed by `scripts/release_path_policy.py`; manifest, ZIP, verifier, and extraction probes must reject ambiguous whitespace/control/non-ASCII/traversal names, component-prefix file/directory shape conflicts, and use `Path.relative_to`-style extraction containment (see `docs/664-release-path-policy-safe-extraction-and-central-directory-canonicalization.md` and `docs/671-release-extraction-tree-shape-conflict-firewall.md`). Release control-file bytes are governed by `scripts/release_control_files.py`; `VERSION` and `MANIFEST.sha256` must be LF-only canonical records, not tolerant text-normalized variants; `VERSION` also uses the unpadded semantic `vNNN` form with no leading zeroes, release ZIP filenames that carry `revNNNN`/`vNNN` tokens must keep every token coherent with that internal identity, and the ZIP verifier must reject lexically ambiguous input path spellings, symlink final input paths, or symlink-routed input ancestry so those filename-token checks apply to the operator-supplied basename; after that preflight, ZIP verification must use a single input byte snapshot for the reported hash, parser, raw layout checks, manifest hashes, and canonical rebuild comparison (see `docs/669-release-control-file-byte-canonicality-and-crlf-firewall.md`, `docs/682-release-version-number-canonicality-and-leading-zero-firewall.md`, `docs/683-release-filename-version-token-coherence-firewall.md`, `docs/684-release-zip-input-symlink-alias-firewall.md`, `docs/685-release-zip-single-snapshot-verification-firewall.md`, and `docs/686-release-zip-input-lexical-path-canonicality-firewall.md`). Manifest construction/checking is also byte-exact; explicit local-only paths are classified separately from governed release paths so unsafe governed names fail builders and extracted-tree verification rather than being silently omitted, builder-side file selection rejects symlinks or special files before hashing/packaging, release ZIP construction rejects ambiguous or symlink-routed source roots and output paths before discovering release members or publishing bytes, and ZIP member writing skips the output artifact only by lexical path equality while rechecking each selected source member as the same regular non-symlink file before reading bytes (see `docs/672-release-builder-byte-exact-manifest-and-file-type-firewall.md`, `docs/673-release-governed-path-closure-and-unsafe-local-file-firewall.md`, `docs/688-release-zip-builder-output-path-canonicality-firewall.md`, `docs/689-release-zip-builder-source-root-canonicality-firewall.md`, and `docs/690-release-zip-builder-source-member-read-canonicality-firewall.md`). The operator-facing extractor verifies the ZIP before writing, preserves raw ZIP input spelling through the hardened verifier, extracts from the verifier's accepted byte snapshot rather than reopening the path, extracts through the shared path policy into a temporary tree, verifies `MANIFEST.sha256` after extraction, rejects symlinked output roots or ancestry components before output-parent creation, rejects non-canonical raw output strings before `pathlib` normalization, avoids side effects for rejected output targets, and only then publishes the output directory (see `docs/668-release-safe-extractor-verified-two-phase-unpack-and-tree-recheck.md`, `docs/674-release-safe-extractor-output-ancestry-firewall.md`, `docs/675-release-safe-extractor-side-effect-free-output-preflight.md`, `docs/681-release-safe-extractor-lexical-output-path-canonicality-firewall.md`, and `docs/687-release-safe-extractor-zip-input-snapshot-bridge-firewall.md`).

### A. Structure + index integrity
- `scripts/check_index.py` (numbered docs must be indexed)
- `scripts/check_doc_number_collisions.py` (fail if a numbered doc ID collides without a tombstone alias)
- `scripts/check_tracks.py` (every numbered doc declares a Track)
- `scripts/check_adr_index.py` (ADR drift firewall: every ADR file is indexed and has Status/Date; prevents silent decision drift)
- `scripts/gen_track_bundles.py` (curated bundle entrypoints must resolve; no broken links)
- `scripts/gen_tombstone_index.py` (generated tombstone alias index stays current)
- `scripts/check_doc_links.py` (relative markdown links must resolve; prevents quiet link-rot)
- `scripts/check_doc_backtick_refs.py` (drift firewall: backticked numbered-doc references must resolve; catches filename typos that aren't links)
- `scripts/check_no_raw_urls_modern_docs.py` (for docs >=170, require `source:` citations instead of raw external URLs)
- `scripts/check_no_forbidden_example_tlds.py` (drift firewall: prevent misleading `example` placeholders under restricted TLDs; see `231`)
- `scripts/check_no_cache_artifacts.py` (fail if cache/build artifacts such as __pycache__/pyc, `tmp_emit_pvr/`, `dist/`, or evidence/cache payloads are present)
- `scripts/check_no_symlinks.py` (fail if any symlinks are present before packaging probes run; prevents non-portable bundles and symlink escape reads)
- `scripts/check_release_path_policy.py` (drift firewall: release paths must be POSIX relative ASCII names with no traversal, whitespace, control characters, reserved/forbidden portable-name shapes, case-insensitive collisions, file/directory extraction-shape conflicts, or string-prefix extraction escapes)
- `scripts/check_release_control_files.py` (drift firewall: `VERSION` and `MANIFEST.sha256` bytes must be LF-only canonical records; CRLF, missing-LF, whitespace, duplicate, unsorted, leading-zero, and non-`vNNN` probes fail closed)
- `scripts/check_release_builder_filesystem_policy.py` (drift firewall: manifest check/write must be raw-byte canonical, manifest/ZIP builders must reject unsafe governed paths, symlinks, or special files before hashing/packaging, and the release ZIP builder must reject ambiguous or symlink-routed output/source routes and source-member ancestry swaps before publication)
- `scripts/check_manifest_verifier.py` (drift firewall: the extracted-tree manifest verifier must accept the live tree under a freshly computed manifest and reject hash mismatch, missing/unlisted file, unsafe extra governed path, unsafe manifest path, duplicate, case-collision, extraction-shape, and symlink probes)
- `scripts/check_release_packaging_alignment.py` (drift firewall: deterministic ZIP file selection must equal manifest-sealed file selection plus `MANIFEST.sha256`; also exercises known local-only and ambiguous-path exclude predicates)
- `scripts/check_release_zip_verifier.py` (drift firewall: the ZIP-artifact verifier must accept a freshly built deterministic archive and reject filename-token disagreement/padded semantic filename tokens, symlink-routed input paths, hash-mismatch, duplicate-member, unsafe/ambiguous-path, reserved-path, case-collision, extraction-shape conflict, mode, overlay, preamble, and noncanonical-compression probes)
- `scripts/check_release_safe_extractor.py` (drift firewall: the verifier-backed safe extractor must verify before extraction, recheck manifest closure after extraction, preserve non-empty outputs without `--clean`, cleanly replace when requested, reject output symlinks where supported, reject non-canonical raw output paths before normalization, avoid creating redirected parents for rejected output targets, reject swapped member directories, and reject verified temporary-root swaps before publication)
- `scripts/check_release_zip_rebuild_from_extract.py` (drift firewall: a freshly built deterministic ZIP must rebuild byte-for-byte after stdlib extraction through the shared safe-extraction path policy; catches unsealed permission/metadata drift)
- `scripts/check_tool_maturity_registry.py` (drift firewall: every tool file is classified as operator/research/skeleton/library; prevents accidental misuse)
- `scripts/check_registries_readme.py` (drift firewall: registries README must list every `artifacts/registries/*.csv`; prevents silent surface drift)
- `scripts/check_envelope_kinds.py` (example EvidenceEnvelope kinds must be registered)
- `scripts/check_doc_envelope_kind_references.py` (doc references using `kind:` / `Envelope kind:` must refer to registered kinds)
- `scripts/check_envelope_payload_schemas.py` (envelope kinds must point to real schemas)
- `scripts/check_attachment_requirements.py` (required receipt/gossip attachments per kind)
- `scripts/check_attachment_registry_integrity.py` (attachment requirements registry must reference known kinds and existing schemas; no duplicate kind+rel rows)
- `scripts/check_example_packets.py` (example evidence packets must verify offline through the observer verifier core; prevents rot without hiding packet-local failures behind repeated subprocess calls)
- `scripts/check_example_packets_public_artifact_lint.py` (public example packets must avoid private/local-only artifacts and misleading publication surfaces)
- `scripts/check_example_packet_readmes.py` (drift firewall: example packets must include a tiny README.txt (size-capped) with a one-line Verify command)
- `scripts/check_example_payloads_against_schemas.py` (bounded payload-vs-schema drift tripwire for shipped example packets)
- `scripts/check_example_ordering_conventions.py` (drift firewall: example payload ordering conventions; stable sorting reduces diff churn)
- `scripts/check_example_report_pins.py` (drift firewall: verifier-report example pins + tool version must match canonical registry bytes and VERSION)
- `scripts/check_operator_smoke_coverage.py` (drift firewall: tools marked smoke_tested=yes must be invoked by the smoke harness)
- `scripts/check_operator_tools_smoke.py` (operator-facing card tools must run cleanly on shipped example packets)
- `scripts/check_public_surface_pins_coverage.py` (drift firewall: `tools/public_surface_pins.py --all --json` must cover and correctly hash stable registry bytes)
- `scripts/check_packet_paths.py` (fail if example packets contain unsafe relative paths)
- `scripts/check_object_uri_alignment.py` (example packets: object store integrity — URIs and bytes match declared digests; no orphan objects)
- `scripts/check_receipt_profiles.py` (example receipts must name a registry profile)
- `scripts/check_publication_triggers.py` (publication-trigger registry integrity: notice types, evidence kinds, and file references stay coherent)
- `scripts/check_election_milestones_registry.py` (election-milestone registry integrity: milestone vocabulary and file references stay coherent)
- `scripts/check_drill_scenarios.py` (drill scenario registry integrity: triggers, notice types, kinds, file refs)
- `scripts/check_known_issues_registry.py` (known-issues registry integrity: status enum + file refs; used for patch/mitigation transparency)
- `scripts/check_catastrophe_classes_registry.py` (catastrophe class vocabulary is strict + stable; used to prioritize hazards and design tradeoffs)
- `scripts/check_hazard_catastrophe_classes.py` (hazard register must use valid `C1..C5`; keeps prioritization explicit)
- `scripts/check_official_channels_registry.py` (official-channels registry integrity: canonical comms surfaces for PublicNotice channel IDs)
- `scripts/check_discovery_pointer_coherence.py` (drift firewall: WellKnown/OfficialChannelDirectory/PublicNoticeFeed example set must be mutually coherent; channel IDs must be registered)
- `scripts/check_public_notice_type_coherence.py` (drift firewall: PublicNotice.notice_type enum must be representable in PublicNoticeFeed entry metadata; prevents silent schema divergence)
- `scripts/check_proof_obligations.py` (claims/hazards may only reference registered POs)
- `scripts/check_no_tombstone_refs.py` (drift firewall: normative docs must cite canonical docs, not tombstone aliases)
- `scripts/check_tombstones.py` (tombstone aliases must be minimal and point to a live target)
- `scripts/check_no_private_keys.py` (fail if any private key material is present)
- `scripts/check_jcs_vectors.py` (drift tripwire for RFC8785 canonicalization rules)
- `scripts/check_observer_kit_jcs_mirror.py` (observer-kit JCS mirror must stay aligned with the canonical implementation/vector set)
- `scripts/check_results_hash_vectors.py` (drift tripwire for results-object TBS hashing + RESULTS-leaf payload hashing; see `235–236`)
- `scripts/check_compact_context_vectors.py` (drift tripwire for compact `req[]/vary[]/age[]` request-context notes; see `DOC:docs/232-compact-request-context-notes.md`)
- `scripts/check_envelope_vectors.py` (drift tripwire for EvidenceEnvelope payload/tbs digests)
- `scripts/check_version_consistency.py` (VERSION/CHANGELOG/START_HERE must agree)
- `scripts/check_release_gate_doc_coverage.py` (release-gate child scripts must be named in this control doc; prevents human checklist drift)
- `scripts/check_release_gate_step_inventory.py` (drift firewall: the shared release-gate step inventory must contain unique existing child scripts and match the runner `--list` output; prevents source-parser drift)
- `scripts/check_platform_media_companion_tags.py` (platform-media companion tags must remain bounded and internally coherent)
- `scripts/check_recent_changelog_version_sequence.py` (recent changelog head must descend contiguously by version; catches silently skipped release notes near the current tip)
- `scripts/check_voter_facing_public_answer_surfaces.py` (public-answer surface registry entries must resolve to their doc/template/checklist triplets)
- `scripts/check_voter_facing_surface_triplets.py` (voter-facing surface doc/template/checklist triplets must stay connected)
- `scripts/check_voter_facing_surface_range_references.py` (entrypoints that summarize voter-facing ranges must remain synchronized with the live surface perimeter)
- `scripts/check_voter_facing_surface_entrypoint_coverage.py` (root/start/index entrypoints must keep navigable coverage of voter-facing public-answer surfaces)
- `scripts/check_voter_facing_surface_anchor_lock_coverage.py` (promoted voter-facing family-tail docs must keep lockfile-backed official source anchors; prevents free-floating prose promotions without pinned official citations)
- `scripts/check_voter_facing_surface_structure_minimums.py` (promoted voter-facing family-tail docs and any newer `special_case_high_risk` rows below `323` must keep the standard bounded-surface section shape; prevents half-formed promotions that lose fallback/freshness/verification structure)
- `scripts/check_voter_facing_special_case_authority_minimums.py` (rows tagged `special_case_high_risk` must keep minimum authority, fallback, and verification language before more specific controls apply)
- `scripts/check_voter_facing_special_case_release_freshness.py` (rows tagged `special_case_high_risk` must keep at least two lockfile-backed official anchors reviewed within 90 days of the archive's release date; prevents shipping time-volatile edge-case voter surfaces with only stale official examples)
- `scripts/check_voter_facing_special_case_official_routing_precedence.py` (rows tagged `special_case_high_risk` must say that the current official state/local election-office source controls and that national/archive summaries are routing aids rather than substitutes; prevents well-sourced edge-case docs from reading like generalized national answers)
- `scripts/check_voter_facing_special_case_current_state_visibility.py` (rows tagged `special_case_high_risk` must say how to identify the current controlling official notice or instruction when older pages, PDFs, screenshots, packet inserts, or archive summaries remain visible; prevents high-risk edge-case docs from sounding current while leaving superseded material unresolved)
- `scripts/check_voter_facing_special_case_unresolved_conflict_stop.py` (rows tagged `special_case_high_risk` must say that unresolved conflicting official materials are a stop condition and that readers should not synthesize a controlling answer from fragments; prevents high-risk edge-case docs from bluffing past unresolved official disagreement instead of routing to current authoritative confirmation)
- `scripts/check_voter_facing_special_case_nonoverlap.py` (rows tagged `special_case_high_risk` must preserve adjacent-surface boundary language so high-risk cases do not duplicate or override neighboring surfaces)
- `scripts/check_voter_facing_special_case_fallback_escalation.py` (rows tagged `special_case_high_risk` must keep safe fallback/escalation language visible rather than implying a generalized national answer)
- `scripts/check_voter_facing_special_case_temporal_volatility.py` (rows tagged `special_case_high_risk` must preserve freshness and temporal-volatility warnings)
- `scripts/check_voter_facing_special_case_direct_jurisdiction_anchors.py` (rows tagged `special_case_high_risk` must carry at least two direct jurisdiction-specific official-public governing anchors; prevents high-risk edge-case docs from leaning only on national routing pages or generalized official summaries)
- `scripts/check_voter_facing_special_case_contactability.py` (rows tagged `special_case_high_risk` must expose a concrete official help/contact path and preserve `305`/`307` routing; prevents high-risk edge-case docs from stopping at abstract “contact the office” prose)
- `scripts/check_voter_facing_special_case_responsible_office_specificity.py` (rows tagged `special_case_high_risk` must identify which official office role actually owns the case and carry `authoritative_office_name` plus `authoritative_office_scope`; prevents reachable-but-ambiguous high-risk docs that still leave the voter unsure which office controls)
- `scripts/check_voter_facing_special_case_secure_channel_and_minimum_disclosure.py` (rows tagged `special_case_high_risk` must name an official secure path for sensitive records, warn against oversharing on public/unverified channels, and carry `official_secure_channel_note` plus `minimum_necessary_disclosure_note`; prevents high-risk docs from routing voters to the right office but the wrong submission channel)
- `scripts/check_voter_facing_special_case_operability_now.py` (rows tagged `special_case_high_risk` must say how to verify that the named office/path is still open and operating right now under same-day or deadline-near conditions, warn against stale hours/closure material, and carry `operability_now_note` plus `deadline_imminence_note`; prevents high-risk docs from naming the right path but not whether it is still usable)
- `scripts/check_voter_facing_special_case_triplet_propagation.py` (rows tagged `special_case_high_risk` must propagate the latest high-risk help-route / office-identity / secure-channel / operability fields into the linked template and checklist, not just the numbered doc; prevents doc-only control drift across the triplet)
- `scripts/check_voter_facing_special_case_freshness_current_state_conflict_propagation.py` (rows tagged `special_case_high_risk` must also propagate the bounded review-window / current-official-controls / superseding-notice / unresolved-conflict-stop fields into the linked template and checklist, not just the numbered doc; prevents older high-risk controls from surviving only in prose)
- `scripts/check_voter_facing_special_case_control_stack_reference_closure.py` (the special-case maintainer-control docs must keep a live pointer to one canonical ordered `344–361` stack map, and the canonical stack section itself must stay current; prevents older control docs from becoming stale navigation surfaces after newer tail controls are added)
- `scripts/check_voter_facing_special_case_overview_stack_inheritance.py` (bounded overview docs such as `242`, `310`, and the entrypoint section of `331` must inherit the current high-risk tail from `docs/355-*` instead of freezing stale local `344–…` summaries; prevents family maps and reading paths from teaching an older control perimeter than the release gate actually enforces)
- `scripts/check_voter_facing_special_case_payload_review_window.py` (rows tagged `special_case_high_risk` must keep the linked payload template's `last_verified_at` parseable, nonfuture, and inside its declared `source_review_window_days` window relative to the release date; prevents stale or impossible verification timestamps from surviving inside otherwise fresh-looking public artifacts)
- `scripts/check_voter_facing_special_case_boundary_portability_checklists.py` (rows tagged `special_case_high_risk` must keep the linked checklist's adjacent-surface boundaries, `305`/`307` lane-change reminders, and no-cross-jurisdiction portability warnings visible in the operator workflow; prevents earlier high-risk scope/portability controls from surviving only in the numbered doc)
- `scripts/check_voter_facing_special_case_surface_doc_current_stack_pointer.py` (rows tagged `special_case_high_risk` must keep an explicit pointer back to the canonical current control-stack map in `docs/355-*`; prevents actual numbered high-risk surface docs from acting as stale local entrypoints after later tail controls are added)
- `scripts/check_voter_facing_special_case_current_stack_range_labels.py` (bounded maintainer docs that spell out the current special-case control-tail range must match the canonical live `344–361` perimeter from `docs/355-*`; prevents one-revision-old current-range labels from surviving in current entrypoints after newer tail controls land)
- `scripts/check_packet_verification_report_linkage.py` (drift firewall: `observer_verify_packet.py` must emit `verifier_report_tbs_digest` when requested; exercised through the bounded in-process CLI harness from `docs/658-*`)
- `scripts/check_packet_verification_report_emit_packet.py` (drift firewall: `observer_verify_packet.py --emit-evidence-object` MUST ship the pinned policy profile object and repeat its digest on the envelope subject; exercised through the bounded in-process CLI harness from `docs/658-*`)
- `scripts/check_size_budget.py` (reject accidental archive bloat)
- `scripts/check_no_hedging_in_public_templates.py` (drift firewall: avoid hedge-language in public-facing templates; require explicit epistemic tags instead)

Registry reference: the canonical CSV registries live under `artifacts/registries/` and are documented in `artifacts/registries/README.md`.

### B. Schema integrity
- `scripts/validate_schemas.py` (schema meta-validation; validates a small set of ship examples when `jsonschema` is available)
- `scripts/gen_schema_catalog.py` (catalog updated)
- `scripts/gen_public_surface_index.py` (public surfaces index updated)
- `scripts/gen_example_packets_index.py` (generated compact index of shipped example packets)
- `scripts/gen_external_sources_index.py` (generated no-URL index of external source lockfile IDs)
- `scripts/gen_evidence_object_catalog.py` (evidence object catalog updated)
- `scripts/check_verifier_problem_codes_registry.py` (verifier problem-code registry is strict + sorted)
- `scripts/check_surface_anomaly_codes_registry.py` (surface anomaly-code registry is strict + sorted)
- `scripts/check_verifier_profiles_registry.py` (verifier profile registry is strict + sorted)
- `scripts/gen_verifier_profiles.py` (publishable verifier profile list updated)
- `scripts/gen_verifier_problem_codes.py` (publishable verifier problem-code list updated)
- `scripts/gen_surface_anomaly_codes.py` (publishable surface anomaly-code list updated)

### C. Source pinning integrity
- `scripts/check_external_sources_lockfile.py` (lockfile hygiene + verify `source:`/`xref:` citations resolve across repo markdown surfaces; fail if any `source:` cites an unpinned external source)
- `scripts/check_recent_backticked_lockfile_citations.py` (bounded seam-closure for recent maintainer entrypoints + the current canonical special-case control stack when those docs use backticked `xref:`/`source:` citations; prevents the newest control tail from looking lockfile-backed while silently bypassing citation coverage because the checker target list went stale)
- `scripts/check_track_a_pinned_sources.py` (Track A docs: any `source: <id>` MUST be pinned; use `xref: <id>` for unpinned/informative refs)
- `scripts/check_unused_sources.py` (fail if any lockfile source id is unused across repo markdown; keeps the lockfile lean without forcing duplicate citations)
- `scripts/verify_external_sources_lock.py` (lockfile entries parse; sha256 verified when local copy exists)

### D. Evidence-reference integrity
- `scripts/validate_artifact_refs.py` verifies that references in:
  - `artifacts/claims/claim-evidence-matrix.csv`
  - `artifacts/hazards/hazard-register.csv`
  resolve to real files.

### E. Manifest integrity
- `scripts/build_manifest.py` regenerates `MANIFEST.sha256`
  - excludes `evidence/cache/` and `dist/` (local caches and release outputs)
- `scripts/check_release_path_policy.py` MUST pass so manifest/ZIP/extraction member paths stay unambiguous, traversal-safe, extraction-tree-shape-safe, and portable across common case-insensitive and Windows-style extraction targets; unsafe non-local-only filesystem paths must fail closed rather than act as an implicit exclusion mechanism
- `scripts/check_release_control_files.py` MUST pass so `VERSION` and `MANIFEST.sha256` use canonical LF-only bytes and tolerant CRLF/whitespace-normalized or leading-zero version variants cannot verify
- `scripts/check_release_builder_filesystem_policy.py` MUST pass so manifest check/write uses raw bytes, builders reject unsafe governed paths, release-scope symlinks, or special files before hashing/packaging, and release ZIP construction rejects ambiguous or symlink-routed output/source routes and source-member ancestry swaps before publication
- `scripts/check_release_packaging_alignment.py` MUST pass so the deterministic ZIP payload equals the manifest payload plus `MANIFEST.sha256`
- `scripts/check_release_zip_verifier.py` MUST pass so the release ZIP artifact verifier accepts a freshly built archive, preserves a canonical raw input-path boundary, binds verification to a single input-byte snapshot, and rejects known-bad filename-version-token, member, path, portable-namespace, extraction-shape, mode, central-directory, byte-layout, and compression-method/canonical-rebuild probes
- `scripts/check_release_safe_extractor.py` MUST pass so the operator-facing extractor verifies before extraction, writes accepted members through no-follow extraction routes where available, rechecks the extracted tree, and preserves local output directories unless clean replacement is explicit
- `scripts/check_release_zip_rebuild_from_extract.py` MUST pass so the archive rebuilds byte-for-byte after stdlib extraction
- `MANIFEST.sha256` MUST match the working tree

## 162.2 Suggested evidence lanes (optional but recommended)
- “Adversary simulation” lane for partition / split-world / censorship drills
- “Publication deadline” lane for MMD-style evidence delivery
- “Observer kit offline verification” lane
- **Surface-focused external review** lane (at least one per release cycle): run `artifacts/checklists/external-review-session-checklist.md` against one high-risk surface and log the session (bounded refs/digests) in `artifacts/registries/external-review-log.csv`.

## 162.3 A minimal CI recipe (copy/paste friendly)

One-command gate (authoritative step list lives in the script):

```bash
python3 scripts/release_gate.py
```

To regenerate the manifest (for maintainers when cutting a release ZIP):

```bash
python3 scripts/release_gate.py --write-manifest
```

## 162.4 When a check fails
Treat failures as **drift alerts**:
- open an ADR if the failure reflects a real policy change
- otherwise fix the artifact so the archive remains self-consistent


## 162.5 Evidence packet publishing (recommended)
When preparing a public bundle for an election or drill:
- build a content-addressed packet and manifest using `tools/evidence_packager.py` (see `docs/173`)
- publish a coverage report using `tools/coverage_accounting.py` (see `docs/174`)
- run MAPT on the public pointer surfaces you intend third parties to use, and log the outcome (bounded refs/digests) in `artifacts/registries/mapt-evaluations.csv` (`docs/187`)
- for authenticity/rumor-control readiness, ensure a recent measured TTR evaluation is logged (drill or incident) in `artifacts/registries/time-to-refute-evaluations.csv` (`docs/240`)

These steps are not required for *every* repo release tag, but they are required for any claim of “court-usable evidence package”.

## 162.6 Deterministic release archives (recommended)
When publishing this repository as a ZIP, prefer a deterministic build so releases are reproducible
(stable file order + stable timestamps).

```bash
python3 scripts/build_release_zip.py
```

This writes `dist/The-Election-Stack_<VERSION>.zip`, rejects ambiguous or symlink-routed output paths before publication, and excludes known non-normative cache paths. The release gate now checks that this ZIP-selection scope cannot drift away from manifest-selection scope (see `docs/658-*`) and that the resulting ZIP artifact can be independently verified against its in-archive manifest (see `docs/659-*`). Manifest generation and extracted-tree manifest verification hash governed members through no-follow member-route readers where available, aligning manifest hash reads with ZIP builder source-member reads.
After building the archive, verify the ZIP artifact itself before publishing it:

```bash
python3 scripts/verify_release_zip.py dist/The-Election-Stack_<VERSION>.zip
```

For verifier-backed extraction into a local tree:

```bash
python3 scripts/extract_release_zip.py dist/The-Election-Stack_<VERSION>.zip election-stack-<VERSION>
```

For an already extracted tree, verify manifest closure directly:

```bash
python3 scripts/verify_manifest.py .
```

This checks archive-member safety, extraction tree-shape consistency, deterministic ZIP metadata, raw local/central-directory layout, filename/version agreement when present, lexical verifier input-path canonicality, canonical LF-only `VERSION`/`MANIFEST.sha256` control-file bytes, single-snapshot input-byte binding for hash/parser/layout/manifest/rebuild checks, in-ZIP `MANIFEST.sha256` closure over every non-manifest entry, stored-member compression-method enforcement, byte-for-byte canonical ZIP rebuild from sealed member payloads, manifest/extracted-tree hash reads through no-follow member routes where available, manifest-builder source-root lexical/symlink-route preflight, `MANIFEST.sha256` control-file read/write route canonicality, safe-extractor member-write no-follow routing, safe-extractor temporary-root and output-parent publish-route identity checks, extracted-tree canonical `0644` file-mode checks, extracted-tree canonical `0755` release-directory and directory-closure checks, and extracted-tree closure after safe extraction.

## v823 safe-extractor output-parent publish route identity note

Safe extraction now captures the output parent directory as an identity-bearing publication boundary. `scripts/extract_release_zip.py` rechecks that parent route before and after the major extraction/publish stages, routes output cleanup through the pinned parent where available, and performs final publication through the pinned parent descriptor where supported. A swap of the output parent route now fails before any verified tree is published; see `docs/698-release-safe-extractor-output-parent-publish-route-identity-firewall.md`.

## v822 safe-extractor temporary-root publish identity note

Safe extraction now captures the temporary extraction root as an identity-bearing boundary. `scripts/extract_release_zip.py` rechecks the same temporary directory before member writes, after member copy, after directory-mode canonicalization, after extracted-tree manifest verification, after output cleanup, before final rename, and after publication. A post-verification swap of the temporary root now fails before any output path is published; see `docs/697-release-safe-extractor-temp-root-publish-identity-firewall.md`.

## v821 safe-extractor member-write openat note

Safe extraction now writes verified ZIP members through concrete extraction-directory routes. `scripts/extract_release_zip.py` rechecks each accepted member name, creates or opens member parent components with directory descriptors and `O_NOFOLLOW` where available, creates leaf files with exclusive create plus `O_NOFOLLOW` where available, and confirms created leaves are regular files before copying bytes. A swapped member-directory symlink now fails extraction without writing release bytes into the symlink target; see `docs/696-release-safe-extractor-member-write-openat-firewall.md`.

## v820 manifest control-file read/write canonicality note

Manifest maintenance now applies a concrete route boundary to `MANIFEST.sha256` itself. `scripts/build_manifest.py --check` refuses symlinked or non-regular manifest control-file targets, reads the manifest through the no-follow route-aware helper where available, and rechecks identity/size after consuming the byte stream. Manifest regeneration writes a temporary sibling under the accepted parent route, rechecks the final target immediately before replacement, and fails closed if a final-path symlink or non-regular swap appears. This aligns the control file that defines archive hash closure with the v817 member-read and v819 source-root firewalls; see `docs/695-release-manifest-control-file-read-write-canonicality-firewall.md`.

## v819 manifest builder source-root canonicality note

Manifest generation now preflights its source root before walking the tree or hashing any governed member. `scripts/build_manifest.py` records its module root as an absolute lexical path rather than a symlink-resolved path, rejects empty/NUL roots, current-directory and parent-directory components, repeated separators, trailing separators, non-directory roots, final-root symlinks, and symlinked ancestry, then keeps the v817 no-follow member-reader discipline for each selected file. This aligns manifest construction with the release ZIP builder source-root firewall and the extracted-tree verifier root firewall; see `docs/694-release-manifest-builder-source-root-canonicality-firewall.md`.

## v818 manifest verifier root lexical canonicality note

Extracted-tree verification now rejects ambiguous explicit verification-root spellings before root existence, symlink, mode, walk, or hash checks run. `scripts/verify_manifest.py` fails closed on empty or NUL-containing roots, current-directory or parent-directory components, repeated separators, and trailing separators; omitted-root CLI use still resolves to the concrete current working directory. This aligns recipient-side manifest verification with the release ZIP input, safe-extractor output, builder output, builder source-root, and manifest member-read path firewalls; see `docs/693-release-manifest-verifier-root-lexical-canonicality-firewall.md`.

## v817 manifest member-read canonicality note

Manifest generation and extracted-tree manifest verification now hash governed members through the same no-follow member-route discipline used by the release ZIP builder. `scripts/build_manifest.py` opens each manifest member's parent route with directory descriptors where available, rejects final-path symlinks and non-regular leaves, and checks identity/size stability while hashing; `scripts/verify_manifest.py` uses that same helper for recipient-side hash verification. Leaf and parent symlink-swap probes cover both construction and extracted-tree verification; see `docs/692-release-manifest-member-read-canonicality-firewall.md`.

## v816 ZIP builder source-member ancestry note

Release ZIP construction now reopens selected source-member parent routes with no-follow directory-descriptor routing where available before reading the leaf file. `scripts/build_release_zip.py` walks the accepted source root and each parent component before opening the final member, so a parent-directory symlink swap after discovery fails closed rather than redirecting packaged bytes; see `docs/691-release-zip-builder-source-member-ancestry-openat-firewall.md`.

## v815 ZIP builder source-member read note

Release ZIP construction now avoids resolving source members for output-artifact exclusion and rechecks every selected source member immediately before writing it into the ZIP. `scripts/build_release_zip.py` skips only the exact lexical output path, rejects governed symlink output aliases as source-scope symlinks, opens source members with final-path no-follow behavior where available, and rejects identity/size drift while reading; see `docs/690-release-zip-builder-source-member-read-canonicality-firewall.md`.

## v814 ZIP builder source-root note

Release ZIP construction now mirrors the verifier/extractor path boundary for both artifact publication and source-tree selection. `scripts/build_release_zip.py` rejects empty, NUL-containing, current-directory, parent-directory, repeated-separator, trailing-separator, missing, non-directory, symlink-final, and symlink-ancestry source roots before release member discovery; see `docs/689-release-zip-builder-source-root-canonicality-firewall.md`.

## v813 ZIP builder output-path note

Release ZIP construction now mirrors the verifier/extractor path boundary for artifact publication. `scripts/build_release_zip.py` rejects empty, NUL-containing, current-directory, parent-directory, repeated-separator, trailing-separator, symlink-final, symlink-ancestry, and existing non-regular output paths before publishing a release ZIP. The builder writes into a temporary sibling file and rechecks the output route immediately before `os.replace()`; see `docs/688-release-zip-builder-output-path-canonicality-firewall.md`.


## v803 extracted-tree directory closure note

Extracted-tree verification now rejects release-scope directories below the tree root unless they are implied by `MANIFEST.sha256` paths and have canonical `0755` mode. The safe extractor normalizes release directories before its post-extraction verifier run; see `docs/678-release-extracted-tree-directory-closure-and-mode-canonicality-firewall.md`.

## v802 extracted-tree file-mode canonicality note

Extracted-tree verification now rejects release-scope files whose filesystem mode is not canonical `0644`. This keeps `scripts/verify_manifest.py` aligned with the ZIP verifier's member-mode checks and the official safe extractor's output mode normalization; see `docs/677-release-extracted-tree-file-mode-canonicality-firewall.md`.

## v800 safe-extractor side-effect-free preflight note

The official safe extractor now runs its lexical/symlink output-target firewall before creating any output parent directory. Rejected output targets therefore do not leave redirected local parent directories behind; see `docs/675-release-safe-extractor-side-effect-free-output-preflight.md`.

## v799 safe-extractor output ancestry note

The official safe extractor now rejects output targets that traverse existing symlink parent components or lexical `.`/`..` components, and it repeats that output-ancestry check immediately before publication. This keeps verified release bytes from being redirected through an ambiguous local output path; see `docs/674-release-safe-extractor-output-ancestry-firewall.md`.

## v798 governed-path closure note

Release tooling now separates explicit local-only paths from governed release paths. Unsafe governed names such as whitespace-bearing files under `docs/` fail manifest/ZIP builders and extracted-tree verification instead of being silently omitted from release scope; see `docs/673-release-governed-path-closure-and-unsafe-local-file-firewall.md`.

## v797 builder byte-exact manifest note

Release construction now mirrors verifier strictness for control-file bytes and filesystem node types. `scripts/build_manifest.py --check` compares raw `MANIFEST.sha256` bytes instead of text-normalized strings, manifest writes are exact LF-only bytes, and manifest/ZIP builders reject release-scope symlinks or special files before hashing or packaging; see `docs/672-release-builder-byte-exact-manifest-and-file-type-firewall.md`.

## v796 extraction tree-shape conflict note

Release archives now reject member sets where a regular-file path is also a component-prefix of another member path, such as `objects/prefix` and `objects/prefix/child.json`. This keeps archive verification, manifest parsing, safe extraction, and extracted-tree verification aligned on a portable regular-file tree shape; see `docs/671-release-extraction-tree-shape-conflict-firewall.md`.

## v801 ZIP stored-member canonicality note

Release archives now use `ZIP_STORED` members rather than DEFLATE, so byte-for-byte archive canonicality no longer depends on local compressor output. `scripts/verify_release_zip.py` rejects deflated members, requires stored member sizes to match payload sizes, and still rebuilds the ZIP byte stream from sealed in-archive payloads for exact comparison; see `docs/676-release-zip-stored-member-compressor-independent-canonicality.md`.

## v795 ZIP deflate-stream canonicality note

`docs/670-release-zip-deflate-stream-canonicality-and-verifier-rebuild.md` introduced verifier-side canonical rebuilds to catch alternate legal deflate streams. v801 supersedes the compression portion of that rule by using stored members, while preserving the byte-for-byte rebuild requirement.


## v794 control-file canonicality note

Release archives now share one byte-strict parser for `VERSION` and `MANIFEST.sha256`; CRLF, surrounding-whitespace, duplicate, unsorted, or otherwise non-canonical control-file variants fail both ZIP-artifact and extracted-tree verification. See `docs/669-release-control-file-byte-canonicality-and-crlf-firewall.md`.

## v793 safe-extractor note

Release archives now ship `scripts/extract_release_zip.py`, a verifier-backed two-phase extractor that verifies the ZIP before writing, extracts into a temporary sibling directory through the shared path policy, rechecks the extracted tree with `scripts/verify_manifest.py`, and only then publishes the output directory; see `docs/668-release-safe-extractor-verified-two-phase-unpack-and-tree-recheck.md`.

## v792 extracted-tree manifest note

Extracted release trees now ship a strict `scripts/verify_manifest.py` verifier and a release-gate smoke/negative-probe check; see `docs/667-release-manifest-tree-verifier-and-symlink-safe-hash-closure.md`.

## v791 release-gate cleanup note

Post-step process cleanup is scoped to child process-group/session members rather than a broad post-exit `killpg` probe; see `docs/666-release-gate-post-step-cleanup-scoping-and-pid-namespace-safety.md`.

## v804 extraction-root mode canonicality note

Extracted-tree verification now includes the publication root directory itself in the mode-canonicality contract. `scripts/verify_manifest.py` rejects a release tree whose root mode is not `0755`, even if every manifested file hash and child-directory mode is correct.

`scripts/extract_release_zip.py` normalizes the temporary extraction root to `0755` before the post-extraction manifest verifier runs and before final publication, so verifier-backed extraction produces a tree accepted by the recipient-side manifest verifier without depending on local `tempfile.mkdtemp()` mode defaults.

Release-gate smoke coverage for this surface lives in `scripts/check_manifest_verifier.py` and `scripts/check_release_safe_extractor.py`.

## v805 extracted-tree verification-root anchoring note

Extracted-tree verification now rejects a symlinked verification root before resolving or walking the tree. `scripts/verify_manifest.py` must prove that the operator-named root is a concrete release tree boundary, not a symlink alias for another directory that happens to verify. The safe extractor already rejects symlink output roots and symlink-routed ancestry; v805 aligns the standalone verifier with that recipient-side publication contract. See `docs/680-release-extracted-tree-verification-root-anchoring-firewall.md`.

The official safe extractor now inspects the raw operator-supplied output string before constructing a `Path`, so lexical `./` components, empty separator components such as `//`, and filesystem-root targets are rejected before output-parent creation. This closes the normalization gap where `pathlib` could hide a non-canonical publication route before the extractor's ancestry firewall ran. See `docs/681-release-safe-extractor-lexical-output-path-canonicality-firewall.md`.
