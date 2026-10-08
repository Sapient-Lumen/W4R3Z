# rev0874 current overlay commands

Validate the ZIP before extraction:

```bash
python3 scripts/validate_zip_container.py ../EvidenceVault-rev0874-2026.06.18.15.44-verified-gate-execution-snapshot-race-closure.zip
```

After extraction, run the complete overlay gate and live coverage:

```bash
python3 scripts/overlay_gate.py
python3 scripts/canonical_coverage.py --include-recovery --json
```

The gate now verifies the complete source inventory, executes every configured Python check from a private verified snapshot under `-I -S`, and revalidates both source and snapshot before success. Do not use the carried canonical `make gate` surface for this partial overlay.

---

# rev0873 current overlay commands

Validate the ZIP before extraction:

```bash
python3 scripts/validate_zip_container.py ../EvidenceVault-rev0873-2026.06.18.13.42-descriptor-bound-zip-validation-transport-snapshot.zip
```

After extraction, run the complete overlay gate and live coverage:

```bash
python3 scripts/overlay_gate.py
python3 scripts/canonical_coverage.py --include-recovery --json
```

The ZIP validator now binds all checks and the reported digest to one immutable descriptor snapshot, then rechecks the retained source bytes and final path identity. Do not use the carried canonical `make gate` surface for this partial overlay.

---

# rev0872 overlay commands

Validate the linked ZIP before extraction:

```bash
python3 scripts/validate_zip_container.py ../EvidenceVault-rev0872-2026.06.18.11.36-root-swap-closure-path-canonicality.zip
```

After extraction, run the manifest-driven overlay gate:

```bash
python3 scripts/overlay_gate.py
```

Inspect live and rehydratable canonical coverage:

```bash
python3 scripts/canonical_coverage.py --include-recovery --json
```

The rev0872 targeted check can be run directly:

```bash
python3 scripts/validate_root_anchor_path_identity_rev0872.py
```

Exact-byte recovery tools remain verify-only unless explicitly given an external target and `--write`. They now retain the target root identity from canonical-index validation through publication. The inherited canonical `make gate` surface remains incomplete and is not the overlay entrypoint.

---

# rev0871 overlay commands

Validate the delivered ZIP before extraction:

```bash
python3 scripts/validate_zip_container.py ../EvidenceVault-rev0871-2026.06.18.09.42-embedded-digest-recovery-safe-materialization-refactor.zip
```

After extraction, use the overlay gate rather than the inherited canonical Makefile surface:

```bash
python3 scripts/overlay_gate.py
```

Inspect the two new exact recoveries and live availability:

```bash
python3 scripts/recover_indexed_embedded_evidence_rev0871.py --json
python3 scripts/canonical_coverage.py --include-recovery --json
```

The recovery command is verify-only by default. `--write` creates only absent exact paths and uses the shared descriptor-bound no-clobber boundary.

---

# rev0870 active overlay commands

Run from the extracted rev0870 root. These are the live overlay entrypoints; the carried canonical Makefile remains historical and incomplete here.

```bash
# Before extraction, from a directory containing both the ZIP and validator:
python3 scripts/validate_zip_container.py ../EvidenceVault-rev0870-2026.06.18.07.02-hash-oracle-byte-recovery-coverage-snapshot-hardening.zip

# Complete manifest-driven overlay gate:
python3 scripts/overlay_gate.py

# Verify the four exact low-entropy recoveries without writing:
python3 scripts/recover_indexed_low_entropy_constants_rev0870.py

# Live canonical/recovery coverage:
python3 scripts/canonical_coverage.py --include-recovery --json
```

`scripts/recover_indexed_low_entropy_constants_rev0870.py --write` is only for an external tree carrying the same canonical index. It creates absent paths, refuses overwrite, rejects symlink traversal, and verifies final bytes. Do not use `make gate` as the entrypoint for this partial overlay.

---

