# Archive hygiene (how we avoid a monster)

This repo must grow over time, but not explode.

## Rules

1) Prefer **RFCs** for proposals, then accept via **ADRs**.
2) Keep docs small:
   - “one concept per file”
   - link out to RFCs/ADRs instead of duplicating content
3) Any new subsystem must pass the **design review rubric** (copy the template into the RFC):
   - contract surface (typed, digest-bound)
   - authority changes (attenuation + revocation + diff surfaces)
   - threat model impact + trust boundaries
   - failure modes + rollback behavior
   - evidence outputs + retention budget

See: `docs/348-design-review-rubric-and-feature-intake.md`.

4) Add references as links; avoid copying external text.
5) When a topic becomes stale, move it to `docs/attic/` and leave a one-line pointer.

## Checks

- Quick path: `python3 tools/hygiene.py` runs the lightweight checks below in one go.
- Sanitized-inspection-derivative boundary guardrail: `python3 tools/check_workstation_sanitized_derivative_boundary.py` will keep sanitized inspection derivatives inspection-shaped and disposable-first, prevent sanitizer success from silently becoming persistent-viewer trust promotion, and keep the working-copy / route examples joined to that boundary.
- This is the workstation sanitized-inspection-derivative boundary: keep the archive teaching one exact answer instead of letting conversion convenience drift into authority.
- sanitized-ocr boundary guardrail: `python3 tools/check_workstation_sanitized_ocr_boundary.py` will keep flat visual sanitized output as the boring default, keep searchable/OCR reconstruction explicit and secondary, and prevent OCR/searchable derivatives from silently entering the baseline working-copy lane.
- sanitized-ocr ambient-index boundary guardrail: `python3 tools/check_workstation_sanitized_ocr_index_boundary.py` will keep local viewer search bounded to the inspection lane, forbid ambient host/global indexing by default, and prevent detached text sidecars from quietly becoming the real searchable artifact.
- OCR text-egress boundary guardrail: `python3 tools/check_workstation_ocr_text_egress_boundary.py` will keep copied OCR-derived text on the explicit plain-text single-delivery data-transfer lane and preserve the `ui.datatransfer.*.content_source` provenance join instead of ambient clipboard/export folklore.
- Workstation data-transfer offer-source/recipient exactness guardrail: `python3 tools/check_workstation_datatransfer_subject_exactness.py` will keep `ui.datatransfer.*` evidence naming both the exact `offer_source_subject` and the current `subject` instead of reopening broker-memory/source-guessing folklore.
- Workstation data-transfer grant-digest join guardrail: `python3 tools/check_workstation_datatransfer_grant_digest_join.py` will keep `ui.datatransfer.receipt` carrying exact `grant_digest`, so detached support/export can join a transfer back to the exact reviewed grant artifact instead of reconstructing policy from `offer_id` / `lease_id` folklore.
- Workstation data-transfer single-delivery exhaustion guardrail: `python3 tools/check_workstation_datatransfer_single_delivery_exhaustion.py` will keep the ordinary workstation transfer lane one-shot, require `grant_exhausted`, and prevent successful single-delivery grants from silently gaining replay/history recovery semantics.
- Workstation data-transfer effective-until guardrail: `python3 tools/check_workstation_datatransfer_effective_until.py` will keep ordinary transfer grants carrying exact `effective_until`, keep late delivery fail-closed, and stop lifetime drift back into TTL/expiry/broker folklore.
- Workstation data-transfer renewal-lineage guardrail: `python3 tools/check_workstation_datatransfer_renewal_lineage.py` will keep reviewed retry/re-offer successor-shaped, require `renewal_posture`, and stop continuity drift back into offer-id/lease-id or in-place-extension folklore.
- Workstation data-transfer successor-scope guardrail: `python3 tools/check_workstation_datatransfer_successor_scope.py` will keep reviewed successor grants carrying `successor_scope_posture`, keep successor continuity same-actor-pair and no-wider-offer, and stop retry wording from hiding widened MIME/byte/source/destination scope.
- Workstation data-transfer successor payload-lineage guardrail: `python3 tools/check_workstation_datatransfer_successor_payload_lineage.py` will keep reviewed successor grants preserving payload lineage and redaction posture exactly, and stop retry wording from hiding `content_source` / `redaction_profile_digest` swaps.
- Workstation data-transfer successor payload-digest guardrail: `python3 tools/check_workstation_datatransfer_successor_payload_digest.py` will keep reviewed successor grants exact-payload-bound, require successor `offer.payload_digest`, and stop semantic-equivalence rebinding or payload-digest drift from hiding behind retry wording.
- Workstation data-transfer successor-foreground guardrail: `python3 tools/check_workstation_datatransfer_successor_foreground.py` will keep reviewed successor grants preserving exact `constraints.requires_foreground`, and stop foreground-visible reviewed transfer from quietly becoming background-capable retry authority.
- Removable-media local-fallback preserved-capture guardrail: `python3 tools/check_removable_media_local_preserved_capture.py` will keep the first removable-media lane preserving the verified capture as exact evidence, forbid later sanitize/convert work from rewriting that capture in place, and keep the canonical receipt naming the sanitized output as a separate derivative from the preserved capture.
- Removable-media local-fallback authoritative-store guardrail: `python3 tools/check_removable_media_local_authoritative_store.py` will keep the first removable-media lane from leaving preserved-capture authority in disposable `/work`, require authoritative quarantine-store commit before detach, and keep later work reading a read-only projection of the stored preserved capture.
- Removable-media local-fallback single-object projection guardrail: `python3 tools/check_removable_media_local_single_object_projection.py` will keep the first removable-media lane from widening post-detach delivery into a browseable authoritative-store namespace, require a single-object projection/handle shape for later work, and keep the authoritative locator receipt-visible rather than worker-browseable.
- Removable-media local-fallback projection digest-binding guardrail: `python3 tools/check_removable_media_local_projection_digest_binding.py` will keep the first removable-media lane from treating a synthetic worker path as self-authenticating, require later delivery to match the preserved capture digest before later ops begin, and keep the canonical receipt recording that binding explicitly.
- Removable-media local-fallback preopened-delivery guardrail: `python3 tools/check_removable_media_local_preopened_delivery.py` will keep the first removable-media lane from drifting back into path-reopen folklore after digest binding, require later execution to stay on one launcher-preopened read-only object (or equivalent), and keep the worker-visible path compatibility-only rather than execution authority.
- Removable-media local-fallback derivative-egress guardrail: `python3 tools/check_removable_media_local_broker_collected_output.py` will keep the first removable-media lane from treating `/work/output/...` as authoritative derivative identity, require later output to leave through launcher-prepared disposable sink objects, and keep authoritative derivative naming on broker collection + remeasurement instead of worker scratch folklore.
- Removable-media local-fallback single-declared-derivative-slot guardrail: `python3 tools/check_removable_media_local_single_declared_derivative_slot.py` will keep the first removable-media lane on one declared writable derivative slot, require any receipt-visible derivative to come from that slot, and keep extra worker result surface out of the first cut.
- Removable-media local-fallback empty-writeonly-derivative-slot guardrail: `python3 tools/check_removable_media_local_empty_writeonly_derivative_slot.py` will keep the first removable-media lane from treating that one declared sink like mutable scratch, require it to start empty, and keep worker readback/truncate out before broker collection.
- Removable-media local-fallback append-open-derivative-slot guardrail: `python3 tools/check_removable_media_local_append_open_derivative_slot.py` will keep the first removable-media lane from quietly lying about seekable-file delivery on FreeBSD: the sink must be handed over `O_APPEND`, stay append-only-protected while the worker runs, keep `CAP_READ`/`CAP_FTRUNCATE`/`CAP_FCNTL` out, and treat any `CAP_SEEK` there as ballast rather than rewrite authority.
- Removable-media local-fallback capability-mode-entry guardrail: `python3 tools/check_removable_media_local_capability_mode_entry.py` will keep the first removable-media lane from quietly treating capability-mode entry as optional launcher folklore: the launcher or its approved shim must enter capability mode before handing control to later tool code, descendants inherit that mode and may not clear it, ambient absolute-path opens stay out after `cap_enter()`, and tools that cannot run on the preopened capability set stay out unless a later explicit wrapper/broker contract earns them.
- Workstation data-transfer successor-delivery-mode guardrail: `python3 tools/check_workstation_datatransfer_successor_delivery_mode.py` will keep reviewed successor grants preserving exact `delivery_mode`, and stop one-shot reviewed transfer from quietly becoming multi-delivery retry authority.
- Workstation data-transfer successor-rate-limit guardrail: `python3 tools/check_workstation_datatransfer_successor_rate_limit.py` will keep reviewed successor grants preserving exact `constraints.rate_limit`, and stop old-story retry from quietly changing throttling posture.
- Workstation data-transfer successor-expires-at guardrail: `python3 tools/check_workstation_datatransfer_successor_expires_at.py` will keep reviewed successor grants preserving exact `constraints.expires_at`, and stop old-story retry from quietly changing the reviewed outer absolute-expiry ceiling.
- Workstation data-transfer constraints-closed-world guardrail: `python3 tools/check_workstation_datatransfer_constraints_closed_world.py` will keep ordinary `ui.datatransfer.grant.constraints` closed-world, typed, and free of hidden extra `constraints.*` posture.
- Removable-media local-fallback executable-identity guardrail: `python3 tools/check_removable_media_local_executable_identity.py` will keep the post-detach later worker on a launcher-resolved digest-pinned executable, require receipt-visible executable/wrapper digests, and keep path search plus implicit helper/plugin discovery out of the first cut.
- Removable-media local-fallback runtime-dependency guardrail: `python3 tools/check_removable_media_local_runtime_dependency_closure.py` will keep the post-detach later worker on a launcher-pinned runtime dependency closure, require receipt-visible closure digests, and keep ambient loader path search out of the first cut.
- Removable-media local-fallback worker-lifecycle guardrail: `python3 tools/check_removable_media_local_worker_lifecycle.py` will keep the post-detach later worker launcher-supervised and daemon-free, require worker exit plus whole-tree reap before derivative receipt authority, and keep background descendants or unreviewed subprocesses out of the first cut.
- Removable-media local-fallback closed-world-descriptor-set guardrail: `python3 tools/check_removable_media_local_closed_world_descriptor_set.py` will keep the post-detach later worker on a reviewed closed-world descriptor set, require the launcher to close or spawn-closefrom every non-reviewed descriptor before handoff, keep `stdin` inert null/empty input only, and keep `stdout`/`stderr` launcher-owned observation channels or reviewed append-only log sinks rather than inherited parent-session surfaces.
- Workstation data-transfer baseline-frozen guardrail: `python3 tools/check_workstation_datatransfer_baseline_frozen.py` will keep the ordinary portable transfer lane frozen, complete enough to implement, and RFC-first for richer widened/substituting/broader lanes instead of quiet baseline drift.
- Workstation data-transfer distinct-family-split guardrail: `python3 tools/check_workstation_datatransfer_distinct_family_split.py` will keep future richer workstation transfer lanes from quietly reusing ordinary `ui.datatransfer.grant` / `ui.datatransfer.receipt`, so any richer lane must arrive as a distinct artifact family with its own schemas/examples/wiring.
- Workstation data-transfer first-richer-RFC-target guardrail: `python3 tools/check_workstation_datatransfer_first_richer_rfc_target.py` will keep the next richer-lane queue pointed at the reviewed finite collection handoff RFC, so archive pressure does not reopen the frozen ordinary baseline or jump straight to persistent directory authority.
- Workstation data-transfer collection-readonly-first guardrail: `python3 tools/check_workstation_datatransfer_collection_readonly_first.py` will keep the first richer finite-collection cut read-only only, so writable receive cannot quietly linger inside `RFC-0194` after the archive has pushed that mutation pressure into a separate later decision.
- Workstation data-transfer finite-collection-autostop guardrail: `python3 tools/check_workstation_datatransfer_finite_collection_autostop.py` will keep the first richer finite-collection handoff cut single-retrieve by default and auto-stopping after the first successful retrieve instead of drifting into repeated-retrieve convenience folklore.
- Workstation data-transfer collection-snapshot-posture guardrail: `python3 tools/check_workstation_datatransfer_collection_snapshot_posture.py` will keep selected directories in the first richer finite-collection handoff lane snapshot-shaped and non-live, preventing drift into quiet tree-traversal authority.
- Workstation data-transfer collection-manifest-posture guardrail: `python3 tools/check_workstation_datatransfer_collection_manifest_posture.py` will keep the first richer finite-collection handoff manifest-first, so reviewed membership stays explicit and tree/collection digests remain supplementary summary evidence instead of becoming the only membership surface.
- Workstation data-transfer collection-member-kind-floor guardrail: `python3 tools/check_workstation_datatransfer_collection_member_kind_floor.py` will keep the first richer finite-collection handoff regular-files-plus-explicit-directories only, so symlink/special-file semantics cannot quietly creep into the first cut.
- Workstation data-transfer collection-manifest-field-floor guardrail: `python3 tools/check_workstation_datatransfer_collection_manifest_field_floor.py` will keep the first richer finite-collection handoff content-identity-first and stat-light, so normalized review path + member kind + payload digest/byte length remain the exact first-cut manifest floor instead of path-only or full-stat folklore.
- Workstation data-transfer collection-manifest-order guardrail: `python3 tools/check_workstation_datatransfer_collection_manifest_order.py` will keep the first richer finite-collection handoff authoritative manifest ordered only by normalized review path in strict ascending bytewise order, locale-independent, and duplicate-path fail-closed rather than traversal/click-order folklore.
- Workstation data-transfer collection-manifest-digest guardrail: `python3 tools/check_workstation_datatransfer_collection_manifest_digest.py` will keep the first richer finite-collection handoff authoritative compact identity bound to `sha256(utf8(JCS(authoritative_manifest)))`, so tree-summary or broker-local hashing folklore does not become the real reviewed-set handle.
- Workstation data-transfer collection-review-path-normalization guardrail: `python3 tools/check_workstation_datatransfer_collection_review_path_normalization.py` will keep the first richer finite-collection handoff using collection-relative clean slash-separated Unicode NFC review paths, reject leading/trailing slash or dot-segment cleanup folklore, and keep normalization collisions fail-closed instead of host/toolkit repaired.
- Workstation data-transfer collection-top-level-names guardrail: `python3 tools/check_workstation_datatransfer_collection_top_level_names.py` will keep the first richer finite-collection handoff using explicit reviewed top-level names, so silent auto-rename or wrapper-root repair cannot drift back in as hidden broker policy.
- Workstation data-transfer collection-ancestor-closure guardrail: `python3 tools/check_workstation_datatransfer_collection_ancestor_closure.py` will keep the first richer finite-collection handoff using an authoritative manifest ancestor-closed, so explicit parent directories remain reviewed structural state and retrieve-time implicit parent synthesis cannot drift back in as hidden materializer policy.
- Workstation data-transfer collection-selected-roots guardrail: `python3 tools/check_workstation_datatransfer_collection_selected_roots.py` will keep the first richer finite-collection handoff using selected roots overlap-free after normalization and reviewed aliasing, so ancestor/descendant root overlap cannot drift back in as silent broker subsumption or hidden review memory.
- Workstation data-transfer collection-fresh-root guardrail: `python3 tools/check_workstation_datatransfer_collection_fresh_root.py` will keep the first richer finite-collection handoff using fresh-rooted retrieve/materialization, so silent merge into an existing tree, overwrite, auto-rename, or same-bytes reuse cannot drift back in as hidden receiver policy.
- Workstation data-transfer collection-result-root-receipt guardrail: `python3 tools/check_workstation_datatransfer_collection_result_root_receipt.py` will keep the first richer finite-collection handoff requiring successful retrieve/materialization receipts to pin the exact created fresh root, so parent-only placement evidence or pathless success prose cannot drift back in as the real result surface.
- Workstation data-transfer collection-placement-hint-posture guardrail: `python3 tools/check_workstation_datatransfer_collection_placement_hint_posture.py` will keep parent chooser, destination label, suggested folder, or save-into prompts receiver-local advisory UI state, so the first richer lane does not quietly turn into sender-directed placement authority.
- Workstation data-transfer collection-result-root-locator-posture guardrail: `python3 tools/check_workstation_datatransfer_collection_result_root_locator_posture.py` will keep successful richer-lane retrieve handle-first, so the exact created fresh root stays joined through a receiver-local stable result-root handle and any display-path snapshot stays advisory instead of becoming mutable-path folklore.
- Workstation data-transfer collection-result-root-display-snapshot-continuity guardrail: `python3 tools/check_workstation_datatransfer_collection_result_root_display_snapshot_continuity.py` will keep any retrieve-frozen advisory display snapshot attached to the original richer-lane retrieve stable when present, so later local rename/move/import/promote state cannot silently rewrite the old human-facing note in place.
- Workstation data-transfer collection-result-root-handle-opacity guardrail: `python3 tools/check_workstation_datatransfer_collection_result_root_handle_opacity.py` will keep the authoritative richer-lane result-root handle opaque and non-path-shaped, so “handle-first” cannot quietly degrade back into a path string or URI with a new field name.
- Workstation data-transfer collection-profile-scope guardrail: `python3 tools/check_workstation_datatransfer_collection_profile_scope.py` will keep the first richer finite-collection handoff scoped to B/C/D, so fleet-host A does not quietly inherit workstation file-ferry semantics by drift.
- Workstation data-transfer collection-example-joins guardrail: `python3 tools/check_workstation_datatransfer_collection_example_joins.py` will keep the first `ui.collection.handoff.*` example stack mechanically aligned, so `collection_digest = sha256(utf8(JCS(authoritative_manifest)))` and receipt `grant_digest = sha256(utf8(JCS(grant_artifact)))` stay real portable joins instead of disconnected placeholders.
- Workstation data-transfer collection-first-impl-aliasing guardrail: `python3 tools/check_workstation_datatransfer_collection_first_impl_aliasing.py` will keep the first implementation fail-closed on top-level basename collisions, so trusted-UI alias/disambiguation UX does not quietly drift back in as hidden reviewed state.
- Workstation data-transfer collection-review-ui-path-compression guardrail: `python3 tools/check_workstation_datatransfer_collection_review_ui_path_compression.py` will keep review-surface compaction bounded to manifest-derived path-compression of deterministic ancestor-only directory runs, so legibility does not quietly become hidden source-breadcrumb or tree-editor authority.
- Workstation data-transfer collection-mime-posture guardrail: `python3 tools/check_workstation_datatransfer_collection_mime_posture.py` will keep the first richer finite-collection handoff path/kind/payload-first, keep advisory MIME optional and non-authoritative, and stop detector/registry folklore from quietly becoming the real reviewed identity surface.
- Workstation reviewed finite-collection current-stack guardrail: `python3 tools/check_workstation_datatransfer_finite_collection_current_stack_contract.py` will keep the dense reviewed finite-collection tightening cluster pointer-backed to `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md`, so nearby docs do not drift into stale partial companion lists once the lane becomes implementation-shaped.
- Workstation data-transfer collection-filesystem-metadata-posture guardrail: `python3 tools/check_workstation_datatransfer_collection_filesystem_metadata_posture.py` will keep owner/group, mode-bit, mtime, xattr, ACL, and similar richer filesystem metadata out of this reviewed lane entirely, keep local materialized metadata receiver-local only, and stop the selected-set handoff from quietly becoming a filesystem-preserving archive format.
- Restore coherence guardrail: `python3 tools/check_restore_boundary.py` will keep restore official and quarantine-first, preventing drift back to “restore is future work” prose or direct-overwrite replacement without typed preconditions.
- Firmware evidence coherence guardrail: `python3 tools/check_firmware_evidence_posture.py` will keep digest-first inventory normal, mutation receipts authoritative, and raw platform material out of routine baseline export.
- Trust-bundle apply coherence guardrail: `python3 tools/check_trust_bundle_apply_boundary.py` will keep `pki-trust-bundle` authoritative, keep `pki.trust.bundle.diff` as the review surface, and keep `pki.trust.bundle.apply.receipt` as the typed proof of the exact trust view a host or unit actually served.
- Trust-bundle apply bundle coherence guardrail: `python3 tools/check_trust_bundle_apply_bundle_contract.py` will keep official incident/support bundles carrying trust-view apply proof through `pki_trust_bundle_apply_receipt_digests` instead of falling back to renderer-specific trust dumps or `extra` folklore.
- PKI-issue bundle coherence guardrail: `python3 tools/check_pki_issue_bundle_contract.py` will keep official incident/support bundles carrying typed PKI issuance proof through `pki_issue_receipt_digests` instead of falling back to CA dashboards, ACME logs, or ticket prose.
- Attestation bundle coherence guardrail: `python3 tools/check_attestation_bundle_contract.py` will keep official incident/support bundles carrying typed attestation posture proof through `boot_attestation_digest`, `attestation_reference_digest`, and `attestation_receipt_digests` instead of falling back to verifier dashboards, portal screenshots, or ticket prose.
- Attestation reference anti-snowflake guardrail: `python3 tools/check_attestation_reference_variance_contract.py` will keep `attestation.reference` scope kind and variance posture explicit, keep the canonical example cohort-shaped and `manifest-replay-first`, and keep the measured-boot docs teaching the same anti-snowflake boundary instead of drifting back toward per-host allowlists.
- Attestation reference exception guardrail: `python3 tools/check_attestation_reference_exception_contract.py` will keep deployment/host and mixed/strict-PCR references timeboxed and approval-shaped, and will keep strict PCR pins from hiding inside the ordinary replay-first baseline.
- Attestation reference renewal guardrail: `python3 tools/check_attestation_reference_renewal_contract.py` will keep renewed non-baseline references digest-linked and successor-shaped, so renewal does not collapse back into verifier row ordering or in-place expiry extension folklore.
- Attestation identity-provenance guardrail: `python3 tools/check_attestation_identity_provenance_contract.py` will keep `attestation.receipt` naming the exact `attester.provision.receipt` digest when an attester key id is present, so AK identity does not drift back into registrar/database lookup folklore.
- Attestation action-verification guardrail: `python3 tools/check_attestation_action_verification_contract.py` will keep decisive consuming authority receipts pinning the exact requirement/receipt/policy digest tuple instead of letting hidden policy-service state become the real authority story.
- Attestation degraded-admission guardrail: `python3 tools/check_attestation_degraded_admission_contract.py` will keep degraded admission requirement-shaped so `min_verdict = degraded` remains the sole portable knob and hidden degraded-waiver state cannot quietly become the real gate.
- Attestation rejected-override guardrail: `python3 tools/check_attestation_rejected_override_contract.py` will keep ordinary secret/identity lanes fail-closed on rejected posture so explicit emergency crossing remains on breakglass instead of hiding inside successful ordinary receipts.
- Attestation verdict-projection guardrail: `python3 tools/check_attestation_verdict_projection_contract.py` will keep decisive consuming receipts carrying `attestation_receipt_verdict` as the exact pinned verifier outcome, so action receipts cannot silently reinterpret `accepted`/`degraded`/`rejected` away from the mirrored `pass`/`degraded`/`fail` verdict.
- Breakglass resumption guardrail: `python3 tools/check_breakglass_resumption_contract.py` will keep breakglass from becoming sticky ordinary authority by requiring `ordinary_resumption_posture` on `breakglass.receipt` and by teaching that later ordinary secret/identity lanes need fresh post-breakglass attestation evidence.
- Breakglass resumption exact-join guardrail: `python3 tools/check_breakglass_resumption_join_contract.py` will keep post-breakglass ordinary authority from rediscovering “the relevant breakglass session” out of backend state by requiring the exact `relevant_breakglass_receipt_digest` teaching on ordinary secret/identity lanes.
- Breakglass resumption same-host guardrail: `python3 tools/check_breakglass_resumption_subject_binding_contract.py` will keep post-breakglass ordinary authority from treating that exact breakglass join as cross-host emergency context by requiring same-host teaching on the ordinary secret/identity lanes and their canonical examples.
- Breakglass resumption temporal guardrail: `python3 tools/check_breakglass_resumption_temporal_contract.py` will keep post-breakglass ordinary authority from treating freshness as prose-only by requiring the canonical breakglass → attestation → ordinary-authority examples and docs to stay causally ordered.
- Event-journal digest coherence guardrail: `python3 tools/check_event_journal_digest_contract.py` will keep `event.record.prev_digest`, `event.segment` continuity heads, and `event.seal.receipt` segment-set roots mechanically exact instead of placeholder-shaped.
- Event-seal bundle coherence guardrail: `python3 tools/check_event_seal_bundle_contract.py` will keep official incident/support bundles from carrying event segments while hand-waving seal proof, by requiring `event_seal_receipt_digests` on the typed handoff path when continuity proof matters.
- Support-session bundle coherence guardrail: `python3 tools/check_support_session_bundle_contract.py` will keep official incident/support bundles from losing the typed place for `support.session` proof, by requiring `support_session_digests` when remote assistance belongs to the support story.

