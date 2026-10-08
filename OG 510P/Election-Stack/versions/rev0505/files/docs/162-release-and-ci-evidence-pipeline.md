# 162 — Release gates and CI evidence pipeline

**Track:** Shared


This doc defines a **minimum release gate** for this archive so it does not silently drift under
human or LLM edits.

The gate is intentionally boring: it enforces that artifacts remain **internally consistent** and
that external references do not change without notice.

## 162.1 Required checks (MUST pass for any release tag)

Canonical step order is defined by `scripts/release_gate.py` (treat it as authoritative to avoid doc drift).

### A. Structure + index integrity
- `scripts/check_index.py` (numbered docs must be indexed)
- `scripts/check_doc_number_collisions.py` (fail if a numbered doc ID collides without a tombstone alias)
- `scripts/check_tracks.py` (every numbered doc declares a Track)
- `scripts/check_adr_index.py` (ADR drift firewall: every ADR file is indexed and has Status/Date; prevents silent decision drift)
- `scripts/gen_track_bundles.py` (curated bundle entrypoints must resolve; no broken links)
- `scripts/check_doc_links.py` (relative markdown links must resolve; prevents quiet link-rot)
- `scripts/check_doc_backtick_refs.py` (drift firewall: backticked numbered-doc references must resolve; catches filename typos that aren't links)
- `scripts/check_no_raw_urls_modern_docs.py` (for docs >=170, require `source:` citations instead of raw external URLs)
- `scripts/check_no_forbidden_example_tlds.py` (drift firewall: prevent misleading `example` placeholders under restricted TLDs; see `231`)
- `scripts/check_no_cache_artifacts.py` (fail if __pycache__/pyc, `dist/`, or evidence/cache payloads are present)
- `scripts/check_no_symlinks.py` (fail if any symlinks are present; prevents non-portable bundles and symlink escape reads)
- `scripts/check_tool_maturity_registry.py` (drift firewall: every tool file is classified as operator/research/skeleton/library; prevents accidental misuse)
- `scripts/check_registries_readme.py` (drift firewall: registries README must list every `artifacts/registries/*.csv`; prevents silent surface drift)
- `scripts/check_envelope_kinds.py` (example EvidenceEnvelope kinds must be registered)
- `scripts/check_doc_envelope_kind_references.py` (doc references using `kind:` / `Envelope kind:` must refer to registered kinds)
- `scripts/check_envelope_payload_schemas.py` (envelope kinds must point to real schemas)
- `scripts/check_attachment_requirements.py` (required receipt/gossip attachments per kind)
- `scripts/check_attachment_registry_integrity.py` (attachment requirements registry must reference known kinds and existing schemas; no duplicate kind+rel rows)
- `scripts/check_example_packets.py` (example evidence packets must verify offline; prevents rot)
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
- `scripts/check_results_hash_vectors.py` (drift tripwire for results-object TBS hashing + RESULTS-leaf payload hashing; see `235–236`)
- `scripts/check_compact_context_vectors.py` (drift tripwire for compact `req[]/vary[]/age[]` request-context notes; see `DOC:docs/232-compact-request-context-notes.md`)
- `scripts/check_envelope_vectors.py` (drift tripwire for EvidenceEnvelope payload/tbs digests)
- `scripts/check_version_consistency.py` (VERSION/CHANGELOG/START_HERE must agree)
- `scripts/check_recent_changelog_version_sequence.py` (recent changelog head must descend contiguously by version; catches silently skipped release notes near the current tip)
- `scripts/check_voter_facing_surface_anchor_lock_coverage.py` (promoted voter-facing family-tail docs must keep lockfile-backed official source anchors; prevents free-floating prose promotions without pinned official citations)
- `scripts/check_voter_facing_surface_structure_minimums.py` (promoted voter-facing family-tail docs and any newer `special_case_high_risk` rows below `323` must keep the standard bounded-surface section shape; prevents half-formed promotions that lose fallback/freshness/verification structure)
- `scripts/check_voter_facing_special_case_release_freshness.py` (rows tagged `special_case_high_risk` must keep at least two lockfile-backed official anchors reviewed within 90 days of the archive's release date; prevents shipping time-volatile edge-case voter surfaces with only stale official examples)
- `scripts/check_voter_facing_special_case_official_routing_precedence.py` (rows tagged `special_case_high_risk` must say that the current official state/local election-office source controls and that national/archive summaries are routing aids rather than substitutes; prevents well-sourced edge-case docs from reading like generalized national answers)
- `scripts/check_voter_facing_special_case_current_state_visibility.py` (rows tagged `special_case_high_risk` must say how to identify the current controlling official notice or instruction when older pages, PDFs, screenshots, packet inserts, or archive summaries remain visible; prevents high-risk edge-case docs from sounding current while leaving superseded material unresolved)
- `scripts/check_voter_facing_special_case_unresolved_conflict_stop.py` (rows tagged `special_case_high_risk` must say that unresolved conflicting official materials are a stop condition and that readers should not synthesize a controlling answer from fragments; prevents high-risk edge-case docs from bluffing past unresolved official disagreement instead of routing to current authoritative confirmation)
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
- `scripts/check_packet_verification_report_linkage.py` (drift firewall: `observer_verify_packet.py` must emit `verifier_report_tbs_digest` when requested)
- `scripts/check_packet_verification_report_emit_packet.py` (drift firewall: `observer_verify_packet.py --emit-evidence-object` MUST ship the pinned policy profile object and repeat its digest on the envelope subject)
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
- `scripts/gen_verifier_problem_codes.py` (publishable verifier problem-code list updated)

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

This writes `dist/The-Election-Stack_<VERSION>.zip` and excludes known non-normative cache paths.