# rev0869 overlay commands

Validate the linked ZIP **before extraction**:

```bash
python3 scripts/validate_zip_container.py ../EvidenceVault-rev0869-2026.06.18.05.12-local-extra-path-closure-source-snapshot-recovery.zip
```

From the extracted root, run the complete overlay gate:

```bash
python3 scripts/overlay_gate.py
```

Inspect live canonical representation and recovery availability:

```bash
python3 scripts/canonical_coverage.py --include-recovery --json
```

The ZIP validator intentionally rejects all central extra fields and every local
extra field except the exact ZIP64 size record emitted by this builder. This is a
strict EvidenceVault transport profile, not a general ZIP ingestion command.

`make gate` is not supported by this partial overlay.

---

# Overlay commands — rev0868

Validate the linked archive before extraction:

```bash
python3 scripts/validate_zip_container.py ../EvidenceVault-rev0868-2026.06.18.03.22-digest-byte-recovery-zip-container-hardening.zip
```

After extraction, run the full manifest-driven overlay gate:

```bash
python3 scripts/overlay_gate.py
```

Inspect live and rehydratable canonical coverage:

```bash
python3 scripts/canonical_coverage.py --json
python3 scripts/canonical_coverage.py --include-recovery --json
```

Build a deterministic linked ZIP from the extracted root into its parent directory:

```bash
python3 scripts/build_deterministic_zip.py . ../EvidenceVault-rev0868-2026.06.18.03.22-digest-byte-recovery-zip-container-hardening.zip
```

The output name must equal the source-root basename plus `.zip`; the builder refuses output inside the source tree, symlinks, special files, and transient Python caches. The inherited `make gate` surface remains unsuitable for this partial overlay.

---

# Overlay commands — rev0867

Run the manifest-driven gate first:

```bash
python3 scripts/overlay_gate.py
```

Inspect the two distinct availability views:

```bash
python3 scripts/canonical_coverage.py --json
python3 scripts/canonical_coverage.py --include-recovery --json
```

Replay and verify the 16 historical canonical versions:

```bash
python3 scripts/recover_indexed_versions_from_overlay_history.py --json
```

Materialize them into a separate tree carrying the identical canonical index:

```bash
python3 scripts/recover_indexed_versions_from_overlay_history.py \
  --target-root ../canonical-tree --write --require-present
```

The inherited root `MANIFEST.sha256`, rev0826 SPDX inventory, dedupe report,
release manifest, and Makefile are canonical-snapshot surfaces. They do not
describe or operate this partial overlay. Do not use `make gate`; use the overlay
gate and `CHECKS/overlay-manifest.json`. Reports must remain outside the bundle.

---

# Overlay commands — rev0866

Use the manifest-driven gate first:

```bash
python3 scripts/overlay_gate.py
```

It verifies the immutable bundle before and after substantive checks and now rejects a stale or inflated representation profile by recomputing coverage live.

Inspect or replay the exact patch-corpus recovery:

```bash
python3 scripts/recover_indexed_files_from_patches.py --json
python3 scripts/canonical_coverage.py --json
```

To materialize every exact candidate into a separate tree with the same `INDEX/files.csv`:

```bash
python3 scripts/recover_indexed_files_from_patches.py   --target-root ../full-tree --write --require-present
```

The tool never mutates this bundle, never overwrites a non-matching target, and rejects symlinked target ancestry. Five baseline candidates are intentionally reported as revision-divergent in this overlay because newer revisions replaced their bytes.

Do not use `make gate` as the overlay entrypoint: 42 Makefile-referenced scripts are absent. Gate reports must remain outside the bundle, for example:

```bash
python3 scripts/overlay_gate.py --report ../rev0866-overlay-gate-report.json
```

---

# EvidenceVault rev0865 overlay commands — immutable reports and explicit partial coverage

## Full overlay gate

```bash
python3 scripts/overlay_gate.py
```