- Run `python3 tools/check_consistency.py` before committing:
  - missing RFC/ADR ids
  - broken backticked repo paths
  - broken internal markdown links (repo-relative or relative-to-file links)
  - rejects accidental ChatGPT citation markers (use explicit URLs in docs)

- Run `python3 tools/check_markdown_inline_code_balance.py` before committing Markdown-heavy changes:
  - rejects unbalanced inline backticks outside fenced code blocks
  - keeps `Last updated: 2026-05-25r517` stamp prose, historical release bullets, and short artifact/key references from turning into malformed Markdown
  - keeps inline code spans line-local instead of split across physical lines

- Run `python3 tools/check_discovery.py` before committing when you added/renamed docs or changed the reading paths:
  - ensures `docs/00-index.md` contains a `New in <version>` section for the newest CHANGELOG entry
  - ensures the newest `New in <version>` block is the **first** `New in ...` section (prevents stale top-of-file release notes)
  - ensures `docs/00-index.md` has a current-version `Last updated: 2026-05-25r517` stamp
  - ensures critical “amnesia-resistor” entry points remain wired (LLM runbook, product profiles, etc.)
  - ensures numbered docs mentioned in the newest CHANGELOG entry are wired into discovery surfaces (index vs juicy lessons)
  - ensures those docs also appear in the matching `New in <version>` block (so release notes don't go stale)
  - ensures repo paths mentioned in the newest CHANGELOG entry actually exist

- Run `python3 tools/check_changelog_format.py` to keep release notes compact and diff-friendly:
  - enforces that `CHANGELOG.md` has minimal leading whitespace after the top heading
  - rejects trailing whitespace (prevents noisy diffs)

- Run `python3 tools/check_changelog_artifact_mentions.py` to prevent 'paper artifact' drift in the newest release:
  - for docs mentioned in the newest CHANGELOG entry, ensures any backticked `*.plan`/`*.receipt`/etc artifact kinds have a matching schema under `spec/` (e.g. `spec/mirror.import.receipt.schema.json`)

- Run `python3 tools/check_release_last_updated.py` to keep release-touched docs stamped:
  - for docs mentioned in the newest `CHANGELOG.md` entry, requires a current-version `Last updated: 2026-05-25r517` stamp
  - keeps doc changes mechanically visible without forcing retroactive churn

- Run `python3 tools/check_publish_session_post_end_access_contract.py` when editing publish-session lifecycle semantics, stale-share/revisit behavior, temporary-sharing docs, or `spec/net.publish.session.schema.json`:
  - requires `lifecycle.post_end_access_posture = explicit-ended-or-fresh-share`
  - keeps stale copied/share handles fail-closed after the lease ends instead of silently rebinding to a successor share or generic launcher

- Run `python3 tools/check_must_read_set.py` to prevent 'must-read' drift:
  - ensures the runbook’s mandatory refresh list keeps the canonical start-here docs
  - keeps the generated context pack’s must-read section complete (since it is derived from the runbook)

- Run `python3 tools/check_doc_metadata.py` when editing docs in the meta-engineering range (>=397):
  - enforces a tiny Tier/Profiles/Pillars metadata block near the top of the doc
  - validates Tier/Profiles/Pillars values against the allowed enums

- Run `python3 tools/check_meta_doc_discoverability.py` when adding/moving meta-engineering docs (>=397):
  - ensures every meta doc remains linked from either `docs/00-index.md` or `docs/110-juicy-os-lessons.md`
  - prevents quiet drift where the "design law" docs exist but are unreachable

- Run `python3 tools/check_diff_surface_registry.py` when adding or refactoring diff artifacts:
  - enforces that every `*.diff` schema under `spec/` is listed in the canonical diff surface registry (`docs/430-diff-surface-registry.md`)
  - prevents quiet review-surface drift where new diffs exist but aren’t discoverable

- Run `python3 tools/check_diff_surface_registry_wiring.py` when editing the diff surface registry table:
  - enforces that each `*.diff` row includes at least one backticked wiring-doc pointer (e.g. `docs/428-...`)
  - prevents “registry lists a diff but nobody can find the gate semantics” drift

- Run `python3 tools/check_diff_review_docs.py` when adding or refactoring per-diff review-surface docs:
  - enforces that each `*diff-as-*surface*.md` doc declares Tier placement
  - requires the canonical pattern token `Registry→Diff→Gate`
  - requires schema + example pointers so reviewers can jump directly to contracts
  - keeps the family of “diff review surface” docs uniform (reduces amnesia drift)

- Run `python3 tools/check_diff_wiring_risk_flags.py` when adding new diff wiring docs:
  - incrementally requires wiring docs listed in `docs/430-diff-surface-registry.md` to declare a `## Risk flags` section (or be explicitly allowlisted under `tools/baselines/`)
  - keeps `risk_flags` reason codes as a stable jump-to review surface for UI + policy gates

- Run `python3 tools/check_juicy_lesson_references.py` when adding new external URLs to the juicy lessons index (`docs/110-juicy-os-lessons.md`):
  - blocks new uncataloged citations without forcing retroactive churn (uses a baseline allowlist)
  - prefer adding new URLs to `docs/32-curated-references.md`; extend the allowlist only for historic gaps

- Run `python3 tools/check_risk_flag_registry.py` when introducing or renaming `risk_flags` reason codes:
  - enforces that a canonical risk flag registry exists as a typed artifact (`risk.flag.registry`)
  - ensures spec examples and gate docs use canonical kebab-case ids (prevents ad-hoc flag drift)

- Run `python3 tools/check_risk_flag_typical_sources.py` to keep risk flag metadata wired to real artifacts:
  - ensures each `typical_sources` entry in `risk.flag.registry` refers to a real schema under `spec/`
  - requires diff kinds referenced as typical sources are listed in the canonical diff surface registry (`docs/430-diff-surface-registry.md`)

- Run `python3 tools/check_doc_patterns.py` for meta docs (>=397):
  - requires a `**Patterns:**` metadata line near the top
  - forces new ideas to explicitly map to existing patterns (reduces design sprawl)

- Run `python3 tools/check_role_binding_policy_contract.py` when editing non-interactive remembered-role authority joins or `intent.role.binding.event` policy wiring:
  - keeps `policy-reconcile` role-binding events joined to `policy.decision` through `policy_decision_digest`
  - enforces the canonical policy-reconcile example and the complementary workstation/policy doc wiring

- Run `python3 tools/check_role_binding_precondition_contract.py` when editing remembered-role apply semantics or stale-write denial docs/schemas:
  - keeps `intent.role.binding.diff.from_binding.digest` as the compare-and-swap precondition
  - keeps stale writes on typed `precondition-failed` evidence (`reason_code`, `observed_binding`) instead of silent rebase
- Run `python3 tools/check_role_binding_import_contract.py` when editing remembered-role support/import joins, subtype schemas, or `intent.role.binding.event` import provenance wiring:
  - keeps `trigger = support-import` joined back to typed import evidence through `import_receipt_digest` instead of restore-log folklore
  - enforces the shipped remembered-role subtype profile schemas so example validation stays warning-free
- Run `python3 tools/check_role_binding_authority_contract.py` when editing remembered-role event trigger vocabulary, admin-tool semantics, or `source.*` vs `trigger` wiring:
  - keeps `intent.role.binding.event.trigger` reserved for authority/apply lanes instead of local/remote admin transport folklore
  - keeps admin-tool identity in `source.name` / `source.service_id` while non-interactive writes still compile through `policy.decision`
- Run `python3 tools/check_role_binding_policy_profile_contract.py` when editing remembered-role non-interactive policy exactness or `policy.decision` request/apply tuples:
  - keeps the exact-mutation role-binding policy profile on `spec/intent.role.binding.policy.profile.schema.json`
  - keeps `policy_decision_digest` joined to a host/profile/trigger/binding tuple instead of a vague class-level allowance
- Run `python3 tools/check_role_binding_policy_apply_window_contract.py` when editing remembered-role non-interactive policy freshness/consumption semantics:
  - keeps single-apply remembered-role policy decisions bounded by `must_apply_before` plus `max_successful_events = 1`
  - keeps successful remembered-role writes from turning `policy_decision_digest` into a reusable standing permission
- Run `python3 tools/check_role_binding_policy_instance_identity_contract.py` when editing remembered-role non-interactive policy re-issuance / digest-identity semantics (unique issuance identity):
  - keeps remembered-role policy decisions carrying `decision_instance_id`
  - keeps independently issued exact-mutation/single-apply authorizations from collapsing to the same digest
- Run `python3 tools/check_role_binding_policy_denial_contract.py` when editing remembered-role non-interactive denial semantics or `intent.role.binding.event.reason_code` for joined policy-window failures:
  - keeps `policy-expired` and `policy-consumed` distinct from generic `policy-denied`
- Run `python3 tools/check_role_binding_denial_precedence_contract.py` when editing remembered-role denial ordering across policy-window checks and compare-and-swap:
  - keeps `policy-denied` / `policy-consumed` / `policy-expired` winning before `precondition-failed` in the non-interactive lane
  - keeps `policy-consumed` from decaying into `policy-expired` on later retries
  - keeps the dedicated policy-window denial subtype/example and evidence wiring stable
- Run `python3 tools/check_role_binding_policy_consumption_pointer_contract.py` when editing remembered-role `policy-consumed` denial evidence or non-interactive replay/support semantics:
  - keeps `reason_code = policy-consumed` carrying `consumed_by_event_id`
  - keeps the denial pointing at the earlier successful consuming event instead of leaving winner identification to log archaeology
- Run `python3 tools/check_role_binding_policy_consumption_digest_contract.py` when editing remembered-role `policy-consumed` denial evidence or offline export/bundle verification semantics:
  - keeps `policy-consumed` denials carrying `consumed_by_event_digest`
  - keeps the denial bound to verifiable consuming-event bytes instead of only an id pointer
- Run `python3 tools/check_role_binding_policy_consumption_previous_binding_digest_contract.py` when editing remembered-role `policy-consumed` denial evidence for updated winners or old→new retry/export summaries:
  - keeps `consumed_previous_binding_digest` available when the earlier consuming success was `updated`
  - keeps the winner's replaced `previous_binding.digest` queryable without reopening the winner event body
- Run `python3 tools/check_role_binding_policy_consumption_action_contract.py` when editing remembered-role `policy-consumed` denial winner-shape summaries or old-edge presence rules:
  - keeps `consuming_event_action` aligned with the earlier consuming success event's `action`
  - keeps `consumed_previous_binding_digest` required for updated winners and forbidden for initialized winners
- Run `python3 tools/check_role_binding_policy_consumption_recovery_contract.py` when editing remembered-role retry/recovery semantics:
  - keeps `policy-consumed` retries collapsing to **already-applied** only on an exact consuming-event tuple match
  - keeps spent-authority failures that do *not* prove the same tuple visible as ordinary denials
- Run `python3 tools/check_role_binding_policy_recovery_interpretation_contract.py` when editing remembered-role retry/export summary semantics:
  - keeps `policy-consumed` denials carrying `recovery_interpretation`
  - keeps `recovery_interpretation = already-applied` reserved for exact-match replay proofs
- Run `python3 tools/check_role_binding_policy_consumption_binding_digest_contract.py` when editing remembered-role spent-authority result summaries:
  - keeps `policy-consumed` denials carrying `consumed_binding_digest`
  - keeps `consumed_binding_digest` aligned with the earlier consuming success event
- Run `python3 tools/check_role_binding_policy_consumption_diff_digest_contract.py` when editing remembered-role spent-authority review summaries:
  - keeps `policy-consumed` denials carrying `consumed_diff_digest`
  - keeps `consumed_diff_digest` aligned with the earlier consuming success event

- Run `python3 tools/check_curated_references.py` when introducing new external work in meta docs (>=397):
  - ensures each external URL in meta docs is listed in `docs/32-curated-references.md`
  - keeps citations centralized and reduces long-term “link drift”

- Run `python3 tools/check_release_curated_references.py` when cutting a release that introduces new numbered docs:
  - for numbered docs mentioned in the newest `CHANGELOG.md` entry, ensures any external URLs are also listed in `docs/32-curated-references.md`
  - prevents new “uncataloged citations” without forcing retroactive churn across the full archive

- Run `python3 tools/check_support_bundle_contract.py` when editing incident/support handoff docs or schemas:
  - keeps the official support handoff contract wired (`incident.timeline` + `incident.bundle` + `bundle.plan` + `bundle.payload.manifest` + `bundle.build.receipt`)
  - enforces timeline-first example wiring and the canonical `tar.zst` payload default

- Run `python3 tools/check_safe_open_contract.py` when editing content-import, safe-open, or support-bundle intake docs/schemas:
  - keeps the safe-open support-bundle intake boundary wired (`content.import.plan` + `content.import.receipt` execution boundary, no-network disposable intake, timeline-first preview posture)
  - enforces the canonical example wiring so support-bundle intake does not drift back to direct-host-open folklore

- Run `python3 tools/check_support_bundle_import_contract.py` when editing the typed support-bundle intake shapes or canonical import examples:
  - keeps `spec/content.import.support-bundle.plan.schema.json` / `spec/content.import.support-bundle.receipt.schema.json` aligned with the generic import lane
  - enforces that the official support-bundle path remains a constrained specialization of `content.import.plan` / `content.import.receipt`, not a new authority kind
  - keeps the canonical support-bundle example shapes, preview members, and disposable microVM posture wired

- Run `python3 tools/check_boot_contract.py` when editing boot admission, loader-verification, or kernel-module join docs/schemas:
  - keeps the boot-code admission contract wired (`boot.manifest` + `boot.override.policy` + `boot.override.receipt` + `boot.attestation` + `kmod.load.plan` + `kmod.load.receipt`)
  - enforces example digest joins so manifests, attestation, override receipts, and kmod receipts cannot drift apart silently

- Run `python3 tools/check_reset_contract.py` when editing install/recovery, destructive reprovision, or reset-authority docs/schemas:
  - keeps the destructive-reprovision contract wired (`reset.authorization` + `reset.receipt` + `disk.layout.plan` + `disk.layout.receipt`)
  - enforces example digest joins so reset authority, disk mutation evidence, and A–D profile defaults cannot drift apart silently

- Run `python3 tools/check_strata_contract.py` when editing runtime-composition docs or schemas:
  - keeps the explicit userland-composition contract wired (`stratum.manifest` + `stratum.stack` + `mount.view` + `runtime.manifest`)
  - enforces the example digest joins and the no-host-fallback / single-ABI-anchor boundary so multi-origin userlands do not drift back into ad-hoc chroot folklore

- Run `python3 tools/check_keyless_identity_contract.py` when editing keyless identity, Sigstore bundle, or release-authority join docs/schemas:
  - keeps `publisher.identity.receipt` supplemental (`authority_semantics = identity-evidence-only`) and bundle-first for `sigstore-keyless`
  - enforces the example digest joins across `publisher.identity.receipt`, `sigstore.bundle`, trust roots, `release.authority.policy`, and `release.publish.receipt`

- Run `python3 tools/check_release_transparency_contract.py` when editing release transparency, checkpoint receipts, monitor snapshots, or release-authority gating docs/schemas:
  - keeps `release.publish.receipt` authoritative while `release.transparency.entry`, `log.checkpoint.receipt`, and `transparency.monitor.snapshot` stay evidence-only
  - enforces the example digest joins across `release.authority.policy`, `release.transparency.entry`, `log.checkpoint.receipt`, `transparency.monitor.snapshot`, and `release.publish.receipt`

- Run `python3 tools/check_witness_policy_contract.py` when editing witness rosters, checkpoint receipts, monitor policy, or release-authority witness gating docs/schemas:
  - keeps `witness.policy` as the authoritative witness-trust surface instead of inline quorum folklore
  - enforces the example digest joins across `witness.policy`, `log.checkpoint.receipt`, `transparency.monitor.policy`, `release.authority.policy`, and `release.publish.receipt`

- Run `python3 tools/check_supplychain_verification_contract.py` when editing workflow-verification, in-toto layout-policy, or release-authority gating docs/schemas:
  - keeps `supplychain-verify-receipt` supplemental (`authority_semantics = workflow-verification-evidence-only`)
  - enforces the example digest joins across `supplychain-layout-policy`, `supplychain-verify-receipt`, `release.authority.policy`, and `release.publish.receipt`

- Run `python3 tools/check_vulnerability_verification_contract.py` when editing vulnerability-intel, VEX, or release-authority gating docs/schemas:
  - keeps `vuln-gate-receipt` supplemental (`authority_semantics = vulnerability-verification-evidence-only`)
  - enforces the example digest joins across `vuln.gate.policy`, `vuln.query.receipt`, `vuln-gate-receipt`, `release.authority.policy`, and `release.publish.receipt`

- Run `python3 tools/check_attestation_admission_contract.py` when editing attestation evidence, admission-policy, or consuming action-receipt docs/schemas:
  - keeps `attestation.receipt` evidence-only (`authority_semantics = attestation-evidence-only`)
  - enforces the example digest joins across `attestation.requirement`, `attestation.admission.policy`, `attestation.receipt`, `secret-receipt`, `breakglass-receipt`, and `workload-identity-issue-receipt`

- Run `python3 tools/check_attestation_identity_provenance_contract.py` when editing measured-boot, attester-lifecycle, or attestation-receipt docs/schemas:
  - keeps `attestation.receipt` joining attester identity provenance by exact `attester.provision.receipt` digest when `attester_key_id` is present
  - enforces the canonical receipt example and the no-registrar-folklore boundary across the measured-boot / attester-lifecycle docs

- Run `python3 tools/check_attestation_action_verification_contract.py` when editing consuming action-receipt, attestation-admission, or remote-attestation docs/schemas:

- Run `python3 tools/check_attestation_degraded_admission_contract.py` when editing `attestation.requirement`, degraded attestation examples, or consuming authority receipt wording:
  - `spec/attestation.requirement.schema.json`
  - `spec/examples/attestation.requirement.degraded.json`
  - `spec/examples/secret.receipt.degraded.json`
  - `spec/secret.receipt.schema.json`
  - `spec/breakglass.receipt.schema.json`
  - `spec/workload.identity.issue.receipt.schema.json`
  - `docs/226-platform-posture-and-attestation-results-as-evidence.md`
  - `docs/388-remote-attestation-admission-and-enrollment.md`
  - `docs/469-platform-provenance-and-attestation-admission-posture-by-profile.md`
  - `docs/492-attestation-results-evidence-and-admission-issue-boundary.md`
  - `docs/645-attestation-consuming-action-receipts-pin-the-exact-decision-tuple.md`
  - `docs/646-attestation-degraded-admission-stays-requirement-shaped-and-no-hidden-waivers.md`
  - `docs/99-llm-runbook.md`

  - keeps decisive `attestation_verification` outcomes carrying the full exact requirement/receipt/policy digest tuple
  - enforces the canonical action-receipt examples and the no-hidden-policy-service-state boundary across the consuming attestation docs

- Run `python3 tools/check_lease_authority_contract.py` when editing temporary-authority grant / lease / use docs or schemas:
  - keeps the authoritative temporary-authority object lane-specific (grant / lease / session) while `lease.envelope`, `lease.issue.receipt`, and `lease.use.receipt` stay metadata / evidence-only
  - enforces the canonical example joins across `portal-grant`, `lease.envelope`, `lease.issue.receipt`, `lease.use.receipt`, and `export.receipt`

- Run `python3 tools/check_authority_budget_contract.py` when editing authority-budget docs or schemas:
  - keeps `authority.budget` authoritative for the narrow component-runtime lane while `authority.budget.check` stays evidence-only
  - enforces the v0 dimension set and the canonical example joins across `authority.budget`, `authority.budget.check`, and `authority.exception`

- Run `python3 tools/check_store_gc_contract.py` when editing retention, GC, or boot-environment wiring docs/schemas:
  - keeps the store-retention contract wired (`store_retention` profile defaults + `store.gc.plan` + `store.gc.receipt`)
  - enforces the hard rollback-floor split from soft retention preference and the canonical rollback-coverage example wiring

- Run `python3 tools/check_publish_session_contract.py` when editing temporary sharing, relay-backed publish, or ingress/transport boundary docs or schemas:
  - keeps `net.publish.session` distinct from durable non-loopback ingress
  - enforces the canonical local-first + leased + transport-joined publish-session example and keeps the discovery docs wired

- Run `python3 tools/check_publish_session_access_posture_contract.py` when editing temporary sharing audience/publicness posture, publish-session docs, or `spec/net.publish.session.schema.json`:
  - keeps `published_endpoint.audience` required on `net.publish.session`
  - keeps B/C human sharing audience-bound by default and keeps `public-link` / `public-webhook` explicit instead of collapsing `internet` back into ambient public sharing

- Run `python3 tools/check_publish_session_lifetime_contract.py` when editing publish-session lifetime/end-condition posture, temporary sharing docs, or `spec/net.publish.session.schema.json`:
  - keeps `net.publish.session.lifecycle` required with explicit end conditions
  - keeps relay-backed sharing reboot-cleared and `new-session-with-fresh-authority` instead of silently auto-resuming after restart
  - keeps authority-triggered endings (`initiating-user-session-end`, `support-session-end`, `operator-session-end`, `maintenance-window-end`) aligned with the initiating authority lane

- Run `python3 tools/check_publish_session_locator_posture_contract.py` when editing publish-session locator/naming posture, temporary sharing docs, or `spec/net.publish.session.schema.json`:
  - keeps `published_endpoint.locator_posture` required on `net.publish.session`
  - keeps public/org/support relay locators `session-scoped` so reserved domains, custom DNS, or remembered public hostnames do not become the real durable-ingress surface
  - keeps `tailnet-device-name` as the only stable-name exception inside the temporary-sharing lane

- Run `python3 tools/check_publish_session_secret_handoff_contract.py` when editing publish-session secret-gating posture, temporary sharing docs, or `spec/net.publish.session.schema.json`:
  - keeps secret-gated publish sessions joined to `secret.receipt` instead of embedding usable bearer material in `url_hint` / `path_prefix`
  - keeps `published_endpoint.secret_handoff.secret_receipt_digest` present for `single-use-secret` / `shared-secret` auth modes
- Run `python3 tools/check_publish_session_secret_lifetime_contract.py` when editing publish-session secret lifetime posture, temporary sharing docs, or `spec/net.publish.session.schema.json`:
  - keeps secret-gated publish sessions `session-authority-bounded` instead of leaving behind a longer-lived shadow secret
  - keeps `published_endpoint.secret_handoff.expires_at` present and no later than the publish-session authority window in the canonical example
- Run `python3 tools/check_publish_session_secret_consumption_contract.py` when editing publish-session secret consumption posture, temporary sharing docs, or `spec/net.publish.session.schema.json`:
  - keeps `published_endpoint.secret_handoff.consumption_posture` required for secret-gated publish sessions
  - keeps `single-use-secret` bound to `single-successful-admission` and `shared-secret` bound to `reusable-until-expiry`

- Run `python3 tools/check_publish_session_secret_handoff_authn_mode_contract.py` when editing publish-session secret authn posture, temporary sharing docs, or `spec/net.publish.session.schema.json`:
  - keeps `secret_handoff` exact with the typed `authn_mode` lane so `authn_mode` stays singular
  - keeps non-secret lanes (`none`, `provider-identity`, `support-session`, `tailnet-identity`) from carrying a second hidden secret story

- Run `python3 tools/check_publish_session_support_session_contract.py` when editing support-peer sharing, remote-assistance joins, temporary sharing docs, or `spec/net.publish.session.schema.json`:
  - keeps `support-peer` publication subordinate to the `support.session` authority lane
  - keeps `authority.support_session_digest` required whenever support-session wording becomes the actual publish-session posture

- Run `python3 tools/check_publish_session_authority_join_contract.py` when editing publish-session authority lanes, temporary sharing docs, or `spec/net.publish.session.schema.json`:
  - keeps authority joins now follow `authority.trigger` exactly
  - keeps maintenance stays reserved and digest-empty until a dedicated maintenance-window join exists
  - keeps `trusted-ui` / `policy` / `operator-session` / `support-session` publication from mixing several digest families in one receipt

- Run `python3 tools/check_publish_session_lease_id_contract.py` when editing publish-session lease wiring, temporary sharing docs, or `spec/net.publish.session.schema.json`:
  - keeps every publish session carrying `authority.lease_id`
  - keeps the canonical example lease-addressable across trusted-UI, policy, and maintenance-shaped variants

- Run `python3 tools/check_publish_session_support_trigger_contract.py` when editing publish-session support authority posture, support-peer docs, or `spec/net.publish.session.schema.json`:
  - keeps `authority.trigger = support-session` bound back to the full support-peer share shape; support-session trigger itself now also stays support-peer shaped
  - keeps support-session proof from justifying public callback/demo or ordinary audience-bound `relay-url` shares

- Run `python3 tools/check_publish_session_access_model_contract.py` when editing publish-session access-model posture, temporary sharing docs, or `spec/net.publish.session.schema.json`:
  - keeps `public-link` / `public-webhook` URL-shaped with `relay-url`
  - keeps support-peer sharing `peer-relay` shaped instead of regressing to generic tunnel-URL folklore

- Run `python3 tools/check_publish_session_tailnet_access_model_contract.py` when editing tailnet sharing posture, publish-session access-model docs, or `spec/net.publish.session.schema.json`:
  - keeps `tailnet` / `tailnet-users` / `tailnet-identity` / `tailnet-device-name` aligned with `reverse-forward`
  - keeps the private tailnet lane from drifting back into URL-shaped relay folklore

- Run `python3 tools/check_publish_session_human_share_access_model_contract.py` when editing audience-bound human-share posture, publish-session access-model docs, or `spec/net.publish.session.schema.json`:
  - keeps `organization-users` / `named-recipients` aligned with `relay-url`
  - keeps ordinary human sharing from drifting into support-peer `peer-relay` or tailnet `reverse-forward` vocabulary

- Run `python3 tools/check_publish_session_organization_exposure_contract.py` when editing organization-user audience posture, human-share exposure wiring, or `spec/net.publish.session.schema.json`:
  - keeps `organization-users` bound to `published_endpoint.exposure_scope = organization`
  - preserves the narrower non-decision that `named-recipients` exposure is still open
  - keeps the organization-user exposure exactness from drifting back into generic internet publication

- Run `python3 tools/check_publish_session_surface_continuity_contract.py` when editing publish-session endpoint continuity, temporary-sharing share-surface semantics, or `spec/net.publish.session.schema.json`:
  - keeps `published_endpoint.continuity_posture = lease-frozen` required on `net.publish.session`
  - keeps one bounded share tied to one outward published-endpoint surface instead of repointing hostname/path/audience/access posture under the same lease
  - keeps material outward surface change requiring a fresh `session_id` and fresh `authority.lease_id`

- Run `python3 tools/check_publish_session_diagnostic_artifact_contract.py` when editing publish-session evidence surfaces, support/investigation joins, or `spec/net.publish.session.schema.json`:
  - keeps the compact `net.publish.session` envelope baseline-safe
  - keeps `evidence.diagnostic_artifact_digests` off the publish-session schema
  - keeps richer relay/admin diagnostics on support/operator/incident evidence joins instead of the bounded share envelope

- Run `python3 tools/check_publish_session_notes_contract.py` when editing compact publish-session evidence surfaces, temporary-sharing docs, or `spec/net.publish.session.schema.json`:
  - keeps the compact `net.publish.session` envelope note-free
  - keeps free-text `evidence.notes` off the baseline share receipt so commentary must move onto typed fields or stronger evidence lanes

- Run `python3 tools/check_publish_session_return_path_contract.py` when editing active-share management-surface recovery posture, temporary-sharing trusted-UI docs, or `spec/net.publish.session.schema.json`:
  - keeps `evidence.management_return_path_posture = trusted-ui-persistent-until-ended` required on `net.publish.session`
  - keeps a stable trusted-UI re-entry path to the active-share surface present for the full session lifetime
  - keeps browser back/history luck, one-shot toasts, or route rediscovery from masquerading as the share-management recovery path

- Run `python3 tools/check_publish_session_management_return_binding_contract.py` when editing active-share management-target exactness, temporary-sharing trusted-UI return docs, or `spec/net.publish.session.schema.json`:
  - keeps `evidence.management_return_binding = lease-exact` required on `net.publish.session`
  - keeps the stable trusted-UI re-entry path bound to the exact live `authority.lease_id`
  - keeps a generic share home, nearest-current-share view, or successor lease from masquerading as the exact active-share recovery target

- Run `python3 tools/check_publish_session_binding_hints_contract.py` when editing publish-session audience bindings, human-share posture, or `spec/net.publish.session.schema.json`:
  - keeps `provider-identity` / `organization-users` shares naming `identity_provider_hint`
  - keeps `named-recipients` shares naming `recipient_hint` instead of leaving the recipient boundary hand-wavy

- Run `python3 tools/check_publish_session_webhook_validation_contract.py` when editing `public-webhook` posture, publish-session callback-validation docs, or `spec/net.publish.session.schema.json`:
  - keeps `public-webhook` shares naming `audience.validation_hint`
  - keeps callback publication evidentially verifiable without turning the hint into the secret itself

- Run `python3 tools/check_publish_session_validation_hint_webhook_only_contract.py` when editing publish-session validation-hint semantics, audience/publicness docs, or `spec/net.publish.session.schema.json`:
  - keeps `audience.validation_hint` webhook-only
  - keeps non-webhook shares from borrowing callback-verification prose as a generic note field

- Run `python3 tools/check_publish_session_endpoint_hint_contract.py` when editing publish-session endpoint hints, access-model docs, or `spec/net.publish.session.schema.json`:
  - keeps `relay-url` / `reverse-forward` shares carrying `hostname + port`
  - keeps `url_hint` / `path_prefix` restricted to `relay-url` and keeps `peer-relay` free of URL/host endpoint hints

- Run `python3 tools/check_publish_session_url_hint_contract.py` when editing `relay-url` URL hints, endpoint tuples, or `spec/net.publish.session.schema.json`:
  - keeps `url_hint` / `path_prefix` paired on `relay-url` shares
  - keeps `url_hint` serializing the same `hostname + port + path_prefix` tuple the receipt already carries

- Run `python3 tools/check_publish_session_local_service_hint_contract.py` when editing publish-session local-source hints, temporary sharing docs, or `spec/net.publish.session.schema.json`:
  - keeps optional `local_service.service_uri_hint` absolute + loopback-shaped + free of userinfo/query/fragment
  - keeps obvious scheme-bearing protocols (`http`, `https`, `ssh`) aligned with `local_service.protocol` so the local source hint cannot contradict the local-first boundary

- Run `python3 tools/check_publish_session_path_prefix_contract.py` when editing publish-session path hints, URL-hint coherence docs, or `spec/net.publish.session.schema.json`:
  - keeps optional `published_endpoint.path_prefix` absolute + normalized
  - keeps repeated separators and `.` / `..` path segments out of the canonical typed path floor

- Run `python3 tools/check_publish_session_path_prefix_uri_safe_contract.py` when editing publish-session path hints, typed endpoint-path grammar, or `spec/net.publish.session.schema.json`:
  - keeps optional `published_endpoint.path_prefix` URI-path-safe and decode-stable
  - keeps percent-encoding, raw spaces, and backslashes out of the typed path field so later readers do not invent a second decode/comparison ladder

- Run `python3 tools/check_publish_session_hostname_contract.py` when editing publish-session published endpoint hosts, endpoint tuples, temporary sharing docs, or `spec/net.publish.session.schema.json`:
  - keeps optional `published_endpoint.hostname` lowercase + host-shaped rather than URL-shaped or `host:port`-shaped
  - keeps the canonical published host token non-local so the published endpoint tuple cannot collapse back into localhost/loopback source folklore

- Run `python3 tools/check_publish_session_remote_locator_contract.py` when editing relay-side publish-session locators, access-model docs, or `spec/net.publish.session.schema.json`:
  - keeps `relay.remote_locator.kind = uri-hint` in the `relay-url` lane
  - keeps `peer-relay` on `portal-object` / `opaque` and `reverse-forward` on `object-path` / `opaque`

- Run `python3 tools/check_publish_session_remote_locator_value_contract.py` when editing relay-side locator values, relay-kind docs, or `spec/net.publish.session.schema.json`:
  - keeps `relay.remote_locator.value` URI-shaped only for `uri-hint`
  - keeps `portal-object` / `object-path` / `opaque` values non-URI-shaped so support/tailnet lanes cannot hide URL-looking value text

- Run `python3 tools/check_publish_session_remote_locator_uri_hint_contract.py` when editing relay-side `uri-hint` locators, relay-value docs, or `spec/net.publish.session.schema.json`:
  - keeps `relay.remote_locator.value` URI-shaped but non-web-shaped when `kind = uri-hint`
  - keeps `http` / `https`, userinfo, query, and fragment material out of the relay-side locator so it cannot collapse into a second public endpoint URL

- Run `python3 tools/check_publish_session_destination_hint_contract.py` when editing relay-side destination hints, relay-locator docs, or `spec/net.publish.session.schema.json`:
  - keeps URL-shaped `relay.destination_hint` identical to `relay.remote_locator.value`
  - keeps `portal-object` / `object-path` / `opaque` destination hints non-URI-shaped

- Run `python3 tools/check_learn_net_contract.py` when editing learned-network-policy docs or schemas:
  - keeps `net-flow-summary` as the compact evidence-only learn-session surface rather than a hidden authority object
  - enforces bounded learn/audit sessions, canonical example digest joins to `net-flow-receipt` / `net-dns-query-receipt` / `net-egress-policy`, and keeps review-before-enforce visible in the core docs

- Run `python3 tools/check_packet_capture_boundary.py` when editing packet-capture, raw-socket, BPF-risk, or fast-packet-I/O docs:
  - keeps packet capture / raw packet visibility distinct from ordinary `net-egress-policy`
  - enforces that flight recorder, network, device, and netmap docs all point at the same stronger boundary in `docs/506-packet-capture-raw-sockets-and-fast-packet-io-boundary.md`

- Run `python3 tools/check_packet_capture_session_contract.py` when editing packet-capture session, export, or incident-bundle docs/schemas:
  - keeps packet capture lease-shaped through `packet.capture.session` rather than ad-hoc blob workflows
  - enforces summary-first export posture across the packet-capture, export, incident-bundle, evidence, and risk-register docs

- Run `python3 tools/check_packet_capture_summary_contract.py` when editing packet-capture summary, export, or evidence docs/schemas:
  - keeps `packet.capture.summary` distinct from `net-flow-summary` so packet-capture review does not blur into network-policy learning
  - enforces the canonical summary digest join back to `packet.capture.session` and keeps export/incident/evidence docs centered on the summary-first review surface

- Run `python3 tools/check_packet_capture_selector_contract.py` when editing packet-capture selector/session docs or schemas:
  - keeps `packet.capture.selector` as the typed review surface inside `packet.capture.session`
  - prevents free-form backend filter strings from quietly returning to the authoritative session object
  - keeps the selector compiler boundary visible in the session, summary, runbook, and evidence docs

- Run `python3 tools/check_packet_capture_artifact_contract.py` when editing packet-capture retention/summary/export docs or schemas:
  - keeps retained raw packet files subordinate to the typed session/summary lane

- Run `python3 tools/check_packet_capture_import_contract.py` when editing packet-capture import, safe-open, or export docs/schemas:
  - keeps stronger sideband/decryption-bearing packet-capture artifacts on the typed safe-open import profile rather than host-open folklore
  - enforces normalize-before-promotion so ordinary support/export lanes prefer `packet.capture.summary` or normalized `packet-records-only` derivatives
- Run `python3 tools/check_packet_capture_normalization_contract.py` when editing packet-capture normalization, redaction, or export docs/schemas:
  - keeps packet-capture normalization on the generic `redaction-transform` / `redaction-receipt` evidence lane
  - enforces that packet-capture import receipts point at typed normalization proof instead of treating `strip-metadata` as a free-floating tool side effect
- Run `python3 tools/check_packet_capture_bundle_contract.py` when editing packet-capture bundle, support-handoff, or incident-bundle docs/schemas:
  - keeps `incident.bundle` / `bundle.plan` packet-capture joins explicit through session/summary/import/redaction receipt digests
  - enforces that support bundles stay summary-first for packet capture rather than quietly regressing into raw `.pcapng` payload defaults
  - enforces explicit `max_local_retention_seconds`, `metadata_posture`, and `retention_until` joins so local packet files do not quietly become the real product surface

- Run `python3 tools/check_packet_capture_export_contract.py` when editing packet-capture export-policy / export-receipt docs or schemas:
  - keeps `packet.capture.summary` as the ordinary export class and `packet.capture.normalized` as the stronger explicit raw-byte class
  - requires proof-bound stronger exports to carry typed `supporting_evidence` joins back to session / summary / import / redaction evidence instead of normalized `.pcapng` folklore
- Run `python3 tools/check_packet_capture_export_approval_contract.py` when editing stronger packet-capture export approval docs or schemas:
  - keeps `consent_receipt_digest` required for `packet.capture.normalized` export
  - prevents approval drift back to `method = auto` when stronger packet bytes leave the system
- Run `python3 tools/check_packet_capture_export_transport_contract.py` when editing stronger packet-capture export transport or handoff docs/schemas:
  - keeps `transport_receipt_digest` required for completed `packet.capture.normalized` export
  - prevents `destination.type = file` from quietly becoming the completed stronger export act
- Run `python3 tools/check_packet_capture_export_acceptance_contract.py` when editing stronger packet-capture export closure docs/schemas:
  - keeps `transport_acceptance_receipt_digest` required for final `packet.capture.normalized` export
  - keeps `spec/transport.acceptance.receipt.schema.json` + `spec/packet.capture.export.transport.acceptance.receipt.profile.schema.json` wired as the transport acceptance receipt surface
  - keeps final stronger handoff at `delivery_state = recipient-accepted` rather than treating send success as acceptance
  - keeps stronger packet approval destination-bound by checking `action.destination` against transport / recipient acceptance / export destination evidence (`tools/check_packet_capture_export_destination_binding_contract.py`)
- Run `python3 tools/check_packet_capture_export_recipient_digest_contract.py` when editing stronger packet-capture export closure/proof docs or schemas:
  - keeps `acceptance.remote_artifact_digest` required for stronger packet recipient acceptance
  - enforces that the recipient-side acceptance receipt echoes the same normalized digest instead of merely a plausible remote reference
- Run `python3 tools/check_packet_capture_export_remote_object_contract.py` when editing stronger packet-capture export closure/proof docs or schemas:
  - keeps `adapter.remote_id` required for canonical stronger packet export receipts
  - enforces that transport / recipient acceptance / final export evidence stay on the same remote object identifier instead of drifting across multiple remote attachments in one case
- Run `python3 tools/check_packet_capture_export_remote_validator_contract.py` when editing stronger packet-capture export closure/proof docs or schemas:
  - keeps `remote_validator` continuity required when the stronger adapter can see a remote representation/version token
  - enforces that transport / recipient acceptance / final export evidence stay on the same remote validator instead of collapsing back to object id alone
- Run `python3 tools/check_packet_capture_export_remote_protection_contract.py` when editing stronger packet-capture export closure/proof docs or schemas:
  - keeps `remote_protection` continuity required for canonical stronger packet handoff
  - enforces that recipient acceptance / final export evidence stay on the same remote protection posture instead of treating any accepted upload as durable evidence by implication
- Run `python3 tools/check_packet_capture_export_remote_locator_contract.py` when editing stronger packet-capture export closure/proof docs or schemas:
  - keeps `remote_locator` continuity required for canonical stronger packet handoff
  - enforces that transport / recipient acceptance / final export evidence stay on the same remote locator instead of leaving later evidence retrieval to portal folklore
- Run `python3 tools/check_packet_capture_export_reverification_contract.py` when editing stronger packet-capture export follow-up/recheck docs or schemas:
  - keeps `transport.reverification.receipt` as the typed metadata-only reverification lane for later stronger packet evidence checks
  - enforces `body_downloaded = false` plus the same accepted remote validator / protection posture / locator instead of portal screenshots or packet re-downloads
- Run `python3 tools/check_packet_capture_export_digest_stability_contract.py` when editing stronger packet-capture export proof-chain, approval, or transport docs/schemas:
  - keeps stronger packet export digest-stable across normalization, approval, transport, recipient acceptance, and export
  - enforces that approval / transport / transport-acceptance / export receipts keep the same normalized digest instead of drifting across related derivatives

- Run `python3 tools/check_frontend_compile_contract.py` when editing frontend-authoring boundary docs or schemas:
  - keeps compiled canonical JSON authoritative while `frontend.compile.receipt` stays evidence-only
  - enforces the canonical HuJSON example joins across `frontend.compile.receipt`, `spec/examples/trust.policy.hujson`, and `spec/examples/trust.policy.json`

- Run `python3 tools/check_package_recipe_surface_contract.py` when editing package-recipe, build-language, or restricted-pipeline boundary docs:
  - keeps the package-recipe authority boundary evaluator-free and restricted-pipeline-first
- Run `python3 tools/check_package_recipe_step_boundary.py` when editing native restricted-pipeline step-boundary docs:
  - keeps the native lane registry-backed
  - forbids a generic authoritative `run` / `script` / opaque-command escape hatch
  - enforces that ADR-0289 / docs/699 / RFC-0091 / the risk register all keep saying the same thing instead of quietly reopening “maybe some general language later”
- Run `python3 tools/check_cross_platform_identity_boundary.py` when editing store, closure, base-set, or cross-compilation boundary docs:
  - keeps cross-compilation identity on explicit `build_platform` / `host_platform` / optional `target_platform` metadata
  - keeps store paths are not a target-triple namespace
  - keeps runtime closure/admission keyed on `host_platform` instead of path parsing or ambient build variables

- Run `python3 tools/check_crypto_compat_agent_projection_boundary.py` when editing crypto broker, key-policy, or compatibility-agent boundary docs:
  - keeps compatibility agents as typed projections over the brokered lane rather than ambient authority
  - keeps the first reviewed scope `local-session-only`
  - keeps remembered approvals `same-lease-only` instead of durable agent folklore

- Run `python3 tools/check_fuzz_contract.py` when editing fuzzing, crash-replay, or regression-localization docs/schemas:
  - keeps `fuzz.receipt` evidence-only and `crash.case` replay-focused with explicit reproducibility state
  - enforces the v0 target-class set, keeps coverage percentages advisory, and prevents drift across fuzz receipts, crash cases, and product-shape fuzz target classes

- Run `python3 tools/check_product_profiles.py` when editing `spec/examples/product.profiles.json` or profile-shape docs:
  - keeps the A–D runtime and authority defaults stable
  - prevents profile drift on network-topology posture, hardware-compatibility posture, device-authority posture, installation/recovery posture, kernel-mutation posture, update-delivery posture, high-risk approval posture, workstation runtime, removable media, firmware-update posture, backup/recovery posture, data-at-rest posture, trustworthy-time posture, platform-provenance / attestation-admission posture, inbound/outbound networking posture, remote-assistance posture, private-key posture, human-identity/home-state posture, evidence-collection posture, evidence-export posture, trust-bundle posture, and workload-identity / credential-issuance posture

- Run `python3 tools/check_remote_assistance_recording_posture.py` when editing remote-assistance recording/detail/export posture docs:
  - keeps `docs/616-remote-assistance-recording-detail-and-export-posture-by-profile.md` wired as a compiled consequence of `remote_assistance`, `evidence`, `evidence_exports`, and `high_risk_approvals`
  - keeps A/D on session-metadata + output-only TTY trails for brokered maintenance/admin lanes, keeps B metadata-first unless support explicitly enters a stronger terminal lane, keeps C output-only operator trails preferred but richer capture explicit, and prevents accidental new-profile-key drift

- Run `python3 tools/check_operator_access_recording_posture.py` when editing operator-access recording/detail/export posture docs:
  - keeps `docs/617-operator-access-recording-detail-and-export-posture-by-profile.md` wired as a compiled consequence of `operator_access`, `evidence`, `evidence_exports`, and `high_risk_approvals`
  - keeps A/D on session-metadata + output-only TTY trails for brokered remote or approved maintenance operator lanes, keeps B ordinary local admin metadata-first unless a remote/breakglass shell lane is used, keeps C output-only brokered remote-admin trails preferred but local/static-key compatibility explicit, and prevents accidental new-profile-key drift

- Run `python3 tools/check_breakglass_recording_posture.py` when editing breakglass/recovery recording/detail/export posture docs:
  - keeps `docs/618-breakglass-recording-detail-and-export-posture-by-profile.md` wired as a compiled consequence of `installation_recovery`, `evidence`, `evidence_exports`, and `high_risk_approvals`
  - keeps A/D on session-metadata + output-only TTY trails for breakglass shell/console sessions, keeps B breakglass stronger than ordinary local admin while still refusing ambient screen recording, keeps C output-only TTY preferred for Derive-managed breakglass while classic rescue paths stay explicit, and prevents accidental new-profile-key drift

- Run `python3 tools/check_destructive_reprovision_evidence_posture.py` when editing destructive-reprovision evidence/detail/export posture docs:
  - keeps `docs/619-destructive-reprovision-evidence-detail-and-export-posture-by-profile.md` wired as a compiled consequence of `destructive_reprovision`, `installation_recovery`, `evidence`, `evidence_exports`, and `high_risk_approvals`
  - keeps reset proof profile-shaped so A/D retain typed reset/storage truth plus output-only console trails in maintenance lanes while B stays trusted-UI-first and no profile inherits ambient panic recording

- Run `python3 tools/check_firmware_evidence_posture.py` when editing firmware posture, platform provenance, Secure Boot rotation, or firmware evidence/detail/export docs:
  - keeps `docs/621-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md` wired as a compiled consequence of `firmware_updates`, `platform_provenance`, `evidence`, `evidence_exports`, and `high_risk_approvals`
  - keeps `fw.inventory.receipt` + `fw.inventory.diff` routine, keeps `fw.update.receipt` / `uefi.var.set.receipt` authoritative for mutation, and keeps raw vendor logs / efivar blobs / raw Secure Boot databases out of routine baseline export

- Run `python3 tools/check_hw_support_matrix_contract.py` when editing hardware support/admission docs or schemas:
  - keeps `hw.support.matrix` a class-summary-first catalog rather than a live authority lane
  - enforces the `hw.compat.report.support_matrix` join shape and the workstation trusted-UI/recovery finding vocabulary

- Run `python3 tools/check_hw_support_conditions_contract.py` when editing hardware support caveat/limitation docs or schemas:
  - keeps non-fully-supported matrix entries on typed `conditions[]` instead of release-note prose
  - enforces `support_claim.condition_ids`, `support-condition-triggered`, and `matched_condition_ids` wiring so published caveats stay joinable from preflight/support surfaces
  - keeps the accepted boundary wired across the ADR, hardware docs, and canonical examples

- Run `python3 tools/check_hw_support_promotion_contract.py` when editing hardware support promotion or workstation support-floor semantics:
  - keeps positive `hw.support.matrix` entries carrying typed `qualification` summaries
  - enforces the `supported` / `conditional` / `canary-only` stage ladder and the `trusted-ui-basic` / `rollback-or-recovery` evidence floor expectations
  - keeps the promotion boundary wired across the ADR, hardware docs, runbook, and canonical example

- Run `python3 tools/check_hw_support_qualification_receipt_contract.py` when editing hardware support qualification evidence or preflight support-matrix joins:
  - keeps positive support claims receipt-bound through `qualification.receipt_digest` rather than ticket folklore
  - enforces the canonical example join across `hw.support.matrix`, `hw.support.qualification.receipt`, and `hw.compat.report`
  - keeps the receipt boundary wired across the ADR, hardware docs, runbook, and canonical examples

- Run `python3 tools/check_hw_support_qualification_profile_contract.py` when editing hardware support qualification standards or receipt check mapping:
  - keeps positive support claims standard-bound through `qualification.profile_digest` rather than lab-specific playlists
  - enforces the canonical example join across `hw.support.matrix`, `hw.support.qualification.profile`, and `hw.support.qualification.receipt`
  - keeps receipt `check_results[]` keyed to profile `check_id`s with real supporting evidence digests

- Run `python3 tools/check_hw_support_qualification_freshness_contract.py` when editing support-qualification freshness or stale-gate semantics:
  - keeps support qualification freshness typed through profile `max_age_days_by_stage`, receipt `fresh_until`, and receipt `reverify_on`
  - enforces the canonical example join across `hw.support.qualification.profile`, `hw.support.qualification.receipt`, `hw.support.matrix`, and `hw.compat.report`
  - keeps `qualification-stale` wired across the ADR, hardware docs, runbook, and canonical example

- Run `python3 tools/check_hw_support_qualification_status_contract.py` when editing support-qualification lifecycle state or non-current support-proof findings:
  - keeps current positive support claims pointing at an `accepted` receipt rather than historical proof objects
  - enforces `status_effective_at`, typed `reason_code`, and `replacement_receipt_digest` when supersession is published
  - keeps `qualification-superseded` and `qualification-revoked` distinct from `qualification-stale` across the ADR, hardware docs, runbook, and canonical example


- Run `python3 tools/check_hygiene_checkset_completeness.py` when adding, renaming, deleting, or wiring guardrail scripts:
  - keeps every top-level `check_*.py` script referenced exactly once by `tools/hygiene.py`
  - fails stale wrapper entries for deleted or renamed guardrails instead of letting the one-command check drift
  - keeps omitted-checker regressions visible before packaging

- Run `python3 tools/check_generated_docs.py` to ensure generated discovery docs are up to date:
  - checks `docs/412-product-profile-matrix.md`
  - checks `docs/420-context-pack.md` and `docs/_generated/context_pack.json`
  - checks `docs/414-doc-catalog.md` and `docs/_generated/doc_catalog.json`
  - checks `docs/415-risk-register-index.md` and `docs/_generated/risk_register.json`
  - checks `docs/418-artifact-index.md` and `docs/_generated/artifact_index.json`
  - fix by running:
    - `python3 tools/gen_product_profile_matrix.py --write`
    - `python3 tools/gen_context_pack.py --write`
    - `python3 tools/gen_doc_catalog.py --write`
    - `python3 tools/gen_risk_register_index.py --write`
    - `python3 tools/gen_artifact_index.py --write`

- Run `python3 tools/check_validation_logs_clean.py` before packaging or publishing an archive with root validation logs:
  - scans top-level `*.log` files for stale validation-failure markers such as `ERROR:`, `FAIL`, `FAILED`, or Python tracebacks
  - keeps repaired source archives from carrying old red hygiene snapshots that contradict the current `check_run.log`, `hygiene_full.log`, or `checks_tail.log` evidence

- Run `python3 tools/check_version.py` before packaging or publishing a release:
  - keeps `README.md` `Last updated: 2026-05-25r517` and `Version:` aligned with the newest `CHANGELOG.md` entry
  - keeps the key human entry points `docs/00-index.md` and `docs/110-juicy-os-lessons.md` stamped to the same release
  - prevents a top-level archive from advertising one current release while retaining an older release identity tag

- Run `python3 tools/check_risk_register.py` when editing the open questions/risk register:
  - enforces that each numeric item in `docs/266-open-questions-and-risk-register.md` contains an explicit `Risk:` line

- Run `python3 tools/check_risk_register_heading_ids.py` when editing or renumbering the open questions/risk register:
  - enforces that each `## <id>)` item heading in `docs/266-open-questions-and-risk-register.md` has a unique stable id
  - allows explicit suffixed insertions such as `22a`, `62a`, or `67a` instead of reusing an existing numeric id
  - keeps generated risk/context indexes from silently forking one item identity into multiple topics

- Run `python3 tools/check_schema_kind_matches_filename.py` when adding or renaming dotted-kind schemas:
  - enforces that schemas with dotted `kind` names (e.g. `mirror.import.receipt`) keep a stable filename mapping (e.g. `spec/mirror.import.receipt.schema.json` for kind `mirror.import.receipt`)
  - prevents quiet drift where docs/tooling refer to one kind while the schema declares another

- Run `python3 tools/check_spec_example_coverage.py` when adding or refactoring artifacts:
  - ensures each critical artifact schema (plan/receipt/event/report/registry/diff) has a matching example in `spec/examples/`

- Run `python3 tools/check_product_profiles.py` when changing A–D defaults or wording around their hard boundaries:
  - keeps profile-shaped defaults (runtime, hardware compatibility, network topology, device authority, installation/recovery, kernel mutation, operator access, media/USB, firmware updates, networking, support, key use, home state, recovery, data at rest, trustworthy time, platform provenance, export, trust bundles, workload identity) stable and reviewable

- If `tools/check_remote_assistance_recording_posture.py` fails, keep remote assistance evidence profile-shaped: restore `docs/616-remote-assistance-recording-detail-and-export-posture-by-profile.md`, keep it a compiled consequence of `remote_assistance`, `evidence`, `evidence_exports`, and `high_risk_approvals` instead of a new profile key, keep A/D on session metadata plus output-only TTY trails in brokered maintenance/admin lanes, keep B metadata-first unless support explicitly enters a stronger terminal lane, and keep C output-only operator trails preferred while richer capture stays explicit.

- If `tools/check_operator_access_recording_posture.py` fails, keep operator-access evidence profile-shaped: restore `docs/617-operator-access-recording-detail-and-export-posture-by-profile.md`, keep it a compiled consequence of `operator_access`, `evidence`, `evidence_exports`, and `high_risk_approvals` instead of a new profile key, keep A/D on session metadata plus output-only TTY trails in brokered remote or approved maintenance operator lanes, keep B ordinary local admin metadata-first unless a remote/breakglass shell lane is used, and keep C output-only brokered remote-admin trails preferred while local/static-key compatibility stays explicit.
- If `tools/check_breakglass_recording_posture.py` fails, keep breakglass evidence profile-shaped: restore `docs/618-breakglass-recording-detail-and-export-posture-by-profile.md`, keep it a compiled consequence of `installation_recovery`, `evidence`, `evidence_exports`, and `high_risk_approvals` instead of a new profile key, keep A/D on session metadata plus output-only TTY trails in breakglass shell or approved offline maintenance recovery lanes, keep B breakglass stronger than ordinary local admin while still refusing ambient screen recording, and keep C output-only TTY preferred for Derive-managed breakglass while classic rescue paths stay explicit.

- If `tools/check_destructive_reprovision_evidence_posture.py` fails, keep destructive-reset proof profile-shaped: restore `docs/619-destructive-reprovision-evidence-detail-and-export-posture-by-profile.md`, keep it a compiled consequence of `destructive_reprovision`, `installation_recovery`, `evidence`, `evidence_exports`, and `high_risk_approvals` instead of a new profile key, keep A/D on typed `reset.receipt` + `disk.layout.receipt` truth with output-only TTY trails only when reset actually runs through maintenance/reset consoles, keep B trusted-UI-first with observed disk-identity confirmation and no ambient screen recording, and keep C output-only TTY preferred for Derive-managed remote/reset-console flows while classic installer/admin adapters stay explicit.
- If `tools/check_firmware_evidence_posture.py` fails, keep firmware evidence/detail/export profile-shaped: restore `docs/621-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md`, keep it a compiled consequence of `firmware_updates`, `platform_provenance`, `evidence`, `evidence_exports`, and `high_risk_approvals` instead of a new profile key, keep `fw.inventory.receipt` and `fw.inventory.diff` routine, keep `fw.update.receipt` and `uefi.var.set.receipt` authoritative, and keep raw vendor logs / efivar blobs / raw Secure Boot databases / raw capsule bytes in the stronger side-evidence lane rather than routine export.
- If `tools/check_fw_inventory_diff_bundle_contract.py` fails, restore the official support-handoff drift join: keep `spec/incident.bundle.schema.json` exposing `firmware_inventory_diff` plus `fw_inventory_diff_digest`, keep `spec/examples/incident.bundle.json` binding the real `fw.inventory.diff` example digest, keep `spec/examples/bundle.plan.json` exercising the shared selector, and keep the surrounding docs teaching that official support handoff has a typed place for `fw.inventory.diff` proof instead of drifting back toward screenshots or dashboard comparisons.
- If `tools/check_boot_bless_bundle_contract.py` fails, restore the official support-handoff boot-finalization join: keep `spec/incident.bundle.schema.json` exposing `boot_bless_receipts` plus `boot_bless_receipt_digests`, keep `spec/examples/incident.bundle.json` binding the real `boot.bless.receipt` example digest, keep `spec/examples/bundle.plan.json` exercising the shared selector, and keep the surrounding docs teaching that official support handoff has a typed place for `boot.bless.receipt` proof instead of drifting back toward loader counters, greenboot status text, or updater prose.
- If `tools/check_uefi_var_set_bundle_contract.py` fails, do not solve it by stuffing BootOrder/Secure-Boot mutation proof into `incident.bundle.includes.extra` or by pretending raw efivar dumps are the bundle truth; re-thread `docs/216-incident-snapshots-and-support-bundles.md`, `docs/321-firmware-updates-and-uefi-variables-as-evidence.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/621-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md`, and `docs/630-incident-bundles-carry-uefi-var-set-proof-by-digest.md` until official support handoff can carry `uefi_var_set_receipt_digests` on the typed bundle contract.
- If `tools/check_fw_update_bundle_contract.py` fails, do not solve it by stuffing firmware-update proof into `incident.bundle.includes.extra` or by pretending updater dashboards are the bundle truth; re-thread `docs/216-incident-snapshots-and-support-bundles.md`, `docs/321-firmware-updates-and-uefi-variables-as-evidence.md`, `docs/417-platform-provenance-and-firmware-lifecycle-as-derived-ops.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, `docs/621-firmware-inventory-and-mutation-evidence-detail-and-export-posture-by-profile.md`, and `docs/631-incident-bundles-carry-fw-update-proof-by-digest.md` until official support handoff can carry `fw_update_receipt_digests` on the typed bundle contract.
- If `tools/check_secret_bundle_contract.py` fails, do not solve it by stuffing provider screenshots or secret-manager notes into `incident.bundle.includes.extra`; re-thread `docs/216-incident-snapshots-and-support-bundles.md`, `docs/223-secrets-and-key-management-as-evidence.md`, `docs/253-bundle-plans-and-deterministic-exports.md`, `docs/481-support-bundle-contract-and-timeline-first-handoff.md`, and `docs/637-incident-bundles-carry-secret-state-and-action-proof-by-digest.md` until official support handoff can carry `secret_snapshot_digest` + `secret_receipt_digests` as typed secret-state/action proof.

If `tools/check_trust_bundle_apply_boundary.py` fails, keep `pki-trust-bundle` authoritative, keep `pki.trust.bundle.diff` as the review surface, and keep `pki.trust.bundle.apply.receipt` as the typed proof of the exact served trust view; re-thread `docs/228-pki-and-identity-lifecycle-as-evidence.md`, `docs/304-trust-bundles-and-ca-injection-as-artifacts.md`, `docs/434-pki-trust-bundle-diff-as-review-surface.md`, and `docs/622-trust-bundle-apply-receipts-bind-canonical-bundles-to-runtime-views.md` until `pki-event` can still point at the exact apply proof without turning renderers or distributors into the real authority.

If `tools/check_trust_bundle_apply_bundle_contract.py` fails, keep official support handoff digest-first: restore `docs/624-incident-bundles-carry-trust-bundle-apply-proof-by-digest.md`, keep `pki_trust_bundle_digest` for the reviewed canonical bundle, keep `pki_trust_bundle_apply_receipt_digests` for exact served trust-view proof, and do not let incident bundles fall back to renderer-specific trust dumps, control-plane screenshots, or `extra` folklore.
If `tools/check_pki_issue_bundle_contract.py` fails, keep official support handoff digest-first for PKI action proof too: restore `docs/638-incident-bundles-carry-pki-issuance-proof-by-digest.md`, keep `pki_issue_receipt_digests` as the typed place for exact PKI issuance / renewal / install / revoke proof, and do not let incident bundles fall back to CA dashboards, ACME logs, or ticket prose.
If `tools/check_attestation_bundle_contract.py` fails, keep official support handoff digest-first for measured posture too: restore `docs/639-incident-bundles-carry-attestation-proof-by-digest.md`, keep `boot_attestation`, `attestation_reference`, and `attestation_receipts` on the shared bundle-plan/include surface, keep `boot_attestation_digest`, `attestation_reference_digest`, and `attestation_receipt_digests` as the typed place for exact measured posture proof, and do not let incident bundles fall back to verifier dashboards, portal screenshots, or ticket prose.

If `tools/check_attestation_reference_variance_contract.py` fails, keep routine attestation references cohort-shaped and `manifest-replay-first`: restore `docs/640-attestation-reference-scope-and-variance-boundary.md`, keep `scope.kind` and `boot.variance.mode` explicit in `spec/attestation.reference.schema.json`, keep the canonical example out of `strict_pcr_values`, and do not let deployment/host exceptions decay into an anti-snowflake per-host allowlist database.

If `tools/check_attestation_reference_exception_contract.py` fails, keep non-baseline measured-boot references timeboxed and approval-shaped: restore `docs/641-attestation-reference-exceptions-stay-timeboxed-and-approval-shaped.md`, keep `attestation.reference.exception` required for deployment/host or mixed/strict-PCR references, keep `exception.expires_at` and `exception.approvals` present, and do not let verifier-side databases or ticket notes become the real exception authority.

If `tools/check_attestation_reference_renewal_contract.py` fails, keep renewed measured-boot exceptions digest-linked and successor-shaped: restore `docs/642-attestation-reference-renewals-stay-digest-linked-and-successor-shaped.md`, keep `exception.renewal_posture` required, keep `supersedes-prior-exception` joined to `exception.supersedes_reference_digest`, and do not let verifier row ordering, reused IDs, or in-place expiry extension become the real renewal contract.

If `tools/check_attestation_reference_selection_contract.py` fails, keep measured-boot reference choice exact-digest-pinned and no-latest-wins: restore `docs/643-attestation-reference-selection-stays-exact-digest-pinned-and-no-latest-wins.md`, keep `scope.selector` as discovery metadata rather than precedence, keep `attestation.receipt.reference_digest` as the exact reviewed reference answer, and do not let selector overlap, latest-matching selector, or verifier-side named-policy rows become the real contract.

If `tools/check_event_seal_bundle_contract.py` fails, keep official support handoff digest-first for event integrity too: restore `docs/625-incident-bundles-carry-event-seal-proof-by-digest.md`, keep bounded `event_segments` as the window selector, keep `event_seal_receipt_digests` as the exact seal proof for that window, and do not let incident bundles fall back to verifier-private output, screenshots, or `extra` folklore.

- Run `python3 tools/check_version.py` before committing if you touched discovery surfaces or version stamps:
  - ensures README + docs/00-index + docs/110 last-updated tags match the newest CHANGELOG entry

- Run `python3 tools/lint_spec_schemas.py` when touching `spec/` schemas:
  - checks schema convention drift (kind/version/id/timestamp fields; catches copy/paste errors)

- Run `python3 tools/validate_spec_examples.py` when touching `spec/`:
  - validates examples under `spec/examples/` against schemas under `spec/`
  - catches schema/example drift early
  - if an example is intended as a long-lived contract, add a matching schema (even a thin `$ref` wrapper)
  - if you want multiple long-lived variants for a single contract, suffix the example filename (e.g. `microvm.stop.receipt.denied.json`) **and** add a matching wrapper schema (e.g. `spec/microvm.stop.receipt.denied.schema.json`) that `$ref`s the base schema and pins the variant semantics

## Document lifecycle

- `rfcs/` = debate + iteration
- `adrs/` = decisions (append-only)
- `docs/` = current truth (concise, updated when ADR lands)

- Run `python3 tools/check_hw_support_qualification_target_scope_contract.py` when editing support-qualification target scope, `release_train`, or target-mismatch findings:
  - keeps support proof bound to explicit `target_binding` instead of floating across release trains or boot-manifest lineages
  - enforces the canonical example join across `hw.support.matrix`, `hw.support.qualification.profile`, `hw.support.qualification.receipt`, and `hw.compat.report` for `qualification-target-mismatch`

- Run `python3 tools/check_workstation_graphics_boundary.py` when editing workstation graphics/GUI boundary docs:
  - keeps the host-owned composition + software-first guest GUI decision wired through desktop viability, host/AppVM boundary, device authority, risk, and runbook surfaces
  - prevents graphics/GUI boundary drift back into ambient host display-server or GPU authority folklore
- Run `python3 tools/check_workstation_session_surface_boundary.py` when editing the workstation session-surface boundary:
  - keeps the session-surface boundary wired through desktop viability, host/AppVM boundary, risk, and runbook surfaces
- Run `python3 tools/check_workstation_datatransfer_boundary.py` when editing workstation clipboard/file-transfer boundary docs or schemas:
  - keeps the no-ambient-shared-clipboard floor wired through desktop viability, host/AppVM boundary, risk, runbook, and README surfaces
  - keeps `ui.datatransfer` explicit about single-delivery posture instead of leaving it to broker folklore
- Run `python3 tools/check_workstation_uri_open_boundary.py` when editing workstation URI-opening boundary docs:
  - keeps `http` / `https` on the designated browsing compartment and `file://` out of the cross-domain URI lane
  - keeps URI opening intent-routed, compartment-preserving, and off the ambient host-browser fallback path
- Run `python3 tools/check_workstation_file_open_boundary.py` when editing workstation file-open/import boundary docs or route/role schemas:
  - keeps cross-compartment document open/view/edit import-shaped first and route-shaped second instead of slipping back into host-open or generic “open with…” folklore
  - keeps the small `document_viewing` / `document_editing` role pair and `intent.route.receipt.import_receipt_digest` wired through the workstation/support/archive surfaces
- Run `python3 tools/check_workstation_document_edit_boundary.py` when editing workstation imported-document mutation posture docs or document-route examples:
  - keeps the imported-document view-first / working-copy boundary wired through the workstation/risk/runbook/archive surfaces
  - keeps the archive on **work on a copy** rather than silently reintroducing **edit the imported original in place** as the baseline
- Run `python3 tools/check_workstation_document_viewing_posture.py` when editing workstation foreign-document viewing posture docs or document-view examples:
  - keeps the imported-document disposable-first viewing posture wired through the workstation/risk/runbook/archive surfaces
  - keeps the archive from silently reintroducing persistent-viewer fallback as the baseline for foreign imported originals
- Run `python3 tools/check_workstation_sanitized_ocr_boundary.py` when editing sanitized-document OCR/searchable derivative docs or `content.ocr-inspection.*` schemas/examples:
  - keeps flat visual sanitized output as the default inspection artifact, searchable/OCR output as an explicit secondary derivative, and baseline authoring narrower than convenience-driven OCR drift (`tools/check_workstation_sanitized_ocr_boundary.py`)

- Run `python3 tools/check_workstation_sanitized_ocr_index_boundary.py` when editing sanitized-document OCR/searchable derivative docs or `content.ocr-inspection.*` schemas/examples:
  - keeps local viewer search bounded to the disposable inspection lane, keeps ambient host/global indexing forbidden by default, and prevents detached text sidecars from quietly becoming the real searchable artifact (`tools/check_workstation_sanitized_ocr_index_boundary.py`)

- Run `python3 tools/check_workstation_ocr_text_egress_boundary.py` when editing OCR-searchable inspection egress wording, `content.ocr-inspection.*.boundary`, or `ui.datatransfer.*` provenance joins:
  - keeps `text_egress_default = explicit-datatransfer-only`, `clipboard_mime_default = text/plain;charset=utf-8`, and `rich_text_transfer_by_default = false` on the OCR inspection boundary, and keeps `ui.datatransfer.*.content_source` available for provenance-carrying OCR text transfer receipts (`tools/check_workstation_ocr_text_egress_boundary.py`)
- Run `python3 tools/check_workstation_datatransfer_subject_exactness.py` when editing workstation transfer evidence docs or `ui.datatransfer.*` schemas/examples:
  - keeps transfer evidence actor-exact by requiring `offer_source_subject` on grants/receipts, preserving the rule that `subject` stays the current holder/recipient side, and keeping the OCR inspection example wired as document-viewer → notes instead of direction folklore (`tools/check_workstation_datatransfer_subject_exactness.py`)
- Run `python3 tools/check_workstation_datatransfer_grant_digest_join.py` when editing workstation transfer evidence docs or `ui.datatransfer.receipt` schemas/examples:
  - keeps transfer receipts exact-join shaped by requiring `grant_digest`, preserving the rule that detached tooling should answer which exact grant artifact governed the crossing instead of reconstructing policy from `offer_id` / `lease_id` folklore (`tools/check_workstation_datatransfer_grant_digest_join.py`)
- Run `python3 tools/check_workstation_datatransfer_single_delivery_exhaustion.py` when editing workstation transfer recovery wording or `ui.datatransfer.*` schemas/examples:
  - keeps the ordinary transfer lane one-shot by requiring `grant_exhausted`, preserving the rule that the first successful read-side transfer exhausts the grant, and keeping recovery on fresh grant / re-offer rather than replay/history folklore (`tools/check_workstation_datatransfer_single_delivery_exhaustion.py`)
- Run `python3 tools/check_workstation_datatransfer_first_richer_rfc_target.py` when editing richer workstation transfer intake/prioritization docs or the first richer-lane RFC draft:
  - keeps the next richer-lane queue pointed at the reviewed finite collection handoff RFC, preserving the rule that richer-lane work should start from a session-bounded, read-only-first finite selected-set handoff instead of reopening ordinary `ui.datatransfer.*` or jumping straight to persistent tree authority (`tools/check_workstation_datatransfer_first_richer_rfc_target.py`)
  - keeps the first richer finite-collection cut read-only only, preserving the rule that writable receive is not part of the first cut and must come back as a separate later RFC/ADR decision (`tools/check_workstation_datatransfer_collection_readonly_first.py`)
- Run `python3 tools/check_workstation_datatransfer_finite_collection_autostop.py` when editing the first richer-lane RFC or its surrounding queueing docs:
  - keeps the first richer finite-collection handoff cut single-retrieve by default and auto-stop after the first successful retrieve, preserving the narrow first-cut replay posture instead of letting repeated-retrieve convenience sneak in by drift (`tools/check_workstation_datatransfer_finite_collection_autostop.py`)
- Run `python3 tools/check_workstation_datatransfer_collection_snapshot_posture.py` when editing the first richer-lane RFC, its queueing docs, or any prose that says “selected folder” / “directory member”:
  - keeps the first richer finite-collection handoff honest by requiring snapshot-shaped reviewed membership instead of live tree traversal or persistent directory authority (`tools/check_workstation_datatransfer_collection_snapshot_posture.py`)
- Run `python3 tools/check_workstation_datatransfer_collection_manifest_posture.py` when editing the first richer-lane RFC, its queueing docs, or any prose that explains reviewed collection membership: 
  - keeps the first richer finite-collection handoff manifest-first by requiring an explicit per-member manifest and treating tree/collection digests as supplementary summary evidence instead of the only reviewed membership surface (`tools/check_workstation_datatransfer_collection_manifest_posture.py`)
- Run `python3 tools/check_workstation_datatransfer_collection_member_kind_floor.py` when editing the first richer-lane RFC, its queueing docs, or any prose that explains reviewed member kinds:
  - keeps the first richer finite-collection handoff regular-files-plus-explicit-directories only and blocks drift into symlink-following, symlink-preserving, or special-object semantics inside the first cut (`tools/check_workstation_datatransfer_collection_member_kind_floor.py`)
- Run `python3 tools/check_workstation_datatransfer_collection_manifest_field_floor.py` when editing the first richer-lane RFC, its queueing docs, or any prose that explains the per-member review surface:
  - keeps the first richer finite-collection handoff content-identity-first and stat-light by requiring normalized review path + member kind for every entry and exact payload digest + exact byte length for regular files (`tools/check_workstation_datatransfer_collection_manifest_field_floor.py`)
- Run `python3 tools/check_workstation_datatransfer_collection_result_root_receipt.py` when editing the first richer-lane RFC, its queueing docs, or any prose that explains successful retrieve/materialization:
  - keeps the first richer finite-collection handoff requiring successful retrieve receipts to pin the exact created fresh root instead of collapsing result evidence back to parent hints or pathless success prose (`tools/check_workstation_datatransfer_collection_result_root_receipt.py`)
- Run `python3 tools/check_workstation_datatransfer_collection_placement_hint_posture.py` when editing the first richer-lane RFC, its queueing docs, or any prose that explains destination placement or chooser UX:
  - keeps parent chooser, destination label, suggested folder, or save-into prompts receiver-local advisory UI state instead of letting the first richer finite-collection handoff quietly become reviewed sender-directed placement authority (`tools/check_workstation_datatransfer_collection_placement_hint_posture.py`)
- Run `python3 tools/check_workstation_datatransfer_collection_result_root_locator_posture.py` when editing the first richer-lane RFC, its queueing docs, or any prose that explains successful retrieve/result evidence:
  - keeps the exact created fresh root joined through a receiver-local stable result-root handle and prevents mutable path text or display snapshots from becoming the authoritative local result locator (`tools/check_workstation_datatransfer_collection_result_root_locator_posture.py`)
- Run `python3 tools/check_workstation_working_copy_contract.py` when editing workstation working-copy schemas, edit-route joins, or related docs:
  - keeps the working-copy receipt / edit-route join boundary wired through workstation/risk/runbook/archive surfaces
  - keeps allowed `document_editing` routes evidence-bound to `content.working-copy.receipt` instead of path folklore
- Run `python3 tools/check_workstation_working_copy_save_boundary.py` when editing the imported-document authoring/save boundary:
  - keeps the working-copy save-scope / no-implicit-writeback boundary wired through workstation/risk/runbook/archive surfaces
  - keeps `content.working-copy.*.boundary.default_save_target = working-copy-output` and `source_writeback = separate-act-required` from drifting back into editor folklore
- Run `python3 tools/check_workstation_reintegration_boundary.py` when editing the imported-document source-lineage/reintegration boundary:
  - keeps the working-copy reintegration / successor-candidate boundary wired through workstation/risk/runbook/archive surfaces
  - keeps `content.reintegrate.*` on the `local-successor-candidate` / `replace_in_place = forbidden` / `upstream_finalize = separate-adapter-required` floor instead of letting app/cloud versioning folklore become the source of truth
- Run `python3 tools/check_workstation_candidate_snapshot_boundary.py` when editing successor-candidate immutability or reintegration-follow-on docs:
  - keeps the immutable-candidate / resnapshot boundary wired through workstation/risk/runbook/archive surfaces
  - keeps `content.reintegrate.*.boundary.candidate_snapshot = immutable` and `later_edits = new-candidate-required` from drifting back into moving-file-pointer folklore
  - keeps stale supersession denials carry observed current-head evidence (`observed_current_receipt_digest`, `observed_current_candidate_digest`) plus `fresh-explicit-supersession-required` instead of a generic stale error (`tools/check_workstation_candidate_stale_denial_boundary.py`)

- Run `python3 tools/check_workstation_candidate_supersession_boundary.py` when editing multi-candidate reintegration semantics or `content.reintegrate.*` docs/schemas:
  - keeps the explicit-candidate-supersession / no-latest-wins boundary wired through workstation/risk/runbook/archive surfaces
  - keeps candidate-to-candidate replacement explicit through `supersedes_receipt_digest` instead of newest-wins folklore

- Run `python3 tools/check_workstation_candidate_same_origin_boundary.py` when editing candidate-supersession scope/evidence semantics or `content.reintegrate.*` docs/schemas:
  - keeps the same-origin candidate-supersession boundary wired through workstation/risk/runbook/archive surfaces
  - keeps `supersession_scope = same-authoritative-origin-only`, `superseded_candidate_digest`, and `superseded_authoritative_origin_digest` from drifting back into cross-origin or under-specified supersession folklore

- Run `python3 tools/check_workstation_candidate_stale_target_boundary.py` when editing candidate-supersession freshness/race semantics or `content.reintegrate.*` docs/schemas:
  - keeps the current-head exact candidate-supersession boundary wired through workstation/risk/runbook/archive surfaces
  - keeps `supersession_target_posture = current-unsuperseded-candidate-only` and `stale_target_handling = fail-closed` from drifting back into stale supersession attempts fail closed instead of drifting back into stale-target rebinding or retroactive lineage folklore
- Run `python3 tools/check_workstation_candidate_retry_recovery_boundary.py` when editing stale-supersession recovery joins or `content.reintegrate.*` docs/schemas:
  - keeps stale-supersession recovery denial-joined and head-pinned through workstation/risk/runbook/archive surfaces
  - keeps `recovery.mode = from-stale-supersession-denial`, `stale_denial_receipt_digest`, and `expected_current_*` from drifting back into generic retry folklore or ambient storage rediscovery
- Run `python3 tools/check_workstation_intent_role_boundary.py` when editing workstation chooser/default-app or intent-role boundary docs:
  - keeps chooser/default-app behavior on trusted host-managed roles instead of arbitrary handler discovery
  - enforces `target_role` / `resolution_mode` wiring so route receipts explain how the target was selected
  - prevents first-open prompts from silently rewriting role defaults from untrusted context
- Run `python3 tools/check_workstation_role_binding_contract.py` when editing workstation remembered-role/default state docs or schemas:
  - keeps remembered chooser/default state in typed `intent.role.binding` objects instead of ambient desktop registries
  - enforces `role_binding_digest` wiring so route receipts can prove which remembered state snapshot they used
- Run `python3 tools/check_workstation_role_binding_diff_contract.py` when editing remembered-role/default drift wiring:
  - keeps `intent.role.binding.diff` as the compact review surface instead of raw settings blobs or desktop-registry deltas
  - keeps drift-bundle / evidence-spine / workstation wiring jumpable from one canonical diff doc
- Run `python3 tools/check_workstation_role_binding_event_contract.py` when editing remembered-role/default mutation evidence wiring:
  - keeps `intent.role.binding.event` as the durable remembered-role mutation trace instead of shell-history or GUI-settings folklore
  - keeps structured-event-log / support-bundle / workstation wiring jumpable from one canonical event doc
- Run `python3 tools/check_workstation_role_binding_consent_contract.py` when editing remembered-role approval, workstation settings authority, or `intent.role.binding.event` join docs/schemas:
  - keeps interactive workstation remembered-role changes on the generic consent lane (`intent.role.binding.consent.request.profile` + `intent.role.binding.consent.receipt.profile`)
  - enforces the non-`auto` approval rule and the `intent.role.binding.event` join via `consent_receipt_digest` so trusted settings UI does not drift back into ambient write authority

- If `tools/check_role_binding_policy_contract.py` fails, keep non-interactive remembered-role reconcile on the existing policy lane: restore `docs/545-role-binding-policy-decision-join-for-noninteractive-mutations.md`, `policy_decision_digest` on `intent.role.binding.event`, and the canonical `policy-reconcile` example instead of inventing a shadow admin approval family or pretending a workstation prompt happened.
- If `tools/check_role_binding_import_contract.py` fails, keep support/import remembered-role mutations joined to typed import evidence: restore `docs/547-role-binding-support-import-join-via-content-import-receipt.md`, `import_receipt_digest` on `intent.role.binding.event`, and the canonical `support-import` example instead of letting imported remembered state collapse back into restore logs or path folklore.
- If `tools/check_role_binding_authority_contract.py` fails, keep remembered-role triggers authority-shaped: restore `docs/548-role-binding-authority-lanes-not-invocation-surfaces.md`, remove `admin-cli` from `intent.role.binding.event.trigger`, and keep admin-tool identity in `source.*` instead of inventing a transport-specific trigger lane.
- If `tools/check_role_binding_policy_profile_contract.py` fails, keep non-interactive remembered-role policy exact-mutation-bound: restore `docs/549-role-binding-policy-decisions-bind-exact-mutation.md`, `spec/intent.role.binding.policy.profile.schema.json`, and the canonical role-binding policy-decision example instead of treating `policy_decision_digest` as a vague class-level allowance.
- If `tools/check_role_binding_policy_apply_window_contract.py` fails, keep single-apply remembered-role policy decisions bounded: restore `docs/550-role-binding-policy-decisions-are-short-lived-and-single-apply.md`, keep `must_apply_before` plus `max_successful_events = 1`, and do not let successful remembered-role writes reuse a consumed `policy_decision_digest`.
- If `tools/check_role_binding_policy_instance_identity_contract.py` fails, keep remembered-role policy decisions uniquely issuable: restore `docs/551-role-binding-policy-decisions-need-unique-instance-identity.md`, keep `decision_instance_id`, and do not let separately issued single-apply authorizations for the same tuple collapse to the same digest.
- If `tools/check_role_binding_policy_denial_contract.py` fails, keep remembered-role non-interactive failure semantics typed: restore `docs/552-role-binding-policy-window-denials-need-typed-reasons.md`, keep `policy-expired` and `policy-consumed` on `intent.role.binding.event.reason_code`, and keep the dedicated policy-window denial example instead of flattening expired/spent authorizations into generic `policy-denied`.
- If `tools/check_role_binding_denial_precedence_contract.py` fails, keep remembered-role denial ordering deterministic: restore `docs/553-role-binding-denial-precedence-between-policy-and-precondition.md`, keep policy-window validity ahead of compare-and-swap in the non-interactive lane, and keep `policy-consumed` ahead of `policy-expired` so replay evidence does not decay into mere age.
- If `tools/check_role_binding_policy_consumption_pointer_contract.py` fails, keep remembered-role spent-authority evidence actionable: restore `docs/554-role-binding-policy-consumed-denials-point-to-consuming-event.md`, keep `consumed_by_event_id` on `policy-consumed` denials, and keep support bundles able to point at the earlier successful consuming event instead of reconstructing the winner from timestamps.
- If `tools/check_role_binding_policy_consumption_digest_contract.py` fails, keep remembered-role spent-authority evidence portable: restore `docs/557-role-binding-policy-consumed-denials-carry-consuming-event-digest.md`, keep `consumed_by_event_digest` on `policy-consumed` denials, and keep offline bundles able to verify the exact winner bytes instead of trusting only `consumed_by_event_id`.
- If `tools/check_role_binding_policy_consumption_binding_digest_contract.py` fails, keep remembered-role spent-authority result summaries queryable: restore `docs/558-role-binding-policy-consumed-denials-carry-consuming-binding-digest.md`, keep `consumed_binding_digest` on `policy-consumed` denials, and do not force support/export/retry readers to reopen the winner event body just to learn the resulting binding digest.
- If `tools/check_role_binding_policy_consumption_diff_digest_contract.py` fails, keep remembered-role spent-authority review summaries queryable: restore `docs/559-role-binding-policy-consumed-denials-carry-consuming-diff-digest.md`, keep `consumed_diff_digest` on `policy-consumed` denials, and do not force support/export/retry readers to reopen the winner event body just to learn the earlier winning reviewed diff digest.
- If `tools/check_role_binding_policy_consumption_recovery_contract.py` fails, keep remembered-role retries honest: restore `docs/555-role-binding-policy-consumed-same-mutation-retries-collapse-to-already-applied.md`, keep `already-applied` limited to exact consuming-event tuple matches, and do not let spent-authority denials silently collapse to success without that proof.
- If `tools/check_publish_session_path_prefix_contract.py` fails, keep the typed path floor normalized: restore `docs/582-publish-session-path-prefixes-stay-normalized.md`, keep `published_endpoint.path_prefix` absolute + normalized, and do not let repeated separators or `.` / `..` path segments back into the canonical published endpoint tuple.
- If `tools/check_publish_session_https_url_hint_contract.py` fails, keep outward relay-url hints https-shaped: restore `docs/583-publish-session-relay-url-hints-stay-https-shaped.md`, keep `published_endpoint.url_hint` lowercase `https` scheme + authority-bearing, and do not let userinfo/query/fragment or `http`-scheme drift back into the outward URL hint.
- If `tools/check_publish_session_remote_locator_uri_hint_contract.py` fails, keep relay-side `uri-hint` locators relay-scoped rather than web-shaped: restore `docs/584-publish-session-relay-uri-hint-locators-stay-non-web-shaped.md`, keep `relay.remote_locator.value` URI-shaped but non-web-shaped, and do not let `http` / `https`, userinfo, query, or fragment material turn the relay-side locator back into a second public endpoint URL.
- If `tools/check_publish_session_hostname_contract.py` fails, keep the published endpoint tuple honest at the host field: restore `docs/581-publish-session-published-endpoint-hostnames-stay-host-shaped.md`, keep `published_endpoint.hostname` lowercase + host-shaped, and do not let it smuggle URL syntax, `host:port`, or localhost/loopback text back into the canonical published endpoint tuple.
- If `tools/check_publish_session_authority_join_contract.py` fails, keep the publish-session authority lane singular and trigger-shaped: restore `docs/586-publish-session-authority-joins-follow-trigger.md`, keep `trusted-ui` joined to `consent_receipt_digest`, `policy` joined to `policy_decision_digest`, `operator-session` joined to `operator_session_digest`, and do not let one publish session mix several authority-digest families.
- If `tools/check_publish_session_lease_id_contract.py` fails, keep temporary sharing lease-addressable: restore `docs/587-publish-session-authority-stays-lease-addressable.md`, require `authority.lease_id` in `net.publish.session`, and keep the example plus policy/maintenance-shaped variants naming the bounded share instance directly instead of relying on timestamps or locator folklore.
- If `tools/check_publish_session_support_trigger_contract.py` fails, keep support publication support-peer-shaped: restore `docs/588-publish-session-support-session-triggers-stay-support-peer-shaped.md`, keep `authority.trigger = support-session` bound to `support-peer` + `peer-relay` + `support-session-peer` + `support-session`, and do not let support-session proof justify callback/demo publication or ordinary audience-bound URL shares.
- If `tools/check_publish_session_secret_handoff_authn_mode_contract.py` fails, keep publish-session authn singular: restore `docs/589-publish-session-secret-handoffs-follow-authn-mode.md`, keep `secret_handoff` reserved to `single-use-secret` / `shared-secret`, and do not let `none`, `provider-identity`, `support-session`, or `tailnet-identity` lanes carry a second hidden secret story beside `authn_mode`.
- If `tools/check_publish_session_validation_hint_webhook_only_contract.py` fails, keep publish-session callback verification webhook-only: restore `docs/591-publish-session-validation-hints-stay-webhook-only.md`, keep `audience.validation_hint` limited to `public-webhook`, and do not let non-webhook shares borrow callback-verification prose as a generic note field.
- If `tools/check_publish_session_binding_hint_exactness_contract.py` fails, keep publish-session binding hints lane-exact: restore `docs/592-publish-session-binding-hints-stay-lane-exact.md`, keep `identity_provider_hint` limited to `provider-identity` lanes, keep `recipient_hint` limited to `named-recipients`, and do not let other share classes borrow binding-hint prose as spare metadata.
- If `tools/check_publish_session_diagnostic_artifact_contract.py` fails, keep temporary-sharing envelopes baseline-safe: restore `docs/595-publish-session-diagnostic-artifacts-stay-off-baseline-envelope.md`, keep `evidence.diagnostic_artifact_digests` out of `net.publish.session`, and move richer relay/admin diagnostics onto support/operator/incident evidence joins instead of the compact share envelope.
- If `tools/check_publish_session_notes_contract.py` fails, keep temporary-sharing envelopes note-free: restore `docs/596-publish-session-notes-stay-off-baseline-envelope.md`, keep free-text `evidence.notes` out of `net.publish.session`, and move commentary back onto typed fields or stronger evidence lanes instead of the compact share envelope.
- If `tools/check_publish_session_visible_indicator_contract.py` fails, keep temporary-sharing cues durable: restore `docs/597-publish-session-visible-indicators-stay-durable-until-ended.md`, require typed `evidence.visible_indicator_posture = durable-until-ended`, and do not let a transient toast/banner satisfy the active-share visibility floor.
- If `tools/check_publish_session_revocation_affordance_contract.py` fails, keep temporary-sharing stop/revoke controls same-surface durable: restore `docs/599-publish-session-revocation-affordances-stay-same-surface-durable.md`, require typed `evidence.revocation_affordance_posture = same-surface-durable-until-ended`, and do not let a transient toast action, buried menu, or off-surface detour satisfy the live revoke floor.
- If `tools/check_publish_session_return_path_contract.py` fails, keep temporary-sharing management surfaces reacquirable: restore `docs/600-publish-session-return-paths-stay-trusted-ui-persistent.md`, require typed `evidence.management_return_path_posture = trusted-ui-persistent-until-ended`, and do not let browser back/history luck, a one-shot toast, or route rediscovery stand in for a stable trusted-UI return path while the share is still live.
- If `tools/check_publish_session_management_return_binding_contract.py` fails, keep temporary-sharing management-target identity exact: restore `docs/601-publish-session-management-return-paths-stay-lease-exact.md`, require typed `evidence.management_return_binding = lease-exact`, and do not let the stable trusted-UI return affordance fall back to a generic share home, nearest-current-share view, or successor lease.
- If `tools/check_publish_session_post_end_management_return_contract.py` fails, keep post-end management return lease-exact-ended: restore `docs/602-publish-session-post-end-management-return-stays-lease-exact-ended.md`, require `lifecycle.post_end_management_return_posture = exact-ended-state-if-followed`, and do not let a surviving trusted-UI return path or management deep link fall into a generic share home, successor lease, or blank miss after the bounded share ends.
- If `tools/check_publish_session_post_end_access_contract.py` fails, keep stale temporary-share handles fail-closed after end: restore `docs/598-publish-session-post-end-access-stays-fail-closed.md`, require `lifecycle.post_end_access_posture = explicit-ended-or-fresh-share`, and do not let old copied/share handles silently bind to a successor session, generic launcher, or durable ingress surface.
- If `tools/check_publish_session_terminal_end_condition_contract.py` fails, keep ended bounded-share state terminal-cause exact: restore `docs/603-publish-session-ended-states-stay-terminal-cause-exact.md`, require `lifecycle.terminal_end_condition` whenever `ended_at` is present, keep it absent while `ended_at` is absent, and do not let explicit ended-share state erase the exact bounded end-condition class or its exact terminal cause.
- If `tools/check_publish_session_maintenance_trigger_contract.py` fails, keep reserved maintenance triggers digest-empty: restore `docs/590-publish-session-maintenance-triggers-stay-digest-empty.md`, forbid `consent_receipt_digest` / `policy_decision_digest` / `operator_session_digest` / `support_session_digest` when `authority.trigger = maintenance`, and keep maintenance publication reserved-but-bounded instead of a mislabeled borrowed-digest lane.

- Restore bundle coherence guardrail: `python3 tools/check_restore_bundle_contract.py` will keep official incident/support bundles from losing the typed place for `restore.receipt` proof, by requiring `restore_receipt_digests` when recovery belongs to the support story.
- Support-session bundle coherence guardrail: `python3 tools/check_support_session_bundle_contract.py` will keep official incident/support bundles from losing the typed place for `support.session` proof, by requiring `support_session_digests` when remote assistance belongs to the support story.

- Operator-session bundle coherence guardrail: `python3 tools/check_operator_session_bundle_contract.py` will keep official incident/support bundles from losing the typed place for `operator.session` proof, by requiring `operator_session_digests` when privileged operator access belongs to the support story.
- Breakglass bundle coherence guardrail: `python3 tools/check_breakglass_bundle_contract.py` will keep official incident/support bundles from losing the typed place for `breakglass.receipt` proof, by requiring `breakglass_receipt_digests` when emergency access belongs to the support story.
- Lease-snapshot bundle coherence guardrail: `python3 tools/check_lease_snapshot_bundle_contract.py` will keep official incident/support bundles from losing the typed place for `lease.snapshot` authority context, by requiring `lease_snapshot_digest` when live temporary authority belongs to the support story.

If `tools/check_restore_bundle_contract.py` fails, keep official support handoff digest-first for recovery too: restore `docs/626-incident-bundles-carry-restore-apply-proof-by-digest.md`, keep `restore_receipt_digests` as the typed place for `restore.receipt` proof, and do not let incident bundles fall back to backend-specific restore-job logs, operator memory, ticket notes, or shell archaeology.

If `tools/check_support_session_bundle_contract.py` fails, keep official support handoff digest-first for remote assistance too: restore `docs/627-incident-bundles-carry-support-session-proof-by-digest.md`, keep `support_session_digests` as the typed place for `support.session` proof, and do not let incident bundles fall back to helper dashboards, ticket notes, or chat archaeology.

If `tools/check_operator_session_bundle_contract.py` fails, keep official support handoff digest-first for privileged admin work too: restore `docs/628-incident-bundles-carry-operator-session-proof-by-digest.md`, keep `operator_session_digests` as the typed place for `operator.session` proof, and do not let incident bundles fall back to bastion dashboards, ticket notes, or shell archaeology.
If `tools/check_breakglass_bundle_contract.py` fails, keep official support handoff digest-first for emergency authority too: restore `docs/629-incident-bundles-carry-breakglass-proof-by-digest.md`, keep `breakglass_receipt_digests` as the typed place for `breakglass.receipt` proof, and do not let incident bundles fall back to rescue-shell folklore, ticket notes, or operator memory.
If `tools/check_breakglass_resumption_contract.py` fails, keep breakglass non-sticky: restore `docs/649-breakglass-does-not-silently-reopen-ordinary-attestation-gated-authority.md`, keep `ordinary_resumption_posture = fresh-attestation-after-breakglass-created-at-required` on `breakglass.receipt`, and do not let later ordinary secret/identity lanes reuse pre-breakglass accepted/degraded evidence or treat breakglass as standing ordinary authority.
If `tools/check_breakglass_resumption_join_contract.py` fails, keep post-breakglass ordinary resumption exact-joined: restore `docs/650-post-breakglass-ordinary-resumption-stays-exact-breakglass-digest-joined.md`, keep `attestation_verification.relevant_breakglass_receipt_digest` on ordinary secret/identity receipts when breakglass materially mattered, and do not let “latest breakglass wins” folklore become the real join.

If `tools/check_breakglass_resumption_subject_binding_contract.py` fails, keep post-breakglass ordinary resumption same-host bound: restore `docs/651-post-breakglass-ordinary-resumption-stays-same-host-bound.md`, keep the teaching that joined `breakglass.receipt.session.host_id` must match pinned `attestation.receipt.subject.host_id`, and do not let exact breakglass joins drift into cross-host join folklore.
If `tools/check_breakglass_resumption_temporal_contract.py` fails, keep post-breakglass ordinary resumption time-ordered: restore `docs/652-post-breakglass-ordinary-resumption-stays-time-ordered.md`, keep the teaching that the pinned `attestation.receipt.created_at` is strictly later than the relevant breakglass receipt `created_at`, and do not let the later ordinary receipt predate the pinned attestation receipt.

UEFI-var-set bundle guardrail note: `tools/check_uefi_var_set_bundle_contract.py` keeps the archive from drifting back toward support bundles that can describe Secure Boot / BootOrder / capsule-intent mutation in prose but not carry typed proof, now that official support handoff can carry `uefi_var_set_receipt_digests` and raw efivar dumps remain stronger side evidence instead of bundle truth.
Firmware-update bundle guardrail note: `tools/check_fw_update_bundle_contract.py` keeps the archive from drifting back toward support bundles that can describe staged/applied firmware change in prose but not carry a typed place for `fw.update.receipt` proof, now that official support handoff can carry `fw_update_receipt_digests` and updater dashboards remain stronger side evidence instead of bundle truth.
Time-sync bundle guardrail note: `tools/check_time_sync_bundle_contract.py` keeps the archive from drifting back toward support bundles that can mention trustworthy time in prose but not carry a typed place for `time.sync.receipt` proof, now that official support handoff can carry `time_source_inventory_digest` + `time_sync_snapshot_digest` + `time_sync_receipt_digests` and daemon logs or raw protocol transcripts remain stronger side evidence instead of bundle truth.
Secret bundle guardrail note: `tools/check_secret_bundle_contract.py` keeps the archive from drifting back toward support bundles that can talk about secret health/rotation/materialization in prose but not carry typed secret-state/action proof, now that official support handoff can carry `secret_snapshot_digest` + `secret_receipt_digests` and provider dashboards/screen captures remain stronger side evidence instead of bundle truth.
Firmware/platform drift bundle guardrail note: `tools/check_fw_inventory_diff_bundle_contract.py` keeps the archive from drifting back toward support bundles that can describe reviewed firmware/platform drift in prose but not carry a typed place for `fw.inventory.diff` proof, now that official support handoff can carry `fw_inventory_diff_digest` and screenshots or dashboard comparisons remain side aids instead of bundle truth.
Boot-bless bundle guardrail note: `tools/check_boot_bless_bundle_contract.py` keeps the archive from drifting back toward support bundles that can describe health-gated finalization in prose but not carry a typed place for `boot.bless.receipt` proof, now that official support handoff can carry `boot_bless_receipt_digests` and loader counters or greenboot status text remain side aids instead of bundle truth.
Storage-scrub bundle guardrail note: `tools/check_storage_scrub_bundle_contract.py` keeps the archive from drifting back toward support bundles that can describe degraded pools or scrub outcomes in prose but not carry a typed place for `storage.scrub.receipt` proof, now that official support handoff has a typed place for `storage.scrub.receipt` proof through `storage_scrub_receipt_digests` and `zpool status` transcripts or dashboard screenshots remain side aids instead of bundle truth.

Time degraded-response boundary guardrail note: `tools/check_time_degraded_response_boundary.py` keeps the archive from drifting back toward daemon/UI weak-time folklore, now that `time.requirement.degraded_response` is explicit, `allow-if-proof-fresh` must bind to `time.sync.snapshot.inputs.proof_bundle_digest`, and unsynced time cannot silently continue.

Time source-policy profile-floor guardrail note: `tools/check_time_source_policy_profile_floors.py` keeps the archive from drifting back toward vague per-profile trustworthy-time folklore, now that A/B/C/D have a concrete profile-mapped trustworthy-time floor for source count, protocol mix, quorum, skew, and RTC bootstrap posture.
Removable-media local-fallback guardrail note: `tools/check_removable_media_local_fallback_boundary.py` keeps the archive from drifting back toward vague “USB with prompts” folklore, now that the first imperfect-hardware fallback is explicit: storage-only, session-scoped, read-only-first, quarantine-first, and still out of bounds for raw HID or generic passthrough.
Removable-media local-ingest first-cut guardrail note: `tools/check_removable_media_local_ingest_firstcut.py` keeps the archive from quietly turning that fallback into raw-device-in-jail folklore, now that the first buildable execution floor is explicit too: host-controlled read-only mount, disposable no-network jail, read-only `mount.view` ingest tree, and no raw block-device nodes in the ingest jail.
Removable-media local-fallback filesystem-admission guardrail note: `tools/check_removable_media_local_fs_admission.py` keeps the archive from silently widening that same lane into “mount whatever the host can parse” folklore, now that the first `fstyp`-probed allowlist is explicit: `msdosfs`, `exfat`, `ufs`, and `cd9660`, with `ext2fs` / `ntfs` / `zfs` / `geli` / unknown probe results failing closed in the first cut.
Removable-media local-fallback inert-mount guardrail note: `tools/check_removable_media_local_mount_hardening.py` keeps the archive from quietly reintroducing “just open it from the stick” folklore, now that the first admitted host-local mount must keep `ro,nodev,nosuid,noexec,nosymfollow`, treat the mounted tree as inert input only, and leave side-effect launch metadata as bytes rather than ambient instructions.
Removable-media local-fallback member-kind guardrail note: `tools/check_removable_media_local_member_kind_floor.py` keeps the archive from quietly widening the first ingest walk back into namespace-resolution or special-object folklore, now that `/ingest` must stay physical and root-pinned beneath `/ingest`, admit only regular files plus explicit directories only, fail closed on symlink/device/FIFO/socket semantics, and keep hardlink topology out of scope in the first cut.
Removable-media local-fallback member-path guardrail note: `tools/check_removable_media_local_member_path_normalization.py` keeps the archive from quietly inheriting FAT/exFAT/ISO naming folklore, now that admitted member paths must normalize to relative-clean Unicode NFC text, normalization collisions must fail closed, and the first cut performs no silent auto-rename or source-prefix repair.
Removable-media local-fallback metadata-fidelity guardrail note: `tools/check_removable_media_local_metadata_fidelity_floor.py` keeps the archive from quietly widening the first ingest lane into filesystem-preservation folklore, now that reviewed/import identity must stay path/kind/payload-first, owner/mode/mtime/xattr fidelity stays out of scope in the first cut, and any receiver-local metadata outcomes stay receiver-local realization detail.
Removable-media local-fallback single-subject guardrail note: `tools/check_removable_media_local_single_subject.py` keeps the archive from quietly turning the first ingest lane into a stealth collection-transfer subsystem, now that the lane stays single-selected-subject only, direct multi-member review/import is out of scope in the first cut, and multiple outputs only arise as a deterministic consequence of processing that one selected subject.
Removable-media local-fallback regular-file-only subject guardrail note: `tools/check_removable_media_local_regular_file_subject.py` keeps the archive from quietly widening the first ingest lane from one selected file into directory/tree subject semantics, now that the selected subject stays regular-file-only in the first cut and directories are not selectable import subjects in this lane.
Removable-media local-fallback present-device scope guardrail note: `tools/check_removable_media_local_present_device_scope.py` keeps the archive from quietly turning the first ingest lane into remembered-device or auto-resume folklore, now that approval stays present-device-instance-only in the first cut, physical detach or lease end revokes it, and reattach requires a fresh grant.
Removable-media local-fallback attach-receipt hint guardrail note: `tools/check_removable_media_local_attach_receipt_hints.py` keeps the archive from quietly dropping current-instance evidence or turning advisory attach hints into durable trust, now that the canonical `device.attach.receipt` keeps a finite current-presence hint bundle, marks those hints evidence-only, and keeps same-hints-on-reattach non-authoritative.
Removable-media local-fallback subject-capture guardrail note: `tools/check_removable_media_local_subject_capture.py` keeps the archive from quietly sliding back into live-mounted-path processing, now that once one selected regular file is chosen the first non-browsing step is capture-first into `/work`, later operations consume the captured file, and capture failure or digest mismatch fails closed.
Removable-media local-fallback early-detach guardrail note: `tools/check_removable_media_local_early_detach.py` keeps the archive from quietly carrying removable-medium authority farther than the first lane needs, now that once capture verifies the host should end the medium session, emit `device.detach.receipt`, and let later classify/scan/sanitize work continue without live device presence.
Removable-media local-fallback post-detach fresh-worker guardrail note: `tools/check_removable_media_local_post_detach_worker_reset.py` keeps the archive from quietly claiming early detach while later work still inherits a busy `/ingest` execution context, now that after verified capture and detach the first lane restarts later ops in a fresh disposable worker with `/ingest` absent and no inherited cwd/root/fd references to the old mount.
Lease-snapshot bundle guardrail note: `tools/check_lease_snapshot_bundle_contract.py` keeps the archive from drifting back toward support bundles that can describe live temporary authority in prose but not carry a typed place for `lease.snapshot` authority context, now that official support handoff has a typed place for `lease.snapshot` authority context through `lease_snapshot_digest` and bastion dashboards or operator memory remain side aids instead of bundle truth.
Attestation bundle guardrail note: `tools/check_attestation_bundle_contract.py` keeps the archive from drifting back toward support bundles that can describe measured posture in prose but not carry typed attestation posture proof, now that official support handoff can carry `boot_attestation_digest` + `attestation_reference_digest` + `attestation_receipt_digests` and verifier dashboards or portal screenshots remain side aids instead of bundle truth.

Attestation reference anti-snowflake guardrail note: `tools/check_attestation_reference_variance_contract.py` keeps the archive from drifting back toward routine per-host golden-PCR folklore, now that `attestation.reference` makes `scope.kind` + `boot.variance.mode` explicit, the canonical example stays cohort-shaped and `manifest-replay-first`, and `strict-pcr-only` remains an explicit exception posture instead of the everyday baseline.

Attestation reference exception guardrail note: `tools/check_attestation_reference_exception_contract.py` keeps the archive from drifting back toward verifier-side exception folklore, now that non-baseline references carry `attestation.reference.exception`, exceptions are timeboxed and approval-shaped, and `strict_pcr_values` cannot hide inside the ordinary replay-first baseline.

Attestation reference renewal guardrail note: `tools/check_attestation_reference_renewal_contract.py` keeps the archive from drifting back toward renewed-exception folklore, now that successor renewals carry `exception.renewal_posture`, `supersedes-prior-exception` stays joined to `exception.supersedes_reference_digest`, and renewed references stay new-artifact-plus-predecessor-digest instead of in-place extension.

Binding-hint exactness guardrail: `tools/check_publish_session_binding_hint_exactness_contract.py` keeps binding hints lane-exact so `identity_provider_hint` and `recipient_hint` remain typed audience evidence instead of generic note fields.

- Run `python3 tools/check_publish_session_current_stack_contract.py` whenever you touch the recent `docs/593-*` through `docs/603-*` publish-session cluster or `docs/604-publish-session-current-contract-stack-and-stale-entrypoint-firewall.md`.
- If `tools/check_publish_session_current_stack_contract.py` fails, fix the stale entry surface or current-stack map before shipping the revision.

Workstation transfer collection-manifest-order guardrail note: `tools/check_workstation_datatransfer_collection_manifest_order.py` keeps the archive from letting the first richer finite-collection manifest order drift back toward traversal, click, or locale-sensitive UI order, now that authoritative serialization is fixed as canonical review-path order and duplicate normalized review paths must fail closed.

Workstation transfer collection-review-path-normalization guardrail note: `tools/check_workstation_datatransfer_collection_review_path_normalization.py` keeps the archive from letting the first richer finite-collection review surface drift back toward host-path-cleanup folklore, now that review paths themselves are fixed as collection-relative clean slash-separated Unicode NFC identity paths and collisions after normalization must fail closed.

Workstation transfer collection-top-level-names guardrail note: `tools/check_workstation_datatransfer_collection_top_level_names.py` keeps the archive from letting multi-root naming drift back toward silent broker rename or wrapper-root repair, now that top-level reviewed names themselves are fixed as explicit reviewed state and any collision disambiguation must be reviewed alias state or fail closed.

Workstation transfer collection-ancestor-closure guardrail note: `tools/check_workstation_datatransfer_collection_ancestor_closure.py` keeps the archive from drifting back toward retrieve-time parent reconstruction folklore, now that the authoritative manifest itself is fixed as ancestor-closed and parent directories are explicit reviewed structural state instead of implicit materializer output.

Workstation transfer collection-selected-roots guardrail note: `tools/check_workstation_datatransfer_collection_selected_roots.py` keeps the archive from drifting back toward silent ancestor-wins overlap repair or hidden descendant-selection memory, now that the accepted selected-root set itself is fixed as overlap-free reviewed state.

Workstation transfer collection-profile-scope guardrail note: `tools/check_workstation_datatransfer_collection_profile_scope.py` keeps the archive from drifting back toward “maybe fleet hosts too” ambiguity, now that the first richer finite-collection handoff is fixed as a B/C/D-only lane and A is intentionally kept on rollout/support/import-export/breakglass-shaped answers.

Workstation transfer collection-first-impl-aliasing guardrail note: `tools/check_workstation_datatransfer_collection_first_impl_aliasing.py` keeps the archive from quietly widening the first trusted review surface into a rename/disambiguation UI, now that the first implementation is fixed as fail-closed on top-level basename collisions unless a later RFC explicitly earns typed reviewed alias state.

Workstation transfer collection-review-ui-path-compression guardrail note: `tools/check_workstation_datatransfer_collection_review_ui_path_compression.py` keeps the archive from turning review-surface legibility into hidden source breadcrumbs or a broader tree editor, now that bounded manifest-derived path-compression of deterministic ancestor-only runs is the only accepted compaction move in the first richer lane.

Workstation transfer collection-mime-posture guardrail note: `tools/check_workstation_datatransfer_collection_mime_posture.py` keeps the archive from turning optional MIME hints into mandatory reviewed identity, now that the first richer lane stays path/kind/payload-first and detector or registry output remains descriptive only.

Workstation transfer collection-result-root-receipt guardrail note: `tools/check_workstation_datatransfer_collection_result_root_receipt.py` keeps the archive from drifting back toward parent-hint or pathless-success folklore, now that fresh-rooted retrieve is only considered fully specified when successful receipts pin the exact created fresh root.
Workstation transfer collection-result-root-locator-posture guardrail note: `tools/check_workstation_datatransfer_collection_result_root_locator_posture.py` keeps the archive from drifting back toward mutable-path folklore, now that successful richer-lane retrieve keeps a receiver-local stable result-root handle authoritative and any display-path snapshot advisory only.
Workstation transfer collection-result-root-display-snapshot-continuity guardrail note: `tools/check_workstation_datatransfer_collection_result_root_display_snapshot_continuity.py` keeps the archive from drifting back toward silently rewritten current-location folklore, now that any retrieve-frozen advisory display snapshot on the original richer-lane retrieve stays stable when present.
Workstation transfer collection-result-root-handle-opacity guardrail note: `tools/check_workstation_datatransfer_collection_result_root_handle_opacity.py` keeps the archive from quietly renaming path folklore into a “stable handle,” now that successful richer-lane retrieve keeps the authoritative result-root handle opaque and non-path-shaped.

Workstation data-transfer collection-artifact-family guardrail: `python3 tools/check_workstation_datatransfer_collection_artifact_family_contract.py` will keep the reviewed finite-collection lane on the accepted `ui.collection.handoff.*` stack and stop the RFC/docs/spec surfaces from drifting back into “final family TBD” folklore now that `grant` / `manifest` / `receipt` are fixed.
Workstation transfer collection-artifact-family guardrail note: `tools/check_workstation_datatransfer_collection_artifact_family_contract.py` keeps the archive from letting the first richer finite-collection lane drift back into provisional-family folklore now that `ui.collection.handoff.grant`, `ui.collection.handoff.manifest`, and `ui.collection.handoff.receipt` are the accepted first spec stack.
Workstation transfer collection-example-joins guardrail note: `tools/check_workstation_datatransfer_collection_example_joins.py` keeps the archive from treating the new richer-lane examples as decorative prose, now that `collection_digest` and `grant_digest` in the first `ui.collection.handoff.*` stack are expected to be mechanically computed joins over canonical JSON rather than disconnected placeholder strings.
Reviewed finite-collection current-stack guardrail note: `tools/check_workstation_datatransfer_finite_collection_current_stack_contract.py` keeps the archive from letting the dense `docs/674-*` through `docs/696-*` tightening cluster rot into stale local companion lists now that `docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md` is the canonical current-stack map for implementation-oriented reading.

Package recipe native-step boundary guardrail note: `tools/check_package_recipe_step_boundary.py` keeps the archive from reopening shell-shaped native authority through a generic `run` / `script` step now that the restricted pipeline lane is supposed to stay registry-backed and typed.
Cross-platform identity boundary guardrail note: `tools/check_cross_platform_identity_boundary.py` keeps the archive from turning store paths into target-triple folklore or letting runtime closure truth drift away from explicit `build_platform` / `host_platform` / optional `target_platform` metadata.

Breakglass adapter-detail guardrail note: `tools/check_breakglass_adapter_detail_boundary.py` keeps adapter/runtime detail out of the baseline receipt so `breakglass.receipt` stays adapter-thin, `notes` cannot launder console URLs/session ids/tokens/`ConsoleEntryCommand` values into canonical truth, and richer launch/runtime evidence remains redacted side evidence until a dedicated typed family/RFC exists.
Breakglass adapter-bundle guardrail note: `tools/check_breakglass_adapter_bundle_boundary.py` keeps the archive from quietly promoting richer breakglass adapter/runtime investigation material into the first-class bundle contract before a dedicated typed family exists; official handoff stays authority-first on `breakglass_receipt_digests`, and supplementary side evidence stays second-class.
Breakglass adapter-export-receipt guardrail note: `tools/check_breakglass_adapter_export_receipt_boundary.py` keeps the archive from letting raw attachment ids or portal handles become the portable truth surface for supplementary breakglass adapter/runtime exports; receipt-first when exported is now the rule.
Breakglass adapter-anchor guardrail note: `tools/check_breakglass_adapter_anchor_boundary.py` keeps the archive from letting supplementary breakglass adapter/runtime receipt chains stand alone as portable emergency-access proof; the richer trail stays authority-anchored to exact `breakglass_receipt_digests`.
Breakglass adapter-live-locator guardrail note: `tools/check_breakglass_adapter_live_locator_boundary.py` keeps the archive from letting portable supplementary breakglass adapter/runtime evidence drift onto live console URLs, copied `ConsoleEntryCommand` values, `WebSocketEndpoint` strings, image locators, or session tokens; the portable story stays artifactized.
Breakglass adapter payload-anchor guardrail note: `tools/check_breakglass_adapter_payload_anchor_boundary.py` keeps the archive from letting portable supplementary breakglass adapter/runtime evidence stop at a receipt-only chain; the same story must stay payload-anchored to at least one passive artifact digest or accepted case-object proof.
Breakglass accepted-case-object exactness guardrail note: `tools/check_breakglass_adapter_case_object_exactness_boundary.py` keeps the archive from letting accepted case-object proof collapse into a parent case/ticket/thread/container id; supplementary breakglass payload anchors must stay object-exact on the accepted remote attachment/object/message-part identity.
Breakglass accepted-case-object validator guardrail note: `tools/check_breakglass_adapter_case_object_validator_boundary.py` keeps the archive from dropping a visible revision/version/generation/ETag-like validator when accepted case-object proof is the payload anchor; when the adapter can see a stronger validator for the same accepted remote object, the portable lane stays validator-pinned when visible.
Breakglass accepted-case-object remote-protection guardrail note: `tools/check_breakglass_adapter_case_object_remote_protection_boundary.py` keeps the archive from treating any accepted portal object as durable evidence by implication; when the adapter can see a protection/retention/hold posture for the same accepted remote object, the portable lane stays remote-protection-shaped when visible.
Breakglass accepted-case-object remote-protection exactness guardrail note: `tools/check_breakglass_adapter_case_object_remote_protection_exactness_boundary.py` keeps the archive from satisfying that rule with ambient case/container/bucket policy alone; when the adapter can honestly bind visible protection posture to the same accepted object revision/version, the portable lane must keep that same accepted object revision/version too.
Breakglass accepted-case-object remote-locator continuity guardrail note: `tools/check_breakglass_adapter_case_object_remote_locator_boundary.py` keeps the archive from falling back to parent case/container browse URLs or portal clicking when the adapter can already preserve a safe locator for the same accepted remote object revision/version; live control locators remain forbidden.
Breakglass accepted-case-object metadata-only reverification guardrail note: `tools/check_breakglass_adapter_case_object_reverification_boundary.py` keeps the archive from treating screenshots, portal clicking, or body-download folklore as the canonical follow-up proof when the adapter can later produce typed metadata-only reverification of the same accepted object revision/version on `transport.reverification.receipt`.

Breakglass recording activation guardrail note: `tools/check_breakglass_recording_activation_boundary.py` / `check_breakglass_recording_activation_boundary.py` keeps breakglass TTY proof from starting late; the first prompt must already be covered by recording that starts at session open.
Breakglass repair-outcome guardrail note: `tools/check_breakglass_repair_outcome_boundary.py` / `check_breakglass_repair_outcome_boundary.py` keeps closeout truth on `breakglass.receipt.repair_outcome` plus authoritative receipts, so session end or notes masquerade as repair proof remains forbidden.
Breakglass method guardrail recovery note: `tools/check_breakglass_method_boundary.py` / `check_breakglass_method_boundary.py` keeps actual emergency session methods concrete and prevents a generic `oob` bucket from becoming the portable session method.
Breakglass bootstrap-join recovery note: `tools/check_breakglass_bootstrap_join_boundary.py` / `check_breakglass_bootstrap_join_boundary.py` keeps `bootstrap_receipt_joins[]` pre-session-recovery-path-only and exact on `boot.override.receipt` / `reset.receipt` digests.
Breakglass bootstrap-sequence recovery note: `tools/check_breakglass_bootstrap_sequence_boundary.py` / `check_breakglass_bootstrap_sequence_boundary.py` keeps plural bootstrap joins earliest-to-latest-pre-session-enabling-only and filters out denied attempts or failed dead ends.
Breakglass bootstrap-actuation recovery note: `tools/check_breakglass_bootstrap_actuation_boundary.py` / `check_breakglass_bootstrap_actuation_boundary.py` keeps the paired one-time-boot story ordered with `boot.override.receipt` before the later `reset.receipt` when both materially enabled entry.
Breakglass adapter-live-locator recovery note: `tools/check_breakglass_adapter_live_locator_boundary.py` keeps portable supplementary breakglass adapter/runtime evidence artifactized rather than live-locator-shaped.
Breakglass accepted-case-object exactness recovery note: `tools/check_breakglass_adapter_case_object_exactness_boundary.py` keeps accepted case-object proof object-exact instead of collapsing to parent case or container folklore.
Release metadata placement guardrail note: `tools/check_version.py` now treats release identity as terminal package metadata too; `README.md` must end with `Last updated: 2026-05-25r517` followed by `Version:`, and `docs/00-index.md` / `docs/110-juicy-os-lessons.md` must end with their current `Last updated: 2026-05-25r517` stamp so append-only compatibility prose cannot hide after the release identity block.
Markdown H1 structure guardrail note: `tools/check_markdown_h1_structure.py` keeps every Markdown file rooted at exactly one first-line H1, so generated discovery maps and human review do not confuse buried titles or legacy section labels for separate documents.

Text final-newline guardrail note: `tools/check_text_files_final_newline.py` keeps line-oriented archive evidence from losing its final record separator; non-empty Markdown, JSON/schema/example, log, Python, YAML, and baseline text artifacts must end with a final newline so shell output, prompts, and adjacent release-stamp excerpts do not visually merge.
Release-heading uniqueness guardrail note: `tools/check_release_heading_uniqueness.py` keeps the discovery map from silently forking one release id into multiple sections, now that `CHANGELOG.md` and `docs/00-index.md` both treat release headings as stable review anchors.

Python tool executable-bit guardrail note: `tools/check_python_tool_executable_bits.py` keeps shebang-bearing Python tool scripts under `tools/` entry points directly executable after extraction; ZIP/package handoff should preserve script mode bits instead of treating runnable guardrails and generators as inert text.

Changelog/index release coverage guardrail note: `tools/check_changelog_index_release_coverage.py` keeps `CHANGELOG.md` and `docs/00-index.md` aligned at the release-heading level so a release cannot remain in the ledger while disappearing from the front-door human index.

Release-heading order guardrail note: `tools/check_release_heading_order.py` keeps `CHANGELOG.md` and `docs/00-index.md` newest-first so release anchors do not become present-but-buried discovery traps.

Index front-matter order guardrail note: `tools/check_index_front_matter_order.py` keeps `docs/00-index.md` usable as the human front door by requiring the project orientation and `## Reading paths` block to appear before the first `## New in ...` release heading.

Numbered-doc identity guardrail note: `tools/check_doc_number_prefix_uniqueness.py` keeps numbered `docs/` prefixes unambiguous as stable review handles; only the explicit legacy `00` and `99` front-door pairs may share a number.

Markdown H2 uniqueness guardrail note: `tools/check_markdown_h2_heading_uniqueness.py` keeps document-local H2 section anchors unique; appendix material should stay under appendix subsections instead of reusing main-body H2 headings.


## Removable-media reviewed process launch context guardrail

`tools/check_removable_media_local_reviewed_process_launch.py` keeps the first removable-media local fallback from drifting back to inherited parent environment, media-derived argv, or inherited cwd authority.
The canonical posture tokens are `reviewed-minimal-env-no-inherited-parent-env`, `launcher-reviewed-argv-no-media-derived-args`, and `launcher-owned-empty-workdir-no-ingest-store-cwd`.
Run it with the rest of `tools/hygiene.py` whenever the removable-media examples, preopen map schema, or startup-context docs change.

## Removable-media executable identity guardrail

`tools/check_removable_media_local_executable_identity.py` keeps the first removable-media local fallback from drifting back to path search, cwd-relative executable lookup, media-derived executable names, unrecorded executable identity, or implicit helper/plugin discovery.
The canonical posture tokens are `launcher-resolved-executable-digest-no-path-search`, `receipt-records-executable-and-wrapper-digests`, and `no-implicit-helper-or-plugin-discovery`.
Run it with the rest of `tools/hygiene.py` whenever the removable-media examples, preopen map schema, or post-detach launcher docs change.

## Removable-media runtime dependency closure guardrail

`tools/check_removable_media_local_runtime_dependency_closure.py` keeps the first removable-media local fallback from drifting back to ambient dynamic-loader search, host-global library resolution, media-derived library paths, or unrecorded runtime dependency closure identity.
The canonical posture tokens are `launcher-pinned-runtime-dependency-closure-no-ambient-loader-search`, `receipt-records-runtime-dependency-closure-digest`, and `no-ld-library-path-cwd-or-media-derived-loader-inputs`.
Run it with the rest of `tools/hygiene.py` whenever the removable-media examples, preopen map schema, executable/wrapper docs, or post-detach launcher docs change.

## Removable-media credential envelope guardrail

`tools/check_removable_media_local_credential_envelope.py` keeps the first removable-media local fallback from drifting back to root/operator credential inheritance, supplementary groups, setuid/setgid or saved-ID regain, ambient privilege regain, or unrecorded worker credential identity.
The canonical posture tokens are `launcher-fixed-unprivileged-credential-envelope-no-supplementary-groups`, `receipt-records-worker-credential-envelope`, `no-supplementary-groups`, and `no-setuid-setgid-saved-id-or-ambient-privilege-regain`.
Run it with the rest of `tools/hygiene.py` whenever the removable-media examples, preopen map schema, executable/runtime closure docs, or post-detach launcher docs change.

## Removable-media worker lifecycle guardrail

`tools/check_removable_media_local_worker_lifecycle.py` keeps the first removable-media local fallback from drifting back to daemonization, orphan descendants, background helper trees, derivative receipts before worker-tree reap, or unreviewed subprocess lifetime.
The canonical posture tokens are `launcher-supervised-no-daemon-or-orphan-descendants`, `receipt-records-worker-exit-and-descendant-reap`, `no-background-descendants-or-unreviewed-subprocesses`, and `launcher-reaps-entire-worker-tree-before-receipt`.
Run it with the rest of `tools/hygiene.py` whenever the removable-media examples, preopen map schema, credential envelope docs, or post-detach launcher docs change.

Removable-media local-fallback post-detach resource-envelope guardrail note: `tools/check_removable_media_local_resource_envelope.py` keeps the archive from quietly treating resource limits as host-local tuning, now that the later worker must record `launcher-enforced-resource-envelope-no-unbounded-worker-consumption`, `receipt-records-resource-envelope-and-observed-usage`, `declared-derivative-output-size-bound-before-receipt`, and `resource-limit-hit-fails-closed-no-derivative-authority` before derivative receipt authority.

Removable-media local-fallback post-detach peer-interaction guardrail note: `tools/check_removable_media_local_peer_interaction.py` keeps the archive from quietly treating peer isolation as host-local folklore, now that the later worker must record `launcher-isolated-peer-envelope-no-ambient-ptrace-signal-or-ipc`, `receipt-records-peer-isolation-and-signal-policy`, `launcher-only-signal-control-no-peer-or-session-control`, `no-unreviewed-ipc-sockets-shm-pipes-or-procfs`, and `procfs-ptrace-and-ktrace-unavailable-to-worker-and-peers` before derivative receipt authority.

Removable-media local-fallback post-detach ambient-input guardrail note: `tools/check_removable_media_local_ambient_input_envelope.py` keeps the archive from quietly treating clock, random, host identity, sysctl, locale, or timezone observations as harmless host defaults, now that the later worker must record `launcher-sealed-ambient-input-envelope-no-worker-clock-random-or-host-identity`, `receipt-records-ambient-input-envelope-and-launcher-owned-timestamps`, `worker-wall-clock-and-timezone-not-derivative-authority`, `no-worker-randomness-or-host-entropy-as-derivative-input`, and `hostname-kernel-sysctl-locale-and-machine-identity-not-derivative-authority` before derivative receipt authority.

Removable-media local-fallback post-detach network-egress guardrail note: `tools/check_removable_media_local_network_egress.py` keeps the archive from quietly treating no-network behavior as host-local folklore, now that the later worker must record `network-egress-absent-no-socket-dns-or-remote-callbacks`, `receipt-records-network-absent-envelope`, `no-dns-mdns-nss-or-resolver-host-input`, `no-proxy-or-remote-service-configuration`, and `no-remote-fetch-or-callback-derivative-authority` before derivative receipt authority.

Removable-media local-fallback post-detach persistent-state guardrail note: `tools/check_removable_media_local_persistent_state.py` keeps the archive from quietly treating durable-state absence as disposable-worker folklore, now that the later worker must record `persistent-state-absent-no-home-cache-or-host-state-writes`, `receipt-records-persistent-state-absence-and-scratch-cleanup`, `launcher-created-empty-scratch-nonauthoritative`, `scratch-destroyed-before-derivative-receipt`, and `no-user-home-cache-config-or-history-state` before derivative receipt authority.

## Removable-media post-detach contract-closure guardrail

`tools/check_removable_media_local_post_detach_contract_closure.py` keeps the first removable-media lane from relying on posture strings alone. It validates `spec/examples/removable.media.local.post_detach.contract.json`, requires invalid fixtures under `spec/examples/invalid/removable-media/post-detach-contract/` to fail, and keeps `schema-backed-positive-and-negative-fixture-guarded`, `receipt-must-bind-freebsd-launch-evidence-to-contract`, and `known-bad-authority-shapes-must-fail-validation` wired through the canonical plan/receipt/preopen/attach/detach examples.

`tools/check_removable_media_local_post_detach_launch_evidence.py` keeps the first removable-media lane from treating FreeBSD backend evidence as log prose. It validates `spec/examples/removable.media.local.post_detach.launch.evidence.json`, requires invalid fixtures under `spec/examples/invalid/removable-media/post-detach-launch-evidence/` to fail, and keeps `typed-freebsd-launch-evidence-positive-and-negative-fixture-guarded`, `sha256:4949494949494949494949494949494949494949494949494949494949494949`, and `known-bad-freebsd-launch-evidence-shapes-must-fail-validation` wired through the contract, plan, receipt, preopen, attach, and detach examples.


## r506 post-detach recovery evidence hygiene

`tools/check_removable_media_local_post_detach_recovery_evidence.py` keeps the first removable-media lane from treating crash cleanup as best-effort prose. It validates `spec/examples/removable.media.local.post_detach.recovery.evidence.json`, requires invalid fixtures under `spec/examples/invalid/removable-media/post-detach-recovery-evidence/` to fail, and keeps `typed-post-detach-recovery-evidence-positive-and-negative-fixture-guarded`, `sha256:5050505050505050505050505050505050505050505050505050505050505050`, and `known-bad-recovery-evidence-shapes-must-fail-validation` wired through the launch evidence, contract, plan, receipt, preopen, attach, and detach examples.


## r507 post-detach query-projection hygiene

`tools/check_removable_media_local_post_detach_query_projection.py` keeps the first removable-media lane from treating receipt search as ambient metadata authority. It validates `spec/examples/removable.media.local.post_detach.query.projection.json`, requires invalid fixtures under `spec/examples/invalid/removable-media/post-detach-query-projection/` to fail, and keeps `typed-post-detach-query-projection-positive-and-negative-fixture-guarded`, `sha256:5656565656565656565656565656565656565656565656565656565656565656`, and `known-bad-query-projection-shapes-must-fail-validation` wired through the recovery evidence, contract, content import plan/receipt, and preopen map.

## Removable-media post-detach export-bundle guardrail

`tools/check_removable_media_local_post_detach_export_bundle.py` keeps the first removable-media lane from treating support or incident handoff as a raw debug bundle. It validates `spec/examples/removable.media.local.post_detach.export.bundle.json`, requires invalid fixtures under `spec/examples/invalid/removable-media/post-detach-export-bundle/` to fail, and keeps `typed-post-detach-export-bundle-positive-and-negative-fixture-guarded`, `sha256:6262626262626262626262626262626262626262626262626262626262626262`, and `known-bad-post-detach-export-bundle-shapes-must-fail-validation` wired through the query projection, recovery evidence, contract, content import plan/receipt, and preopen map.



## r509 removable-media revocation tombstone guardrail

`tools/check_removable_media_local_post_detach_revocation_tombstone.py` keeps `typed-post-detach-revocation-tombstone-positive-and-negative-fixture-guarded` wired through the r508 export bundle, r507 query projection, r506 recovery evidence, r504 contract, content import plan/receipt, and preopen map. Its red corpus proves stale query/export/rehydration, prefix revocation, raw locators, false offline erasure, unbounded tombstones, secret material, and successor authority without a fresh lease fail validation.


`tools/check_removable_media_local_post_detach_denial_receipt.py` keeps `typed-post-detach-denial-receipt-positive-and-negative-fixture-guarded` wired through the r509 tombstone, r508 export bundle, r507 query projection, r506 recovery evidence, r504 contract, content import plan/receipt, and preopen map. Its red corpus proves missing tombstone causality, allowed stale export/rehydration, raw handle/locator leakage, host identity or filename leakage, missing monotonic sequence, unbounded retry, and successor authority without a fresh lease fail validation.

## r511 removable-media fresh-authority guardrail

Run `python3 tools/check_removable_media_local_post_detach_fresh_authority_receipt.py` after touching the removable-media post-detach denial, revocation, query, export, recovery, contract, preopen, or content-import examples. `typed-post-detach-fresh-authority-receipt-positive-and-negative-fixture-guarded` keeps successor authority on a fresh lease and new digest subjects, while `known-bad-post-detach-fresh-authority-receipt-shapes-must-fail-validation` makes known-bad renewal shapes fail validation.

Last updated: 2026-05-25r520
## r512 removable-media fresh-authority consumption guardrail

Run `python3 tools/check_removable_media_local_post_detach_fresh_authority_consumption_receipt.py` after touching the removable-media post-detach fresh-authority, denial, revocation, query, export, recovery, contract, preopen, or content-import examples. `typed-post-detach-fresh-authority-consumption-positive-and-negative-fixture-guarded` keeps a fresh-authority receipt one-shot and successor-artifact-exact, while `known-bad-post-detach-fresh-authority-consumption-shapes-must-fail-validation` makes known-bad consumption shapes fail validation.

### Removable-media post-detach successor-index cutover

Run `python3 tools/check_removable_media_local_post_detach_successor_index_cutover_receipt.py` after touching the removable-media post-detach fresh-authority consumption, query/export/rehydration, recovery, contract, preopen, or content-import examples. `typed-post-detach-successor-index-cutover-positive-and-negative-fixture-guarded` means the r512 successor-index update is a typed cutover receipt; `known-bad-post-detach-successor-index-cutover-shapes-must-fail-validation` keeps old-handle-live, dual-active, orphan/forked successor, raw locator/filename, rollback, full-text, secret-material, and offline-erasure-overclaim shapes red-tested.


### Removable-media post-detach successor-index checkpoint

Run `python3 tools/check_removable_media_local_post_detach_successor_index_checkpoint_receipt.py` after touching the removable-media post-detach cutover, consumption, query/export/rehydration, recovery, contract, preopen, or content-import examples. `typed-post-detach-successor-index-checkpoint-positive-and-negative-fixture-guarded` means the r513 cutover is followed by a typed reader checkpoint; `known-bad-post-detach-successor-index-checkpoint-shapes-must-fail-validation` keeps missing-cutover, non-monotonic, stale-root, old-root-restore, dual-active, unanchored/mutable, raw locator/filename, full-text, secret, and offline-erasure-overclaim shapes red-tested.

- `tools/check_removable_media_local_post_detach_reader_admission_receipt.py` keeps `typed-post-detach-reader-admission-positive-and-negative-fixture-guarded` wired to the r514 checkpoint and rejects known-bad reader-admission shapes.

- `tools/check_removable_media_local_post_detach_reader_use_receipt.py` keeps `typed-post-detach-reader-use-positive-and-negative-fixture-guarded` wired to the r515 reader admission and rejects known-bad reader-use shapes before admitted observations become silent or replayable.

- `tools/check_removable_media_local_post_detach_reader_use_ledger_receipt.py` keeps `typed-post-detach-reader-use-ledger-positive-and-negative-fixture-guarded` wired to the r516 reader-use receipt and rejects known-bad reader-use ledger shapes before concurrent readers can double-spend or roll back observation budget.
- `tools/removable_media_post_detach_guardrail_lib.py` is the first small refactor of the post-detach checker family: new guardrails can share JSON/schema/red-corpus/text assertion helpers instead of copy/pasting them.

- `tools/check_removable_media_local_post_detach_reader_use_ledger_retention_receipt.py` enforces `typed-post-detach-reader-use-ledger-retention-positive-and-negative-fixture-guarded` for the r518 post-detach reader-use ledger retention seam and confirms the helper refactor remains discoverable.
- `tools/check_removable_media_local_post_detach_reader_use_ledger_retention_expiry_receipt.py` enforces `typed-post-detach-reader-use-ledger-retention-expiry-positive-and-negative-fixture-guarded` for the r519 post-detach reader-use ledger retention expiry seam and confirms the shared `require_guardrail_contract` helper remains discoverable.

- `tools/check_removable_media_local_post_detach_reader_use_ledger_retention_expiry_enforcement_receipt.py` enforces `typed-post-detach-reader-use-ledger-retention-expiry-enforcement-positive-and-negative-fixture-guarded` for the r520 post-detach reader-use ledger retention expiry enforcement seam and confirms the shared `require_absent_tokens` helper remains discoverable.


## r521 removable-media runtime state-machine hygiene

Run `python3 tools/check_removable_media_local_post_detach_runtime_state_machine.py` when editing removable-media post-detach state-machine manifests, post-expiry enforcement ledgers, fresh-authority recovery, support projections, backend enforcement evidence, or the r520 production/fixture schema split. The checker validates `runtime-verifiable-post-detach-state-machine-and-post-expiry-ledgers`, computed example digests, lane-family normalization, denial precedence, rate-limit/time-proof joins, successor-only recovery, allowlisted support projection, and FreeBSD backend evidence.

Run `python3 tools/check_readme_latest_cut.py` when editing release front-door text. It keeps the first README `Latest cut:` line synchronized with the newest CHANGELOG entry and newest ADR so humans and LLMs do not start five cuts behind.


## r522 scenario replay and cube schema audit hygiene

Run `python3 tools/check_removable_media_local_post_detach_scenario_replay.py` after editing the removable-media post-detach state machine, expiry enforcement ledger, fresh-authority recovery path, support projection, backend evidence, or scenario replay manifest. The checker enforces `post-detach-scenario-replay-positive-and-negative-fixture-guarded`, recomputes model binding digests through `tools/cube_digest_lib.py`, and proves the replay red corpus fails.

Run `python3 tools/check_cube_schema_audit_report.py` after editing schemas under spec/ or top-level top-level examples under spec/examples/. The checker enforces `cube-schema-audit-report-live-scan-guarded` by rebuilding `spec/examples/cube.schema.audit.report.json` from the live cube and comparing it exactly.

## r523 transition witnesses and hygiene shards

Run `tools/check_removable_media_local_post_detach_transition_witness.py` after changing the post-detach state-machine or replay surfaces. It enforces `transition-witness-capsule-positive-and-negative-fixture-guarded`, recomputes model bindings and outcome digests, and rejects skipped enforcement-ledger commits, non-monotonic steps, raw support visibility, expired-root resurrection, and idempotent replay double-debits.

Run `tools/check_cube_hygiene_checkset_manifest.py` after adding, removing, or renaming any top-level check guardrails guardrail or after editing `tools/hygiene.py`. The `cube-hygiene-checkset-sharded-live-scan-guarded` manifest keeps the full inventory while making `tools/hygiene.py --profile release-critical`, `tools/hygiene.py --profile post-detach`, `tools/hygiene.py --profile generated-surface`, `tools/hygiene.py --profile schema-cube-audit`, and `tools/hygiene.py --profile deep-contract` explicit.


## r524 denial reason registry and schema refactor backlog

Run `tools/check_removable_media_local_post_detach_denial_reason_registry.py` after changing post-detach state-machine, scenario replay, transition witness, enforcement-ledger, fresh-authority recovery, support-projection, or denial receipt surfaces. It enforces `denial-reason-registry-positive-and-negative-fixture-guarded`, recomputes source bindings, checks `lower-rank-wins` precedence, and rejects duplicate ranks, stale bindings, scenario drift, raw support visibility, and subordinate reasons that preempt primary denials.

Run `tools/check_cube_schema_refactor_backlog.py` after changing schemas or `cube.schema.audit.report`. It enforces `cube-schema-refactor-backlog-live-scan-guarded` so every live const-heavy schema has an explicit migration item instead of living only as a descriptive audit count.



## r525 denial selection and contract schema split hygiene

Run `tools/check_removable_media_local_post_detach_denial_selection_receipt.py` after changing the post-detach denial reason registry, scenario replay, transition witness, enforcement ledger, support projection, or rate-limit posture. It enforces `denial-selection-receipt-positive-and-negative-fixture-guarded`, recomputes source bindings, checks `lower-rank-wins` selection, and rejects stale registry bindings, omitted higher-precedence causes, subordinate primary selection, raw support visibility, rate-limit drift, and witness/scenario drift.

Run `tools/check_cube_schema_audit_report.py`, `tools/check_cube_schema_refactor_backlog.py`, and `tools/check_removable_media_local_post_detach_contract_closure.py` after editing `spec/removable.media.local.post_detach.contract.schema.json` or `spec/removable.media.local.post_detach.contract.fixture.schema.json`. The r525 split keeps production validation runtime-shaped while preserving the exact r504 fixture.



## r526 rate-limit debit ledger and reader-use schema split hygiene

Run `tools/check_removable_media_local_post_detach_rate_limit_debit_ledger_receipt.py` after changing the post-detach enforcement ledger, denial-selection receipt, reason registry, scenario replay, transition witness, support projection, or rate-limit posture. It enforces `post-detach-rate-limit-debit-ledger-positive-and-negative-fixture-guarded`, recomputes source bindings, checks first-attempt debit versus idempotent replay no-debit behavior, and rejects CAS mismatch, missing debit, non-advancing roots, policy drift, stale selection bindings, support-visible budget data, and unbounded retry windows.

Run `tools/check_cube_schema_audit_report.py`, `tools/check_cube_schema_refactor_backlog.py`, and `tools/check_removable_media_local_post_detach_reader_use_receipt.py` after editing `spec/removable.media.local.post_detach.reader.use.receipt.schema.json` or `spec/removable.media.local.post_detach.reader.use.receipt.fixture.schema.json`. The r526 split keeps production reader-use validation runtime-shaped while preserving the exact r516 fixture.


## r527 query projection access and query-projection schema split hygiene

Run `tools/check_removable_media_local_post_detach_query_projection_access_receipt.py` after changing the post-detach query projection, support projection, denial selection, rate-limit debit ledger, revocation tombstone, or access-ledger posture. It enforces `post-detach-query-projection-access-positive-and-negative-fixture-guarded`, recomputes source bindings, checks lease/tombstone/allowlisted-field joins, and rejects live subscriptions, aggregate counts, raw/body/path visibility, stale bindings, missing tombstone checks, and non-advancing access roots.

Run `tools/check_cube_schema_audit_report.py`, `tools/check_cube_schema_refactor_backlog.py`, and `tools/check_removable_media_local_post_detach_query_projection.py` after editing `spec/removable.media.local.post_detach.query.projection.schema.json` or `spec/removable.media.local.post_detach.query.projection.fixture.schema.json`. The r527 split keeps production query-projection validation runtime-shaped while preserving the exact r507 fixture.

Last updated: 2026-05-30r530


r528 post-detach export-bundle access guardrail: `check_removable_media_local_post_detach_export_bundle_access_receipt.py` is part of the focused post-detach/release validation path.
- `python3 tools/check_removable_media_local_post_detach_export_bundle_deletion_receipt.py` — validates r529 export-bundle deletion receipts and red corpus.



## r530 terminal closure and denial-receipt schema split hygiene

Run `tools/check_removable_media_local_post_detach_terminal_closure_capsule.py` after changing export deletion, denial selection, support projection, transition witness, scenario replay, or terminal authority posture. It enforces `post-detach-terminal-closure-positive-and-negative-fixture-guarded`, recomputes source bindings, checks future access denial, rejects expired-root resurrection, and keeps offline-copy erasure from being overclaimed.

Run `tools/check_cube_schema_audit_report.py`, `tools/check_cube_schema_refactor_backlog.py`, and `tools/check_removable_media_local_post_detach_denial_receipt.py` after editing `spec/removable.media.local.post_detach.denial.receipt.schema.json` or `spec/removable.media.local.post_detach.denial.receipt.fixture.schema.json`. The r530 split keeps production denial receipt validation runtime-shaped while preserving the exact r510 fixture.

- r531 post-detach terminal-closure access and fresh-authority schema split checks: `check_removable_media_local_post_detach_terminal_closure_access_receipt.py`, `check_removable_media_local_post_detach_fresh_authority_receipt.py`, `check_cube_schema_refactor_backlog.py`.


r532 hygiene addition: `check_removable_media_local_post_detach_terminal_closure_successor_authority_receipt.py` validates the terminal-closure successor-authority receipt, and the reader-admission checker now validates the canonical r515 example against both runtime and exact fixture schemas. Keep using `tools/hygiene.py --profile release-critical`, `tools/hygiene.py --profile post-detach`, and `tools/hygiene.py --profile schema-cube-audit` for interactive cuts.


r533 hygiene addition: `check_removable_media_local_post_detach_terminal_closure_successor_cutover_receipt.py` validates the post-closure successor cutover activation receipt, and the successor-index cutover checker now validates the canonical r513 example against both runtime and exact fixture schemas. Keep running `tools/hygiene.py --profile release-critical`, `tools/hygiene.py --profile post-detach`, and `tools/hygiene.py --profile schema-cube-audit` for interactive cuts.

Last updated: 2026-05-30r533