A successful result proves the carried overlay inventory and configured checks passed. It does not claim canonical completeness. The gate prints the current representation profile: 19 exact, 17 same-path mismatches, and 4,550 missing out of 4,586 canonical index rows.

## Persist a report without changing the bundle

```bash
python3 scripts/overlay_gate.py --report ../rev0865-overlay-gate-report.json
```

The parent directory must already exist. The target must resolve outside the archive root and may not pass through a symlink. Reports are written atomically with mode `0644`.

## Run a selected check

```bash
python3 scripts/overlay_gate.py --check overlay-chain
```

Integrity is automatically added before and after the selected work. The final line is explicitly labeled `NOT A FULL GATE`.

## Inspect the configured plan

```bash
python3 scripts/overlay_gate.py --list
python3 scripts/overlay_gate.py --list --check overlay-chain --json
```

Do not use `make gate` as the overlay entrypoint. The carried Makefile is a canonical-tree surface and references scripts not shipped in this partial overlay.

## Current payload and rights boundary

The exact upstream MCP servers README and adjacent LICENSE are present. The README has a narrow file-level `CC-BY-4.0` conclusion with attribution in `RIGHTS/MCP_SERVERS_README_RECOVERY_REV0865.json`; PACT and the archive remain `NOASSERTION`. StreamFold recovery still requires real external bytes or a full canonical tree.

---

# Overlay commands — rev0864

Use the manifest-driven gate:

```bash
python3 scripts/overlay_gate.py
```

Useful focused forms:

```bash
python3 scripts/overlay_gate.py --list
python3 scripts/overlay_gate.py --check risk-retirement-rev0864
python3 scripts/overlay_gate.py --json
```

The gate executes argument vectors without a shell and reads its required checks from `PATCH_BUNDLE_MANIFEST.json`. The canonical `Makefile` remains a full-tree surface and is not the overlay entrypoint.

Current state: the PACT local license reference is resolved; the root rights decision and all 17 StreamFold payload bytes remain outstanding.

---

# EvidenceVault overlay command surface — rev0863

This ZIP is an overlay/patch artifact, not the full canonical EvidenceVault tree. Do not use `make gate` as the first check for this overlay.

## rev0863 active mission/right/identity command surface

```bash
python3 scripts/validate_overlay_bundle_integrity_rev0848.py
python3 scripts/apply_overlay_stack_rev0850.py --json
python3 scripts/validate_mission_recenter_rights_identity_rev0863.py
python3 scripts/validate_streamfold_archive_payload_search_rev0862.py
```

Use `PATCH_BUNDLE_MANIFEST.json` as the overlay identity entrypoint. Use `RIGHTS/RIGHTS_DECISION_PACKET_REV0863.*` as the next human decision packet. Use the rev0862 archive locator only when actual candidate ZIP/cache/source artifacts are mounted.

The rev0862 proofcore archive search lane remains the active payload-search endpoint:

```bash
python3 PROOFCORE/verifiers/locate_streamfold_payload_archives_rev0862.py --candidate-source /path/to/export.zip --mode minimum --stage-dir /tmp/ev-streamfold-archive-minimum --json
```

Do not add a new proofcore lane unless it admits real candidate bytes, removes a false claim, or directly supports rights/identity/provenance closure.

---

# EvidenceVault overlay command surface — rev0855

This ZIP is an overlay/patch artifact, not the full canonical EvidenceVault tree. Do not use `make gate` as the first check for this overlay.

## Use these checks first

```bash
python3 scripts/validate_overlay_bundle_integrity_rev0848.py
python3 scripts/apply_overlay_stack_rev0850.py --json
python3 scripts/validate_overlay_stack_application_harness_rev0850.py
python3 scripts/validate_mission_alignment_waste_rev0851.py
python3 scripts/validate_snark_origin_proofcore_rev0852.py
python3 scripts/validate_proofcore_frontier_pcd_rev0854.py
python3 scripts/validate_streamfold_sumcheck_lane_rev0855.py
```

## rev0855 streamfold sumcheck lane

```bash
python3 PROOFCORE/verifiers/verify_sumcheck_transcript_rev0855.py --fixture PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0855/fixtures/sumcheck_accept.rev0855.json
python3 PROOFCORE/verifiers/verify_sumcheck_transcript_rev0855.py --fixture PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0855/fixtures/sumcheck_reject_bad_round.rev0855.json --expect-fail
python3 PROOFCORE/verifiers/verify_streamfold_sumcheck_lane_rev0855.py --fixture PROOFCORE/fixtures/accept/ev-streamfold-sumcheck-lane.rev0855.accept.json
python3 PROOFCORE/verifiers/verify_streamfold_sumcheck_lane_rev0855.py --fixture PROOFCORE/fixtures/reject/ev-streamfold-sumcheck-lane.rev0855.reject.json --expect-fail
```

The rev0854 historical checkpoint is replayed by `verify_streamfold_sumcheck_lane_rev0855.py` after reconstructing a rev0854 tree from `PATCHES/rev0854-to-rev0855-overlay.patch` and `PROOFCORE/parent_snapshots/rev0854/`.

A full canonical mount can be checked against the 17-path payload gate with `--candidate-root /path/to/full/canonical/tree`; this overlay itself is expected not to contain those payloads.

---

# EvidenceVault overlay command surface — rev0854

This ZIP is an overlay/patch artifact, not the full canonical EvidenceVault tree. Do not use `make gate` as the first check for this overlay.

## Use these checks first

```bash
python3 scripts/validate_overlay_bundle_integrity_rev0848.py
python3 scripts/apply_overlay_stack_rev0850.py --json
python3 scripts/validate_overlay_stack_application_harness_rev0850.py
python3 scripts/validate_mission_alignment_waste_rev0851.py
python3 scripts/validate_snark_origin_proofcore_rev0852.py
python3 scripts/validate_proofcore_frontier_pcd_rev0854.py
```

## rev0854 proofcore frontier lane

```bash
python3 PROOFCORE/verifiers/verify_proofcore_frontier_rev0854.py --fixture PROOFCORE/fixtures/accept/ev-proofcore-frontier.rev0854.accept.json
python3 PROOFCORE/verifiers/verify_proofcore_frontier_rev0854.py --fixture PROOFCORE/fixtures/reject/ev-proofcore-frontier.rev0854.reject.json --expect-fail
```

The rev0853 transparent PCD lane is now a historical checkpoint. Its exact accept fixture describes the rev0853 tree, so rev0854 replays it by reconstructing rev0853 inside the rev0854 verifier instead of asking operators to run the old exact fixture directly against the changed tree.

---

## Previous rev0853 command surface

# EvidenceVault overlay command surface — rev0853

This ZIP is an overlay/patch artifact, not the full canonical EvidenceVault tree. The root `Makefile` is carried as a canonical-tree surface and many of its recipes reference scripts or payload roots that are intentionally absent from the overlay ZIP. Do not use `make gate` as the first check for this overlay.

## Use these checks first

```bash
python3 scripts/validate_overlay_bundle_integrity_rev0848.py
python3 scripts/apply_overlay_stack_rev0850.py --json
python3 scripts/validate_overlay_stack_application_harness_rev0850.py
python3 scripts/validate_mission_alignment_waste_rev0851.py
python3 scripts/validate_snark_origin_proofcore_rev0852.py
python3 scripts/validate_proofcore_pcd_rev0853.py
```

## Publication status check

```bash
python3 scripts/publication_rights_gate.py --context rev0851-overlay-probe
```

The expected result is refusal, not publication. The current rights ledger remains `publication_blocked_pending_rights_decision`.

## Why this file exists

The overlay has two identities at once: it carries canonical-tree release surfaces for patch application and review, while the ZIP itself is a smaller overlay bundle. This file makes the overlay-local command surface explicit so a future operator does not mistake the carried canonical `Makefile` for a complete runnable command map inside the overlay-only archive.

## rev0852 proofcore note

This overlay is a proofcore recovery map, not the full proof payload tree. Use `INDEX/files.csv` and rights ledgers for orientation; recover the full canonical tree before running or interpreting proof/verifier payloads.


## rev0853 proof-carrying-data lane

The first executable lane is transparent and local:

```bash
python3 PROOFCORE/verifiers/verify_pcd_envelope.py --fixture PROOFCORE/fixtures/accept/ev-overlay-integrity.rev0853.accept.json
python3 PROOFCORE/verifiers/verify_pcd_envelope.py --fixture PROOFCORE/fixtures/reject/ev-overlay-integrity.rev0853.reject.json --expect-fail
```

This verifies overlay integrity and rights-block preservation. It does not verify a SNARK or the missing canonical `zkrtp` / `streamfold` payloads.

## rev0856 active proofcore lane

The active proofcore command is now:

```bash
python3 scripts/validate_sumcheck_fs_lane_rev0856.py
```

Raw transcript-bound fixture checks:

```bash
python3 PROOFCORE/verifiers/verify_sumcheck_fs_transcript_rev0856.py   --fixture PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0856/fixtures/sumcheck_fs_accept.rev0856.json

python3 PROOFCORE/verifiers/verify_sumcheck_fs_transcript_rev0856.py   --fixture PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0856/fixtures/sumcheck_fs_reject_bad_challenge.rev0856.json   --expect-fail

python3 PROOFCORE/verifiers/verify_sumcheck_fs_transcript_rev0856.py   --fixture PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0856/fixtures/sumcheck_fs_reject_omit_payload_binding.rev0856.json   --expect-fail
```

`rev0855` is now a historical checkpoint. Do not run the exact rev0855 lane as
the active endpoint in this overlay; `verify_streamfold_sumcheck_fs_lane_rev0856.py`
reconstructs and replays it as the parent. The next recovery action is still to
supply a candidate root containing the first four canonical streamfold payloads
under the rev0855 payload manifest.

Compatibility note: rev0855 historical checkpoint is carried for parent replay by rev0856.

---

## rev0857 active proofcore lane

Use this as the current overlay-local proofcore check:

```bash
python3 scripts/validate_streamfold_payload_admission_rev0857.py
```

Raw payload admission checks:

```bash
python3 PROOFCORE/verifiers/verify_streamfold_payload_candidate_rev0857.py --mode full
python3 PROOFCORE/verifiers/verify_streamfold_payload_candidate_rev0857.py --candidate-root /path/to/full/canonical/tree --mode minimum
python3 PROOFCORE/verifiers/verify_streamfold_payload_candidate_rev0857.py --candidate-root /path/to/full/canonical/tree --mode full
```

Raw prefix-bound transcript checks:

```bash
python3 PROOFCORE/verifiers/verify_sumcheck_fs_prefix_transcript_rev0857.py --fixture PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0857/fixtures/sumcheck_fs_prefix_accept.rev0857.json
python3 PROOFCORE/verifiers/verify_sumcheck_fs_prefix_transcript_rev0857.py --fixture PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0857/fixtures/sumcheck_fs_prefix_reject_bad_prefix.rev0857.json --expect-fail
python3 PROOFCORE/verifiers/verify_sumcheck_fs_prefix_transcript_rev0857.py --fixture PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0857/fixtures/sumcheck_fs_prefix_reject_payload_contract_tamper.rev0857.json --expect-fail
```

`rev0856` is now a historical checkpoint. rev0856 historical checkpoint replay is handled by the rev0857 lane verifier. Do not run the exact rev0856 lane as the active endpoint in this overlay; `verify_streamfold_payload_admission_lane_rev0857.py` reconstructs and replays it as the parent. The payload bytes remain absent until an operator supplies a candidate root that satisfies the rev0857 admission verifier.

---

## rev0858 active proofcore lane

Use this as the current overlay-local proofcore check:

```bash
python3 scripts/validate_framed_transcript_receipt_rev0858.py
```

Raw payload receipt checks:

```bash
python3 PROOFCORE/verifiers/verify_streamfold_payload_receipt_rev0858.py --receipt PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.full.rev0858.json
python3 PROOFCORE/verifiers/verify_streamfold_payload_receipt_rev0858.py --receipt PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.minimum.rev0858.json
python3 PROOFCORE/verifiers/verify_streamfold_payload_receipt_rev0858.py --receipt PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.reject_tampered_count.rev0858.json --expect-fail
```

Raw framed transcript checks:

```bash
python3 PROOFCORE/verifiers/verify_sumcheck_fs_framed_transcript_rev0858.py --fixture PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/fixtures/sumcheck_fs_framed_accept.rev0858.json
python3 PROOFCORE/verifiers/verify_sumcheck_fs_framed_transcript_rev0858.py --fixture PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/fixtures/sumcheck_fs_framed_reject_reordered_absorb.rev0858.json --expect-fail
python3 PROOFCORE/verifiers/verify_sumcheck_fs_framed_transcript_rev0858.py --fixture PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/fixtures/sumcheck_fs_framed_reject_label_swap.rev0858.json --expect-fail
```

`rev0857` is now a historical checkpoint. rev0857 historical checkpoint replay is handled by the rev0858 lane verifier. rev0858 also hardens a candidate-root symlink bug in the carried payload candidate verifier: the raw `--candidate-root` path is checked for symlink status before resolution.

---

## rev0859 active proofcore lane

Use this as the current overlay-local proofcore check:

```bash
python3 scripts/validate_payload_receipt_liveness_rev0859.py
```

Active payload receipt replay now avoids the legacy subprocess-pipe endpoint:

```bash
python3 PROOFCORE/verifiers/verify_streamfold_payload_receipt_inprocess_rev0859.py --receipt PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.full.rev0858.json
python3 PROOFCORE/verifiers/verify_streamfold_payload_receipt_inprocess_rev0859.py --receipt PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.minimum.rev0858.json
python3 PROOFCORE/verifiers/verify_streamfold_payload_receipt_inprocess_rev0859.py --receipt PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.reject_tampered_count.rev0858.json --expect-fail
```

Full lane check:

```bash
python3 PROOFCORE/verifiers/verify_streamfold_payload_receipt_liveness_lane_rev0859.py --fixture PROOFCORE/fixtures/accept/ev-streamfold-payload-receipt-liveness.rev0859.accept.json
python3 PROOFCORE/verifiers/verify_streamfold_payload_receipt_liveness_lane_rev0859.py --fixture PROOFCORE/fixtures/reject/ev-streamfold-payload-receipt-liveness.rev0859.reject.json --expect-fail
```

`rev0858` is now a historical checkpoint. Its legacy payload-receipt verifier is liveness-quarantined in this cloudtainer because it can wait on captured subprocess pipes after printing a success marker. Do not use `verify_streamfold_payload_receipt_rev0858.py` as the active endpoint; use the rev0859 in-process verifier instead. The canonical streamfold payload bytes remain absent until a candidate root satisfies the payload admission contract.

## rev0860 active proofcore command surface

Use rev0860 as the active endpoint for the payload recovery frontier:

```bash
python3 scripts/validate_streamfold_payload_graft_rev0860.py
python3 PROOFCORE/verifiers/prepare_streamfold_payload_graft_rev0860.py --mode full --json
python3 PROOFCORE/verifiers/prepare_streamfold_payload_graft_rev0860.py --mode minimum --json
python3 PROOFCORE/verifiers/prepare_streamfold_payload_graft_rev0860.py --self-test --json
python3 PROOFCORE/verifiers/verify_streamfold_payload_graft_lane_rev0860.py --fixture PROOFCORE/fixtures/accept/ev-streamfold-payload-graft.rev0860.accept.json
```

When a candidate canonical tree is mounted, stage the minimum first recovery set outside this overlay:

```bash
python3 PROOFCORE/verifiers/prepare_streamfold_payload_graft_rev0860.py --candidate-root /path/to/canonical/tree --mode minimum --stage-dir /tmp/ev-streamfold-minimum-graft --json
```

rev0859 historical checkpoint: `scripts/validate_payload_receipt_liveness_rev0859.py` now short-circuits in rev0860 bundles; parent replay is handled by `PROOFCORE/verifiers/verify_streamfold_payload_graft_lane_rev0860.py`. Do not use the canonical `make gate` surface as the overlay entrypoint.


## rev0861 active proofcore command surface

Use rev0861 as the active endpoint for loose payload recovery:

```bash
python3 scripts/validate_streamfold_loose_payload_locator_rev0861.py
python3 PROOFCORE/verifiers/locate_streamfold_payloads_rev0861.py --mode full --json
python3 PROOFCORE/verifiers/locate_streamfold_payloads_rev0861.py --mode minimum --json
python3 PROOFCORE/verifiers/locate_streamfold_payloads_rev0861.py --self-test --json
python3 PROOFCORE/verifiers/verify_streamfold_loose_payload_locator_lane_rev0861.py --fixture PROOFCORE/fixtures/accept/ev-streamfold-loose-payload-locator.rev0861.accept.json
```

When a loose cache/export/search root may contain the streamfold bytes under
non-canonical paths, scan and stage the minimum first recovery set outside this
overlay and outside the candidate roots:

```bash
python3 PROOFCORE/verifiers/locate_streamfold_payloads_rev0861.py \
  --candidate-root /path/to/cache-or-export \
  --mode minimum \
  --stage-dir /tmp/ev-streamfold-loose-minimum \
  --json
```

rev0860 historical checkpoint: `scripts/validate_streamfold_payload_graft_rev0860.py`
now short-circuits in rev0861 bundles; parent replay is handled by
`PROOFCORE/verifiers/verify_streamfold_loose_payload_locator_lane_rev0861.py`.
Do not use the canonical `make gate` surface as the overlay entrypoint.

## rev0862 active proofcore command surface

Use rev0862 as the active endpoint for ZIP-aware archive payload recovery:

```bash
python3 scripts/validate_streamfold_archive_payload_search_rev0862.py
python3 PROOFCORE/verifiers/locate_streamfold_payload_archives_rev0862.py --mode full --json
python3 PROOFCORE/verifiers/locate_streamfold_payload_archives_rev0862.py --mode minimum --json
python3 PROOFCORE/verifiers/locate_streamfold_payload_archives_rev0862.py --self-test --json
python3 PROOFCORE/verifiers/verify_streamfold_archive_payload_search_lane_rev0862.py --fixture PROOFCORE/fixtures/accept/ev-streamfold-archive-payload-search.rev0862.accept.json
```

When a ZIP/export/cache may contain the streamfold bytes, scan and stage the
minimum first recovery set outside this overlay and outside candidate directory
roots:

```bash
python3 PROOFCORE/verifiers/locate_streamfold_payload_archives_rev0862.py \
  --candidate-source /path/to/export.zip \
  --candidate-source /path/to/unpacked/cache \
  --mode minimum \
  --stage-dir /tmp/ev-streamfold-archive-minimum \
  --json
```

rev0861 historical checkpoint: parent replay is handled by
`PROOFCORE/verifiers/verify_streamfold_archive_payload_search_lane_rev0862.py`.
Do not use the canonical `make gate` surface as the overlay entrypoint.
