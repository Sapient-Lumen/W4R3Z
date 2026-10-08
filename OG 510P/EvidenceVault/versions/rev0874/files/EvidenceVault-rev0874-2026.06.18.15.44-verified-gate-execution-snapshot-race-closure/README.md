# EvidenceVault rev0874 — verified gate execution snapshot and race closure

This is a partial overlay, not a complete or publication-ready canonical release.

## Critical correction

The exact rev0873 overlay gate could pass integrity preflight, execute a validator substituted only between checks, restore the original bytes, pass postflight, and report success. Verification and execution were not bound to the same object.

rev0874 verifies the complete inventory before other in-tree imports, copies it into a private read-only execution snapshot, and runs live coverage plus every configured validator from that snapshot under isolated Python. It then revalidates both the snapshot and retained source tree before returning success. Deterministic regressions reproduce the parent false success, prove the current gate executes captured rather than substituted source bytes, and reject `PYTHONPATH` plus in-bundle stdlib-shadow poisoning.

## Recovery status

A sweep of 12 retained sibling ZIPs and 7,305 file members found 113 unique exact canonical paths, all already available. No speculative or duplicate bytes were admitted. Coverage remains **109 / 4,586 exact current-path files** and **125 files / 4,973,641 bytes rehydratable**.

## Start here

```bash
python3 scripts/validate_zip_container.py ../EvidenceVault-rev0874-2026.06.18.15.44-verified-gate-execution-snapshot-race-closure.zip
python3 scripts/overlay_gate.py
python3 scripts/canonical_coverage.py --include-recovery --json
```

Publication remains blocked by the absent owner-approved root rights decision. All 17 selected StreamFold payloads remain absent, and canonical root `README.md` remains the sole unresolved present-path mismatch. See `AUDIT/VERIFIED_GATE_EXECUTION_SNAPSHOT_REV0874.md`.

---

# EvidenceVault rev0873 — descriptor-bound ZIP validation and transport snapshot

This is a partial overlay, not a complete or publication-ready canonical release.

## Critical correction

The exact rev0872 ZIP validator could structurally validate one archive and then reopen the pathname to hash another object. A deterministic regression replaced the path with a non-ZIP at that final reopen; rev0872 still returned `zip_container_valid`, retained the original size, and reported the replacement digest.

rev0873 opens one no-follow source descriptor, creates and hashes an anonymous immutable snapshot, and performs all ZIP structure, decompression, and embedded-inventory checks against that snapshot. Before success it rehashes the retained source descriptor and requires the pathname to still name the same unchanged identity. The deterministic ZIP builder inherits this stronger byte binding.

## Recovery status

Canonical README patch states and the indexed 64-file OCF v244 batch-output family were investigated. No candidate met canonical path, exact size, and full SHA-256, so no speculative bytes were admitted. Coverage remains **109 / 4,586 exact current-path files** and **125 files / 4,973,641 bytes rehydratable**.

## Start here

```bash
python3 scripts/validate_zip_container.py ../EvidenceVault-rev0873-2026.06.18.13.42-descriptor-bound-zip-validation-transport-snapshot.zip
python3 scripts/overlay_gate.py
python3 scripts/canonical_coverage.py --include-recovery --json
```

Publication remains blocked by the absent owner-approved root rights decision. All 17 selected StreamFold payloads remain absent, and canonical root `README.md` remains the sole unresolved present-path mismatch. See `AUDIT/DESCRIPTOR_BOUND_ZIP_VALIDATION_REV0873.md`.

---

# EvidenceVault rev0872 — root-substitution closure and canonical path identity

This is a partial overlay, not a complete or publication-ready canonical release.

## Critical correction

rev0871 could validate one root directory, then read or write through a different directory installed at the same pathname. The reproduced parent behavior redirected an exact-byte materialization into the replacement root and caused canonical coverage to hash replacement bytes.

rev0872 adds `scripts/root_anchor.py` and retains one device/inode/type identity across root validation, canonical-index reads, recovery-target validation, and exact-byte publication. Four deterministic exchange points are now rejected, including the already-exact early-success branch found during this refactor.

## Path and patch hardening

Relative paths must now arrive in one exact canonical POSIX spelling. `./a`, repeated slashes, embedded `./`, and trailing slashes are rejected rather than normalized. The shared rule now protects the overlay gate, extracted-tree integrity, overlay-chain parser, patch-byte recovery, history recovery, coverage, and materialization.

Finalization also caught the integrity validator creating an unmanifested Python bytecode cache because its no-bytecode switch came after a local import. Six entrypoints now set that switch before local imports, and nine isolated entrypoint probes enforce non-mutation.

## Recovery status

No candidate byte stream from the sibling bundles, patch/history evidence, adjacent OCF output family, or public search met canonical path, exact size, and full SHA-256 together. No guessed bytes were admitted. Coverage remains **109 / 4,586 exact current-path files** and **125 files / 4,973,641 bytes rehydratable**.

## Start here

```bash
python3 scripts/validate_zip_container.py ../EvidenceVault-rev0872-2026.06.18.11.36-root-swap-closure-path-canonicality.zip
python3 scripts/overlay_gate.py
python3 scripts/canonical_coverage.py --include-recovery --json
```

Publication remains blocked by the absent owner-approved root rights decision. All 17 selected StreamFold payloads remain absent, and canonical root `README.md` remains the sole unresolved present-path mismatch. See `AUDIT/ROOT_ANCHOR_PATH_IDENTITY_REV0872.md`.

---

# EvidenceVault rev0871 — embedded digest recovery and safe materialization refactor

This is a partial overlay, not a complete or publication-ready canonical release.

## Material progress

- Restored **two exact canonical PCB subject digest files / 144 bytes** from complete values embedded in retained patch evidence.
- Exact canonical-path coverage is now **109 / 4,586 files**; **125 files / 4,973,641 bytes** are rehydratable with historical recovery objects.
- Exact source coverage increased from 20 to **22 files**.
- A bidirectional patch-history audit and a broad embedded-evidence scan closed false-positive recovery avenues without admitting guessed bytes.

## Critical refactor

`scripts/safe_materialize.py` is now the single exact-byte publication boundary used by four recovery tools. It replaces three duplicated writer implementations with descriptor-bound parent traversal, `O_EXCL` no-clobber creation, exact descriptor read-back, pathname identity verification, and cleanup limited to the inode created by the current invocation.

## Start here

```bash
python3 scripts/validate_zip_container.py ../EvidenceVault-rev0871-2026.06.18.09.42-embedded-digest-recovery-safe-materialization-refactor.zip
python3 scripts/overlay_gate.py
python3 scripts/recover_indexed_embedded_evidence_rev0871.py
python3 scripts/canonical_coverage.py --include-recovery --json
```

Publication remains blocked by the absent owner-approved root rights decision. All 17 selected StreamFold payloads remain absent, and canonical root `README.md` remains the sole unresolved present-path mismatch. See `AUDIT/EMBEDDED_DIGEST_RECOVERY_SAFE_MATERIALIZATION_REV0871.md`.

---

# EvidenceVault rev0870 — exact OCF recovery and coverage-snapshot hardening

This is a partial overlay, not a complete or publication-ready canonical release.

## Material progress

- Restored **four exact canonical OCF source files / 53 bytes**: `hello SDT\n` and three compact DSC summary JSON files.
- Exact canonical-path coverage is now **107 / 4,586 files**; **123 files / 4,973,497 bytes** are rehydratable with historical recovery objects.
- Exact source coverage increased from 16 to **20 files**.
- A full duplicate-identity audit found **zero** remaining unavailable paths whose exact bytes already exist elsewhere in the overlay or recovery store.

## Critical refactor

The coverage engine previously split path checks, `stat`, and hashing across separate pathname operations. A replacement or in-place mutation could therefore make a gate decision from inconsistent file states. `scripts/canonical_coverage.py` now uses explicit no-follow metadata checks before and after each component open, descriptor identity checks, pre/post file identity checks, and a fresh-path identity check for every gate-critical read, including the index and recovery inventory. This explicit binding matters because this cloudtainer's filesystem allowed a directory symlink through an `O_NOFOLLOW` directory open in a direct regression test. The new recovery writer also fixes a discovered cleanup bug that could delete an existing file after correctly refusing to overwrite it.

## Start here

```bash
python3 scripts/validate_zip_container.py ../EvidenceVault-rev0870-2026.06.18.07.02-hash-oracle-byte-recovery-coverage-snapshot-hardening.zip
python3 scripts/overlay_gate.py
python3 scripts/recover_indexed_low_entropy_constants_rev0870.py
python3 scripts/canonical_coverage.py --include-recovery --json
```

Publication remains blocked by the absent owner-approved root rights decision. All 17 selected StreamFold payloads remain absent, and canonical root `README.md` remains the sole unresolved present-path mismatch. See `AUDIT/HASH_ORACLE_RECOVERY_COVERAGE_SNAPSHOT_HARDENING_REV0870.md`.

---

# EvidenceVault rev0869 — exact empty-array recovery and ZIP source-snapshot hardening

This is a rev0869 overlay derived from rev0868. It is **not** a signed canonical
release and it remains publication-blocked.

## Material progress

- Restored two exact canonical 2-byte source files (`[]`) at their indexed paths.
- Exact at-path coverage is now **103 / 4,586 files**; **119 files / 4,973,444
  bytes** are rehydratable when historical recovery objects are included.
- **4,467 files / 101,448,546 bytes** remain unavailable.

## Critical integrity correction

rev0868 accepted a ZIP whose central directory exposed a safe path while a
local-header-only Unicode Path extra field carried `../escape.txt`. rev0869
rejects alternate/unsupported extra-field semantics and requires exact
local/central flags and extraction versions.

The deterministic builder now packages only a captured hash/stat source
snapshot, revalidates the complete tree twice before publication, and confirms
the final path still names the validated temporary inode and bytes.

## Use these entrypoints

```bash
python3 scripts/validate_zip_container.py ../EvidenceVault-rev0869-2026.06.18.05.12-local-extra-path-closure-source-snapshot-recovery.zip
python3 scripts/overlay_gate.py
python3 scripts/canonical_coverage.py --include-recovery --json
```

Do not use the carried canonical `make gate` surface for this partial overlay.
No root rights grant or StreamFold payload recovery is implied.

---

# EvidenceVault rev0868 — exact digest recovery and ZIP-container hardening

This overlay makes one new canonical byte recovery and fixes the archive boundary used to deliver future revisions.

- Exact at-path canonical coverage is now **101 / 4,586 files**; **117 files** are rehydratable when protected historical objects are included.
- `sources/ocf_llm/examples/output_credential_demo_v242/credential_digest.txt` is restored from the surviving report value plus LF and exactly matches `INDEX/files.csv`.
- Validate the linked ZIP **before extraction** with `scripts/validate_zip_container.py`; after extraction, run `python3 scripts/overlay_gate.py`.
- Publication remains blocked pending owner-approved root/component rights decisions. All 17 selected StreamFold payloads remain missing.

The ZIP validator and deterministic builder are consistency controls, not signatures or external authenticity proofs. See `AUDIT/DIGEST_RECOVERY_ZIP_CONTAINER_HARDENING_REV0868.md`.

---

# EvidenceVault rev0867 — canonical recovery objects and live surface truth

This ZIP is a **partial overlay**, not the complete canonical datacube. Start with:

```bash
python3 scripts/overlay_gate.py
```

rev0867 protects a class of bytes that was at real risk of disappearing. Sixteen
files currently carrying newer, revision-divergent bytes had exact
`INDEX/files.csv` versions recoverable only by reversing the incremental patch
history. Their 88,101 exact bytes are now self-contained under
`RECOVERY/canonical-index/objects/sha256/`, with a verified inventory and a
no-clobber external materializer.

Canonical availability is now stated on two separate axes:

- **100 files / 4,885,267 bytes** are exact at their canonical paths.
- **16 additional files / 88,101 bytes** are exact recovery objects.
- **116 files / 4,973,368 bytes** can therefore be rehydrated.
- **4,470 files / 101,448,622 bytes** remain unavailable.
- `README.md` is the sole present same-path mismatch not recovered from overlay
  history.

The inherited `RELEASE_MANIFEST.json`, canonical `MANIFEST.sha256`, rev0826 SPDX
inventory, dedupe report, and Makefile are historical canonical-tree surfaces.
They are not live inventories or an executable command surface for this ZIP.
Use `PATCH_BUNDLE_MANIFEST.json`, `CHECKS/overlay-manifest.json`, and the overlay
gate for current truth. Publication remains blocked by the absent owner-approved
root license/notice, and all 17 selected StreamFold payloads remain absent.

---

# EvidenceVault rev0866 — exact patch-corpus recovery and live coverage enforcement

rev0866 converts dormant patch bodies into verified canonical bytes. It restores **81 previously missing indexed files (546,423 bytes)**, including **12 source payloads**, without guessing partial hunks or overwriting later-revision content.

## Start here

```bash
python3 scripts/overlay_gate.py
```

The gate now computes representation coverage directly from `INDEX/files.csv` and current bytes before listing or running checks. A successful run is an **overlay** pass, not a canonical-completeness claim: this bundle now materializes **100 of 4,586** indexed files exactly, carries **17** same-path revision-divergent files, and is missing **4,469**. Exact canonical `sources/` coverage is **13 of 3,476** files.

Do not start with `make gate`. A fresh command-surface audit finds **42 of 47** lexically referenced `scripts/*.py` or `scripts/*.sh` paths absent from this partial overlay.

## Substantive recovery

`scripts/recover_indexed_files_from_patches.py` scans unified patches for complete new-side byte streams beginning at line 1. A stream is accepted only when both size and SHA-256 exactly match `INDEX/files.csv`. The pre-rev0866 patch corpus yielded 88 exact candidates: 81 were missing and are now restored, two were already exact, and five contain legitimate later-overlay bytes and were not overwritten.

The recovery tool can safely materialize the proved set into a separate tree carrying the identical canonical index:

```bash
python3 scripts/recover_indexed_files_from_patches.py --json
python3 scripts/recover_indexed_files_from_patches.py   --target-root ../full-tree --write --require-present
```

Writes are no-clobber, reject symlink traversal, and are hash-verified after atomic publication.

## Rights and remaining risk

The recovered historical `RIGHTS/NOTICE.draft` and related files are evidence payloads, not active grants. Publication remains blocked: no owner-approved root license or notice exists, component conclusions remain `NOASSERTION`, all 17 selected StreamFold payloads remain absent, and most of the canonical cube is still missing.

See `AUDIT/PATCH_CORPUS_EXACT_RECOVERY_REV0866.md` for the full recovery, coverage, gate, and command-surface audit.

---

# EvidenceVault rev0865 — exact payload recovery and an immutable, honest overlay gate

rev0865 restores real canonical bytes and removes an operational trap. The exact 356,744-byte MCP servers README is now present at its indexed path, while every gate run explicitly reports that this ZIP is only a partial representation of the canonical datacube.

## Start here

```bash
python3 scripts/overlay_gate.py
```

The command checks overlay integrity before and after other work. A full successful run is an **overlay** pass, not a canonical-completeness claim: this bundle exactly materializes **19 of 4,586** indexed files, carries **17** same-path revision-divergent files, and is missing **4,550**. Under canonical `sources/`, exact materialization is **1 of 3,476** files.

Do not start with `make gate`; this overlay does not carry the full canonical Makefile surface.

## Substantive movement

- Embedded `sources/pact/PACT_workdir/eval_real_registry_scan/servers_README.md` with exact canonical SHA-256 `0f7174a89094f7695b899fad71c2e6d0fb12cd6041734d779aacd8a8bfe400c2` and size 356,744 bytes.
- Recorded a narrow file-level `CC-BY-4.0` conclusion and unchanged-source attribution from the exact adjacent upstream `LICENSE`. PACT and EvidenceVault remain `NOASSERTION`.
- Added a measured representation audit rather than another payload-search registry. The three local analysis companions to the README remain absent and were not synthesized.
- Fixed `scripts/overlay_gate.py`: reports must be written outside the immutable bundle, selected checks force integrity, integrity runs preflight and postflight, and partial invocations are labeled `NOT A FULL GATE`.

## Reports

```bash
python3 scripts/overlay_gate.py --report ../rev0865-overlay-gate-report.json
```

An in-bundle report path is rejected because it would change the artifact being verified.

## Remaining high-risk work

The next meaningful inputs are a full canonical tree, real candidate payload bytes, or owner/upstream rights decisions. Publication remains blocked by the absent root policy and unresolved component-wide conclusions; all 17 StreamFold target payloads remain absent.

---

# EvidenceVault rev0864 — upstream license recovery and overlay gate refactor

rev0864 converts two high-risk unknowns into bounded outcomes: it restores one exact upstream `LICENSE` file that the canonical PACT snapshot referenced but lacked, and it proves the carried patch history cannot reconstruct the 17 missing StreamFold payload files.

## Start here

```bash
python3 scripts/overlay_gate.py
```

That single, manifest-driven command runs the shipped rev0864 validator, overlay integrity check, patch-chain check, and active StreamFold archive-search validator. Do **not** start with `make gate`: this overlay is not the full canonical tree and does not carry the Makefile's complete script surface.

## Real forward movement

- Added `sources/pact/PACT_workdir/eval_real_registry_scan/LICENSE` from official `modelcontextprotocol/servers` commit `f4244583a6af9425633e433a3eec000d23f4e011` with exact SHA-256 `0382b0057770ca05e9c350a50aa3b1c1fea84da0bc81d723bf00b9aa841be58a`.
- Reduced missing/outside local license references from **1** to **0** and updated the rights ledgers. PACT remains `NOASSERTION`; no root rights file was invented.
- Searched all 25 parent patch files for exact diff sections for the 17 missing StreamFold paths. The result is **0** target diff sections: metadata mentions exist, payload bodies do not.
- Added `scripts/overlay_gate.py` as the stable overlay entrypoint rather than adding more historical command prose.

## Remaining blockers

Publication is still blocked on an owner-approved archive-level policy and component-level rights decisions. StreamFold recovery still requires actual candidate bytes or a full canonical tree; another search/proof lane without new material is not justified.

---

# EvidenceVault rev0863 mission recenter / rights identity triage overlay bundle

This bundle is a rev0863 overlay derived from rev0862. It is **not** a signed canonical EvidenceVault release artifact, **not** a rights grant, and it does **not** make the datacube publication-ready.

## What rev0863 changes

- Adds `AUDIT/MISSION_RECENTER_RIGHTS_IDENTITY_TRIAGE_REV0863.*`, a deep mission/rights/identity/waste audit over the rev0862 datacube.
- Adds `RIGHTS/RIGHTS_DECISION_PACKET_REV0863.*`, a human-owner decision packet built from the existing rights ledger without inventing licenses.
- Adds `PATCH_BUNDLE_MANIFEST.json`, a first-class overlay/patch-bundle identity surface so rev0863 overlay identity is not confused with carried rev0826 canonical release metadata.
- Adds `scripts/validate_mission_recenter_rights_identity_rev0863.py` and `VALIDATION/rev0863_targeted_validation.txt`.
- Prepends the README and overlay command surface with the current revision so operators do not start from the stale rev0855 headings.

## Core interpretation

The heart of the mission is a **proof-carrying evidence vault**: preserve evidence, payload identities, claims, provenance, rights decisions, and verifier context without confusing local overlay checks, mathematical proof, and publication permission.

rev0863 intentionally recenters the work. The active proofcore lane from rev0862 remains useful for ZIP-aware payload search, but the decisive blockers are still rights, overlay/canonical identity separation, portable provenance, and real candidate payload recovery.

## Use these overlay checks first

```bash
python3 scripts/validate_overlay_bundle_integrity_rev0848.py
python3 scripts/apply_overlay_stack_rev0850.py --json
python3 scripts/validate_mission_recenter_rights_identity_rev0863.py
python3 scripts/validate_streamfold_archive_payload_search_rev0862.py
```

Do **not** treat `make gate` as the overlay entrypoint. The carried canonical `Makefile` still references canonical-tree surfaces that are absent from this overlay ZIP.

## Rights status

Still publication-blocked. rev0863 does not add or infer license terms, root `LICENSE`, root `COPYING`, root `NOTICE`, SPDX conclusions, or RO-Crate rights assertions.

---

# EvidenceVault rev0855 streamfold sumcheck payload-gate overlay bundle

This bundle is a rev0855 proofcore overlay derived from rev0854. It is **not** a signed canonical EvidenceVault release artifact and it does **not** make the datacube publication-ready.

## What rev0855 changes

- Converts the rev0854 recommended frontier group, `streamfold_sumcheck_toy_v2_family`, into an executable lane under `PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0855/`.
- Adds an exact payload recovery gate for the 17 indexed streamfold sumcheck paths: path, byte count, SHA-256, role, and expected absence are now machine-checkable.
- Adds `PROOFCORE/verifiers/verify_sumcheck_transcript_rev0855.py`, a real transparent toy sumcheck transcript verifier with accept and reject fixtures.
- Adds `PROOFCORE/verifiers/verify_streamfold_sumcheck_lane_rev0855.py`, which reconstructs and replays the rev0854 parent checkpoint, validates the payload gate, runs the toy sumcheck accept/reject checks, and preserves the rights block.
- Adds `AUDIT/STREAMFOLD_SUMCHECK_LANE_REV0855.*` and `scripts/validate_streamfold_sumcheck_lane_rev0855.py`.

## Use these overlay checks first

```bash
python3 scripts/validate_overlay_bundle_integrity_rev0848.py
python3 scripts/apply_overlay_stack_rev0850.py --json
python3 scripts/validate_overlay_stack_application_harness_rev0850.py
python3 scripts/validate_mission_alignment_waste_rev0851.py
python3 scripts/validate_snark_origin_proofcore_rev0852.py
python3 scripts/validate_proofcore_frontier_pcd_rev0854.py
python3 scripts/validate_streamfold_sumcheck_lane_rev0855.py
```

Direct lane checks:

```bash
python3 PROOFCORE/verifiers/verify_sumcheck_transcript_rev0855.py --fixture PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0855/fixtures/sumcheck_accept.rev0855.json
python3 PROOFCORE/verifiers/verify_sumcheck_transcript_rev0855.py --fixture PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0855/fixtures/sumcheck_reject_bad_round.rev0855.json --expect-fail
python3 PROOFCORE/verifiers/verify_streamfold_sumcheck_lane_rev0855.py --fixture PROOFCORE/fixtures/accept/ev-streamfold-sumcheck-lane.rev0855.accept.json
python3 PROOFCORE/verifiers/verify_streamfold_sumcheck_lane_rev0855.py --fixture PROOFCORE/fixtures/reject/ev-streamfold-sumcheck-lane.rev0855.reject.json --expect-fail
```

## Rights status

Still publication-blocked. rev0855 does not add or infer license terms, root `LICENSE`, root `COPYING`, root `NOTICE`, SPDX conclusions, or RO-Crate rights assertions.

---

# EvidenceVault rev0854 parent-linked PCD frontier overlay bundle

This bundle is a rev0854 proofcore-frontier overlay derived from the rev0853 executable transparent PCD lane. It is **not** a signed canonical EvidenceVault release artifact and it does **not** make the datacube publication-ready.

## What rev0854 changes

- Adds a second transparent PCD lane for proofcore completion risk: `ev.pcd.proofcore_frontier.rev0854`.
- Adds a parent replay verifier that reconstructs rev0853 in a temporary directory by reversing `PATCHES/rev0853-to-rev0854-overlay.patch`, restores cyclic parent surfaces from `PROOFCORE/parent_snapshots/rev0853/`, and reruns the rev0853 PCD verifier.
- Refactors the rev0853 P0 path-role map into `PROOFCORE/frontier/rev0854/proof_obligation_frontier.rev0854.{json,csv}`.
- Selects `streamfold_sumcheck_toy_v2_family` as the next narrow proof lane because it has ABI/IR, public-input-or-commitment, and attestation/receipt coverage in the canonical index.
- Adds `scripts/validate_proofcore_frontier_pcd_rev0854.py` and rev0854 audit/session evidence.

## Use these overlay checks first

```bash
python3 scripts/validate_overlay_bundle_integrity_rev0848.py
python3 scripts/apply_overlay_stack_rev0850.py --json
python3 scripts/validate_overlay_stack_application_harness_rev0850.py
python3 scripts/validate_mission_alignment_waste_rev0851.py
python3 scripts/validate_snark_origin_proofcore_rev0852.py
python3 scripts/validate_proofcore_frontier_pcd_rev0854.py
```

The rev0853 verifier remains an exact historical checkpoint. In rev0854, use the rev0854 frontier verifier to replay that checkpoint rather than running the rev0853 exact accept fixture directly against the changed tree.

## Rights status

Still publication-blocked. rev0854 does not add or infer license terms, root `LICENSE`, root `COPYING`, root `NOTICE`, SPDX conclusions, or RO-Crate rights assertions.

---

## Previous rev0853 README

# EvidenceVault rev0853 executable PCD lane / proofcore map overlay bundle

This bundle is a rev0853 proof-carrying-data/proofcore overlay derived from the rev0852 SNARK-origin recovery map. It is **not** a signed canonical EvidenceVault release artifact and it does **not** make the datacube publication-ready.

## What rev0853 changes

- Adds a first-class `PROOFCORE/` lane with claim, public inputs, witness policy, commitments, transparent certificate envelope, verifier, accept fixture, and reject fixture.
- Adds `PROOFCORE/verifiers/verify_pcd_envelope.py`, a runnable deterministic verifier for the first local proof-carrying-data claim.
- Adds `PROOFCORE/maps/canonical_path_to_role.rev0853.csv`, a role map over the carried canonical proof-signal subset of `INDEX/files.csv`.
- Adds `AUDIT/PROOFCORE_PATH_ROLE_AUDIT_REV0853.*` and `AUDIT/PROOFCORE_PCD_LANE_REV0853.*`.
- Adds `scripts/validate_proofcore_pcd_rev0853.py` and refreshes overlay command guidance, patch identity, provenance, patch hashes, and overlay hash surfaces.

## Core interpretation

rev0853 adds the first executable proof-carrying-data lane and makes the proof-carrying-data idea executable without overclaiming. The first lane proves a local overlay-integrity claim using public data and a transparent verifier. It is **not** a zk-SNARK, not zero knowledge, not succinct, and not a proof of `zkrtp` or `streamfold` mathematical correctness.

The practical win is shape: the project now has a reusable envelope for future recovered proof payloads. When the full canonical tree is mounted, the next lane should replace this transparent overlay claim with one recovered `zkrtp` or `streamfold` verifier/receipt/public-input edge.

## Use these overlay checks first

```bash
python3 scripts/validate_overlay_bundle_integrity_rev0848.py
python3 scripts/apply_overlay_stack_rev0850.py --json
python3 scripts/validate_overlay_stack_application_harness_rev0850.py
python3 scripts/validate_mission_alignment_waste_rev0851.py
python3 scripts/validate_snark_origin_proofcore_rev0852.py
python3 scripts/validate_proofcore_pcd_rev0853.py
```

Direct PCD fixture checks:

```bash
python3 PROOFCORE/verifiers/verify_pcd_envelope.py --fixture PROOFCORE/fixtures/accept/ev-overlay-integrity.rev0853.accept.json
python3 PROOFCORE/verifiers/verify_pcd_envelope.py --fixture PROOFCORE/fixtures/reject/ev-overlay-integrity.rev0853.reject.json --expect-fail
```

Do **not** treat `make gate` as the overlay entrypoint. The `Makefile` is a carried canonical-tree surface; many canonical scripts and payload roots are intentionally absent from the overlay artifact.

## Rights status

Still publication-blocked. rev0853 does not add or infer license terms. No root `LICENSE`, `COPYING`, or `NOTICE` was added.

---

## Previous rev0852 README

# EvidenceVault rev0852 SNARK-origin proofcore recovery overlay bundle

This bundle is a rev0852 SNARK-origin/proofcore recovery overlay derived from the rev0851 mission/waste audit overlay. It is **not** a signed canonical EvidenceVault release artifact and it does **not** make the datacube publication-ready.

## What rev0852 changes

- Applies the new user context that EvidenceVault began as a SNARKs-adjacent proof exploration.
- Adds `AUDIT/SNARK_ORIGIN_PROOFCORE_RECOVERY_REV0852.*` as an origin-aware proofcore recovery audit.
- Adds `PROOFCORE_RECOVERY_PLAN_REV0852.md` with a concrete proof-carrying evidence lane.
- Adds `scripts/validate_snark_origin_proofcore_rev0852.py`.
- Updates overlay command guidance, patch identity, provenance, patch hashes, and overlay hash surfaces.

## Core interpretation

EvidenceVault should be read as a **proof-carrying evidence vault**: an archive where claims, papers, receipts, attestations, verifier commitments, public inputs, witness policy, provenance, and rights decisions are preserved without confusing archival integrity, mathematical/protocol validity, and publication permission.

The overlay carries indexes and ledgers that point at the proof lineage. It does not carry the full canonical proof payload tree. Recover or mount the full canonical tree before making proof/verifier claims.

## Use these overlay checks first

```bash
python3 scripts/validate_overlay_bundle_integrity_rev0848.py
python3 scripts/apply_overlay_stack_rev0850.py --json
python3 scripts/validate_overlay_stack_application_harness_rev0850.py
python3 scripts/validate_mission_alignment_waste_rev0851.py
python3 scripts/validate_snark_origin_proofcore_rev0852.py
```

Do **not** treat `make gate` as the overlay entrypoint. The `Makefile` is a carried canonical-tree surface; many canonical scripts and payload roots are intentionally absent from the overlay artifact.

## Rights status

Still publication-blocked. rev0852 does not add or infer license terms. The proof-origin context makes source/root and rights closure more important, not less.

---

## Previous rev0851 README

# EvidenceVault rev0851 mission/waste audit overlay bundle

This bundle is a rev0851 mission-alignment and cloudtainer-waste audit derived from the rev0850 overlay-application/rights-boundary bundle. It is **not** a signed canonical EvidenceVault release artifact and it does **not** make the datacube publication-ready.

## What rev0851 changes

- Adds `AUDIT/MISSION_ALIGNMENT_WASTE_ROADMAP_REV0851.*` and `SESSION_REVIEW_REV0851.*` with a deep read of the mission, missing pieces, waste patterns, and correction path.
- Adds `OVERLAY_COMMANDS.md` to make the overlay-local command surface explicit. The carried canonical `Makefile` is not a complete runnable surface inside this overlay-only ZIP.
- Adds `scripts/validate_mission_alignment_waste_rev0851.py`.
- Generalizes `scripts/validate_overlay_stack_application_harness_rev0850.py` so the rev0850 harness validator can validate the current overlay-chain endpoint rather than failing as soon as a later overlay patch is added.
- Adds `PATCHES/rev0850-to-rev0851-overlay.patch` and refreshes overlay hash/provenance surfaces.

## Use these overlay checks first

```bash
python3 scripts/validate_overlay_bundle_integrity_rev0848.py
python3 scripts/apply_overlay_stack_rev0850.py --json
python3 scripts/validate_overlay_stack_application_harness_rev0850.py
python3 scripts/validate_mission_alignment_waste_rev0851.py
```

Do **not** treat `make gate` as the overlay entrypoint. The `Makefile` is a carried canonical-tree surface; many canonical scripts and payload roots are intentionally absent from the overlay artifact.

## Rights status

Still publication-blocked. rev0851 does not add or infer license terms. It records that the central blocker is no longer another audit layer; it is owner/upstream rights closure plus a clean identity/provenance split.

---

## Previous rev0850 README

# EvidenceVault rev0850 overlay/patch refactor bundle

This bundle is a rev0850 risk-reduction overlay derived from the rev0849 authorized-snapshot/html-rights-hardening bundle. It is **not** a signed canonical EvidenceVault release artifact and it does **not** make the datacube publication-ready.

The canonical rev0840 patch payloads remain available and unchanged:

```bash
# From a rev0839-patched expanded tree:
patch -p1 < PATCHES/rev0839-to-rev0840-incremental.patch

# From fresh expanded rev0826:
patch -p1 < PATCHES/rev0826-to-rev0840-cumulative.patch
```

rev0850 adds a guarded overlay-stack application harness and recovers the missing rev0840-to-rev0841 handoff patch, so the overlay series can be checked as a continuous chain:

```bash
# Validate the overlay patch chain inside this bundle:
python3 scripts/apply_overlay_stack_rev0850.py --json

# Dry-run the overlay stack against a full canonical target tree:
python3 scripts/apply_overlay_stack_rev0850.py --target-root /path/to/full/canonical/tree --json

# Apply only after the dry run succeeds and the target tree is the intended full canonical tree:
python3 scripts/apply_overlay_stack_rev0850.py --target-root /path/to/full/canonical/tree --apply --json
```

rev0850 also adds the normal focused overlay patch for this session's targeted changes:

```bash
# Overlay-level patch against the rev0849 bundle contents:
patch -p1 < PATCHES/rev0849-to-rev0850-overlay.patch
```

## What rev0850 changes

- Adds `PATCHES/rev0840-to-rev0841-overlay.patch`, recovering the missing seed handoff that had prevented the overlay patch chain from starting at the rev0840 canonical bundle.
- Adds `scripts/apply_overlay_stack_rev0850.py`, a guarded check/dry-run/apply helper that validates patch names, rejects path-traversing patch payloads, refuses symlinked target trees, and applies the chain through a temporary dry run before optional target mutation.
- Hardens `scripts/publication_rights_gate.py` so `RIGHTS/component_license_ledger.json` and root `LICENSE`, `COPYING`, or `NOTICE` sentinels cannot be symlinks or non-regular files when determining whether publication is rights-ready.
- Tightens `scripts/validate_overlay_bundle_integrity_rev0848.py` so the overlay integrity gate now requires the recovered rev0840-to-rev0841 seed patch and a continuous chain through the current revision.
- Adds rev0850 validators/audits for overlay-stack application and rights-ledger/root-rights boundary hardening.

## Important validation note

`MANIFEST.sha256`, `INDEX/files.*`, `RELEASE_MANIFEST.json`, `ro-crate-metadata.json`, and the SPDX file inventory remain canonical-tree/release surfaces carried by this overlay. For this ZIP as an overlay artifact, verify `CHECKS/overlay-manifest.json`, `CHECKS/overlay-manifest.sha256`, `scripts/validate_overlay_bundle_integrity_rev0848.py`, and `scripts/apply_overlay_stack_rev0850.py --json`.

## Rights status

Still publication-blocked. rev0850 makes the future full-tree application path and rights-unblock boundary harder to get wrong; it does not add or infer license terms.

---

## Previous rev0849 README

# EvidenceVault rev0849 overlay/patch refactor bundle

This bundle is a rev0849 risk-reduction overlay derived from the rev0848 builder-boundary/public-path-integrity bundle. It is **not** a signed canonical EvidenceVault release artifact and it does **not** make the datacube publication-ready.

The canonical rev0840 patch payloads remain available and unchanged:

```bash
# From a rev0839-patched expanded tree:
patch -p1 < PATCHES/rev0839-to-rev0840-incremental.patch

# From fresh expanded rev0826:
patch -p1 < PATCHES/rev0826-to-rev0840-cumulative.patch
```

rev0849 adds a focused overlay patch for this session's targeted changes:

```bash
# Overlay-level patch against the rev0848 bundle contents:
patch -p1 < PATCHES/rev0848-to-rev0849-overlay.patch
```

## What rev0849 changes

- Hardens `scripts/publish_queue_item.py` so every `published/PUBLIC_SURFACE.json` snapshot `entry_point` must be explicitly authorized by `decision.public_paths`; a snapshot can no longer digest extra public entry payloads not covered by the queue decision.
- Extends `scripts/publication_rights_gate.py` so the fresh local rights-reference scan covers conventional `docs/` and `documentation/` roots plus `.html`, `.htm`, `.xhtml`, and `.xml` text surfaces.
- Refactors `scripts/rebuild_indexes.py` so early metadata/hash reads that happen before the final full-tree symlink scan also reject final or intermediate symlink components and outside-root inputs.
- Adds rev0849 validators/audits for authorized snapshot-entry coverage, HTML/XML docs rights scanning, and early rebuild metadata read boundaries.
- Refreshes affected carried-forward audits and records `VALIDATION/rev0849_targeted_validation.txt`.

## Important validation note

`MANIFEST.sha256`, `INDEX/files.*`, `RELEASE_MANIFEST.json`, `ro-crate-metadata.json`, and the SPDX file inventory remain canonical-tree/release surfaces carried by this overlay. For this ZIP as an overlay artifact, verify `CHECKS/overlay-manifest.json`, `CHECKS/overlay-manifest.sha256`, and `scripts/validate_overlay_bundle_integrity_rev0848.py` first.

## Rights status

Still publication-blocked. rev0849 closes authorization, parser coverage, and pre-scan symlink/read-boundary gaps around a future rights-approved publication/rebuild path; it does not add or infer license terms.

---

## Previous rev0848 README

# EvidenceVault rev0848 overlay/patch refactor bundle

This bundle is a rev0848 risk-reduction overlay derived from the rev0847 output-boundary/atomic-rebuild bundle. It is **not** a signed canonical EvidenceVault release artifact and it does **not** make the datacube publication-ready.

The canonical rev0840 patch payloads remain available and unchanged:

```bash
# From a rev0839-patched expanded tree:
patch -p1 < PATCHES/rev0839-to-rev0840-incremental.patch

# From fresh expanded rev0826:
patch -p1 < PATCHES/rev0826-to-rev0840-cumulative.patch
```

rev0848 adds a focused overlay patch for this session's targeted changes:

```bash
# Overlay-level patch against the rev0847 bundle contents:
patch -p1 < PATCHES/rev0847-to-rev0848-overlay.patch
```

## What rev0848 changes

- Hardens `scripts/rebuild_indexes.py` so material-builder subprocess targets are validated as safe Python module names and archive-local, non-symlink regular files before execution.
- Hardens `scripts/publish_queue_item.py` so `decision.public_paths` must be non-empty, duplicate-free, and consistent with the `published/PUBLIC_SURFACE.json` snapshot/source manifest that is actually digested for the release record.
- Extends `scripts/publication_rights_gate.py` so local component-license references under `LICENSES/`, `licences/`, `notices/`, or `copyright/` directories are recognized even when the leaf filename is neutral, such as `LICENSES/Apache-2.0.txt`.
- Adds `scripts/validate_overlay_bundle_integrity_rev0848.py`, a runnable self-check for overlay-manifest exactness, patch hashes, overlay-patch chain continuity, portable input-artifact names, and changed-file list cleanliness.
- Adds rev0848 validators and audit records for the rights scanner, queue publisher, rebuild coordinator, and overlay self-integrity.
- Refreshes affected carried-forward audits and records `VALIDATION/rev0848_targeted_validation.txt`.

## Important validation note

`MANIFEST.sha256`, `INDEX/files.*`, `RELEASE_MANIFEST.json`, `ro-crate-metadata.json`, and the SPDX file inventory remain canonical-tree/release surfaces carried by this overlay. For this ZIP as an overlay artifact, verify `CHECKS/overlay-manifest.json`, `CHECKS/overlay-manifest.sha256`, and now `scripts/validate_overlay_bundle_integrity_rev0848.py` first.

## Rights status

Still publication-blocked. rev0848 closes concrete bypass/consistency seams around a future rights-approved publication/rebuild path; it does not add or infer license terms.

---

## Previous rev0847 README

# EvidenceVault rev0847 overlay/patch refactor bundle

This bundle is a rev0847 risk-reduction overlay derived from the rev0846 release-metadata/symlink-closure bundle. It is **not** a signed canonical EvidenceVault release artifact and it does **not** make the datacube publication-ready.

The canonical rev0840 patch payloads remain available and unchanged:

```bash
# From a rev0839-patched expanded tree:
patch -p1 < PATCHES/rev0839-to-rev0840-incremental.patch

# From fresh expanded rev0826:
patch -p1 < PATCHES/rev0826-to-rev0840-cumulative.patch
```

rev0847 adds a focused overlay patch for this session's targeted changes:

```bash
# Overlay-level patch against the rev0846 bundle contents:
patch -p1 < PATCHES/rev0846-to-rev0847-overlay.patch
```

## What rev0847 changes

- Hardens `scripts/publish_queue_item.py` so public release output writes reject destinations outside the archive root and reject symlinked output parents such as `published/` or `published/releases/` before same-directory temporary files are created.
- Validates `scripts/transition_queue_item.py` through the same archive-local path/symlink boundary helper before the final queue-transition subprocess runs, and runs the child with bytecode suppression and `cwd=ROOT`.
- Adds `scripts/validate_publish_queue_item_output_boundary_rev0847.py` and `AUDIT/PUBLISH_QUEUE_ITEM_OUTPUT_BOUNDARY_REV0847.*`.
- Refactors `scripts/rebuild_indexes.py` so release-critical generated surfaces are written through fsynced same-directory temporary files and atomic replacement instead of direct truncating writes.
- Covers `RELEASE_MANIFEST.json`, `ro-crate-metadata.json`, `RO_CRATE_PROFILE.md`, `INDEX/files.json`, `INDEX/files.csv`, and `MANIFEST.sha256` with the new generated-output helper.
- Adds `scripts/validate_rebuild_indexes_atomic_outputs_rev0847.py` and `AUDIT/REBUILD_INDEXES_ATOMIC_OUTPUTS_REV0847.*`.
- Refreshes affected carried-forward audits and records `VALIDATION/rev0847_targeted_validation.txt`.

## Important validation note

`MANIFEST.sha256`, `INDEX/files.*`, `RELEASE_MANIFEST.json`, `ro-crate-metadata.json`, and the SPDX file inventory remain canonical-tree/release surfaces carried by this overlay. For this ZIP as an overlay artifact, verify `CHECKS/overlay-manifest.json` and `CHECKS/overlay-manifest.sha256` first.

## Rights status

Still publication-blocked. rev0847 reduces partial-write and symlink-redirection risk around future rights-approved publication/rebuild paths; it does not add or infer license terms.

---

## Previous rev0846 README

# EvidenceVault rev0846 overlay/patch refactor bundle

This bundle is a rev0846 risk-reduction overlay derived from the rev0845 boundary-hardening bundle. It is **not** a signed canonical EvidenceVault release artifact and it does **not** make the datacube publication-ready.

The canonical rev0840 patch payloads remain available and unchanged:

```bash
# From a rev0839-patched expanded tree:
patch -p1 < PATCHES/rev0839-to-rev0840-incremental.patch

# From fresh expanded rev0826:
patch -p1 < PATCHES/rev0826-to-rev0840-cumulative.patch
```

rev0846 adds a small overlay patch for this session's targeted changes:

```bash
# Overlay-level patch against the rev0845 bundle contents:
patch -p1 < PATCHES/rev0845-to-rev0846-overlay.patch
```

## What rev0846 changes

- Closes the remaining publication-rights symlink gap: a local `LICENSE` / `COPYING` / `NOTICE` reference reached through a symlinked intermediate directory is now rejected, even if the resolved target points back inside the archive.
- Adds `scripts/validate_publication_rights_gate_intermediate_symlink_rev0846.py` and `AUDIT/PUBLICATION_RIGHTS_GATE_INTERMEDIATE_SYMLINK_REV0846.*`.
- Refactors `scripts/publish_queue_item.py` so queue-state JSON files, decision JSON files, `CHANGELOG.md`, and SHA-256 publication inputs are rejected when any archive path component is a symlink.
- Adds `scripts/validate_publish_queue_item_metadata_symlink_rev0846.py` and `AUDIT/PUBLISH_QUEUE_ITEM_METADATA_SYMLINK_REV0846.*`.
- Refreshes the publication preflight/dry-run safety audit after the publisher code change and records `VALIDATION/rev0846_targeted_validation.txt`.

## Important validation note

`MANIFEST.sha256`, `INDEX/files.*`, `RELEASE_MANIFEST.json`, `ro-crate-metadata.json`, and the SPDX file inventory remain canonical-tree/release surfaces carried by this overlay. For this ZIP as an overlay artifact, verify `CHECKS/overlay-manifest.json` and `CHECKS/overlay-manifest.sha256` first.

## Rights status

Still publication-blocked. rev0846 reduces symlink and mutable-host-data bypass risk around future rights-approved publication paths; it does not add or infer license terms.

---

## Previous rev0845 README

# EvidenceVault rev0845 overlay/patch refactor bundle

This bundle is a rev0845 risk-reduction overlay derived from the rev0844 hardening bundle. It is **not** a signed canonical EvidenceVault release artifact and it does **not** make the datacube publication-ready.

The canonical rev0840 patch payloads remain available and unchanged:

```bash
# From a rev0839-patched expanded tree:
patch -p1 < PATCHES/rev0839-to-rev0840-incremental.patch

# From fresh expanded rev0826:
patch -p1 < PATCHES/rev0826-to-rev0840-cumulative.patch
```

rev0845 adds a small overlay patch for this session's targeted changes:

```bash
# Overlay-level patch against the rev0844 bundle contents:
patch -p1 < PATCHES/rev0844-to-rev0845-overlay.patch
```

## What rev0845 changes

- Hardens `scripts/publication_rights_gate.py` so the fresh local rights-reference scan fails closed on symlinked scan inputs and symlinked local `LICENSE` / `COPYING` / `NOTICE` targets.
- Extends the same fresh scan to recognize local rights links in HTML `href` anchors and reStructuredText inline/reference forms, while avoiding false blocks for in-document `#license` anchors.
- Hardens `scripts/publish_queue_item.py` so queue dates, release IDs, decision IDs, `public_paths`, and `published/PUBLIC_SURFACE.json` entry paths must remain clean archive-relative paths; public-surface payload reads reject traversal and symlink boundaries.
- Hardens `scripts/rebuild_indexes.py` so release-critical index/manifest rebuilds reject symlinked files/directories rather than hashing host/cloudtainer targets through archive-internal links.
- Adds rev0845 validators and audits for rights-gate symlink/parser boundaries, queue-publisher release boundaries, and rebuild-index symlink boundaries.
- Refreshes affected carried-forward safety audits and records `VALIDATION/rev0845_targeted_validation.txt`.

## Important validation note

`MANIFEST.sha256`, `INDEX/files.*`, `RELEASE_MANIFEST.json`, `ro-crate-metadata.json`, and the SPDX file inventory remain canonical-tree/release surfaces carried by this overlay. For this ZIP as an overlay artifact, verify `CHECKS/overlay-manifest.json` and `CHECKS/overlay-manifest.sha256` first.

## Rights status

Still publication-blocked. rev0845 removes more bypass/corruption paths around a future rights-approved publication, but it does not add or infer license terms.

---

## Previous rev0844 README

# EvidenceVault rev0844 overlay/patch refactor bundle

This bundle is a rev0844 risk-reduction overlay derived from the rev0843 refactor bundle. It is **not** a signed canonical EvidenceVault release artifact and it does **not** make the datacube publication-ready.

The canonical rev0840 patch payloads remain available and unchanged:

```bash
# From a rev0839-patched expanded tree:
patch -p1 < PATCHES/rev0839-to-rev0840-incremental.patch

# From fresh expanded rev0826:
patch -p1 < PATCHES/rev0826-to-rev0840-cumulative.patch
```

rev0844 adds a small overlay patch for this session's targeted changes:

```bash
# Overlay-level patch against the rev0843 bundle contents:
patch -p1 < PATCHES/rev0843-to-rev0844-overlay.patch
```

## What rev0844 changes

- Hardens `scripts/publish_queue_item.py` beyond rev0843's atomic writes: future public release outputs now use no-clobber creation for snapshot/record/note files, and rollback tracks only paths successfully created by the current process.
- Adds `scripts/validate_publish_queue_item_no_clobber_rev0844.py` and `AUDIT/PUBLISH_QUEUE_ITEM_NO_CLOBBER_REV0844.*` with helper and race-fixture probes.
- Extends `scripts/publication_rights_gate.py` so the fresh local `LICENSE` / `COPYING` / `NOTICE` reference scan catches inline Markdown links with titles, angle-wrapped targets, and reference-style definitions.
- Adds `scripts/validate_publication_rights_gate_markdown_reference_forms_rev0844.py` and `AUDIT/PUBLICATION_RIGHTS_GATE_MARKDOWN_REFERENCE_FORMS_REV0844.*`.
- Refreshes affected carried-forward safety audits and records `VALIDATION/rev0844_targeted_validation.txt`.

## Important validation note

`MANIFEST.sha256`, `INDEX/files.*`, `RELEASE_MANIFEST.json`, `ro-crate-metadata.json`, and the SPDX file inventory remain canonical-tree/release surfaces carried by this overlay. For this ZIP as an overlay artifact, verify `CHECKS/overlay-manifest.json` and `CHECKS/overlay-manifest.sha256` first.

## Rights status

Still publication-blocked. rev0844 reduces future accidental publication/clobber risk; it does not add or infer license terms.

---

## Previous rev0843 README

# EvidenceVault rev0843 overlay/patch refactor bundle

This bundle is a rev0843 risk-reduction overlay derived from the rev0842 refactor bundle. It is **not** a signed canonical EvidenceVault release artifact and it does **not** make the datacube publication-ready.

The canonical rev0840 patch payloads remain available and unchanged:

```bash
# From a rev0839-patched expanded tree:
patch -p1 < PATCHES/rev0839-to-rev0840-incremental.patch

# From fresh expanded rev0826:
patch -p1 < PATCHES/rev0826-to-rev0840-cumulative.patch
```

rev0843 adds a small overlay patch for this session's targeted changes:

```bash
# Overlay-level patch against the rev0842 bundle contents:
patch -p1 < PATCHES/rev0842-to-rev0843-overlay.patch
```

## What rev0843 changes

- Finishes the concrete rebuild-index subprocess refactor by moving `build_source_index.py` out of the long-lived `rebuild_indexes.py` coordinator. The parent now launches it as a child process and validates `SOURCE_INDEX.json` / `SOURCE_INDEX.md` as a handoff before downstream refreshes.
- Adds `scripts/validate_rebuild_indexes_source_index_subprocess_rev0843.py` and `AUDIT/REBUILD_INDEXES_SOURCE_INDEX_SUBPROCESS_REV0843.*` with fixture probes for successful handoff, child nonzero failure, empty JSON failure, and bytecode suppression.
- Hardens `scripts/publish_queue_item.py` for the future rights-approved path: public release snapshot/record/note outputs use same-directory atomic writes, pre-existing snapshots block, and ordinary queue-transition failures roll back newly created outputs.
- Adds `scripts/validate_publish_queue_item_atomic_outputs_rev0843.py` and `AUDIT/PUBLISH_QUEUE_ITEM_ATOMIC_OUTPUTS_REV0843.*` with rights-ready temporary fixtures proving rollback and successful emission behavior.
- Refreshes the rev0839 rebuild-index subprocess audit and the rev0840 publication preflight/dry-run safety audit where this partial overlay can safely do so.

## Important validation note

`MANIFEST.sha256`, `INDEX/files.*`, `RELEASE_MANIFEST.json`, `ro-crate-metadata.json`, and the SPDX file inventory remain canonical-tree/release surfaces carried by this overlay. For this ZIP as an overlay artifact, verify `CHECKS/overlay-manifest.json` and `CHECKS/overlay-manifest.sha256` first.

## Rights status

Still publication-blocked. rev0843 reduces accidental partial-publication risk for a future rights-approved queue path; it does not add or infer license terms.

---

## Previous rev0842 README

# EvidenceVault rev0842 overlay/patch refactor bundle

This bundle is a rev0842 risk-reduction overlay derived from the rev0841 review bundle. It is **not** a signed canonical EvidenceVault release artifact and it does **not** make the datacube publication-ready.

The canonical rev0840 patch payloads remain available and unchanged:

```bash
# From a rev0839-patched expanded tree:
patch -p1 < PATCHES/rev0839-to-rev0840-incremental.patch

# From fresh expanded rev0826:
patch -p1 < PATCHES/rev0826-to-rev0840-cumulative.patch
```

rev0842 adds a small overlay patch for this session's targeted changes:

```bash
# Overlay-level patch against the rev0841 review bundle contents:
patch -p1 < PATCHES/rev0841-to-rev0842-overlay.patch
```

## What rev0842 changes

- Hardens `scripts/publication_rights_gate.py` with a fresh, narrow runtime scan for local `LICENSE` / `COPYING` / `NOTICE` references. A stale generated rights ledger can no longer be the only protection against a missing local rights-file reference.
- Adds `scripts/validate_publication_rights_gate_fresh_scan_rev0842.py`, proving missing references block, resolved references pass, stale counts block when comparable, partial scan scopes fail closed, and the CLI emits no Python bytecode.
- Refactors `scripts/rebuild_indexes.py` so `build_dedupe_report.py` and `build_spdx_inventory.py` run as isolated subprocesses instead of being imported into the long-lived rebuild coordinator.
- Adds focused audits for the fresh rights scan and the rebuild-index subprocess finish.
- Adds targeted validation output for the changed paths.
- Adds a non-cyclic in-toto/SLSA-style provenance statement for the overlay tree and an explicit rev0842 patch-bundle identity file.

## Important validation note

`MANIFEST.sha256`, `INDEX/files.*`, `RELEASE_MANIFEST.json`, `ro-crate-metadata.json`, and the SPDX file inventory remain canonical-tree/release surfaces carried by this overlay. For this ZIP as an overlay artifact, verify `CHECKS/overlay-manifest.json` and `CHECKS/overlay-manifest.sha256` first.

## Rights status

Still publication-blocked. rev0842 strengthens the refusal path; it does not add or infer license terms.

---

## Previous rev0841 README

# EvidenceVault rev0841 overlay/patch review bundle

This bundle is a rev0841 review/hygiene overlay derived from the uploaded rev0840 overlay/patch bundle. It is **not** a signed canonical EvidenceVault release artifact and it does **not** make the datacube publication-ready.

The canonical patch payloads remain the rev0840 patch streams:

```bash
# From a rev0839-patched expanded tree:
patch -p1 < PATCHES/rev0839-to-rev0840-incremental.patch

# From fresh expanded rev0826:
patch -p1 < PATCHES/rev0826-to-rev0840-cumulative.patch
```

The cumulative patch is a patch stream: rev0826 -> rev0839, followed by rev0839 -> rev0840.

## What rev0841 adds

- `SESSION_REVIEW_REV0841.md` / `.json`: deep review findings, missing pieces, waste points, and suggested correction path.
- `AUDIT/OVERLAY_ABSOLUTE_PATH_REFERENCE_AUDIT_REV0841.md` / `.json`: overlay-level scan for cloudtainer-local path references.
- `CHECKS/patch-bundle-identity-rev0841.json`: explicit distinction between this overlay bundle identity and the rev0826 canonical release identity surfaces carried inside it.
- `CHECKS/input-artifacts.sha256`: normalized to input archive basenames instead of cloudtainer-local absolute input paths.

## Important validation note

`MANIFEST.sha256`, `INDEX/files.*`, `RELEASE_MANIFEST.json`, `ro-crate-metadata.json`, and `SBOM/spdx.json` remain canonical-tree/release surfaces carried by the overlay. For this ZIP as an overlay artifact, verify `CHECKS/overlay-manifest.json` and `CHECKS/overlay-manifest.sha256` first.

## rev0856 overlay note

The active proofcore lane is now transcript-bound:

```bash
python3 scripts/validate_sumcheck_fs_lane_rev0856.py
```

This revision addresses a concrete proof-system risk from the rev0855 toy
sumcheck harness: explicit challenge fields are no longer trusted unless they
match deterministic challenge derivation over public context, payload manifest
identity, rights-block state, prior transcript messages, and the current round
polynomial.

## rev0857 overlay note

The active proofcore lane is now payload-admission and transcript-prefix hardened:

```bash
python3 scripts/validate_streamfold_payload_admission_rev0857.py
```

This revision does two practical things: it turns the 17-path streamfold payload gate into an executable candidate-root verifier, and it derives toy sumcheck challenges from previous public transcript-message hashes plus round running claims. The canonical streamfold payload bytes are still absent from this overlay and publication remains blocked.

## rev0858 proofcore lane

rev0858 makes the active streamfold proofcore lane more operational:

```bash
python3 scripts/validate_framed_transcript_receipt_rev0858.py
```

It adds recomputable payload absence receipts, a fixed framed transcript operation log, and candidate-root negative controls. The canonical streamfold payload bytes remain absent, and publication remains blocked pending rights decisions.

## rev0859 proofcore lane

rev0859 makes a targeted liveness correction in the proof-carrying-data lane. The rev0858 payload receipts remain intact, but the legacy rev0858 payload-receipt verifier is no longer the active endpoint because it can hang in this cloudtainer while waiting on a captured subprocess pipe. The new active replay command is:

```bash
python3 scripts/validate_payload_receipt_liveness_rev0859.py
```

This revision adds an in-process receipt verifier, a parent-linked liveness lane, and a subprocess-surface audit. The 17 canonical streamfold payload bytes remain absent and publication remains blocked pending rights decisions.

## rev0860 payload graft engine candidate staging

rev0860 keeps the proof-carrying-data work on the riskiest unfinished edge: the canonical `streamfold_sumcheck_toy_v2` payload bytes are still absent. This revision does not invent those bytes. It adds an exact-hash graft engine that can verify a mounted candidate root and stage only matching payload files into an isolated directory outside the overlay.

Primary command:

```bash
python3 scripts/validate_streamfold_payload_graft_rev0860.py
```

Candidate-root command when a canonical tree is available:

```bash
python3 PROOFCORE/verifiers/prepare_streamfold_payload_graft_rev0860.py --candidate-root /path/to/canonical/tree --mode minimum --stage-dir /tmp/ev-streamfold-minimum-graft --json
```

Publication remains blocked; no root license, notice, recovered payload bytes, SNARK proof, zero-knowledge proof, or streamfold correctness claim is added.


## rev0861 overlay note — loose payload locator

rev0861 makes the active streamfold payload recovery lane less brittle. rev0860
requires candidate payloads to appear at canonical paths; rev0861 can scan loose
candidate roots for exact byte-count/SHA-256 matches and stage a complete unique
match set back to canonical paths outside the overlay.

Current active validation:

```bash
python3 scripts/validate_streamfold_loose_payload_locator_rev0861.py
```

Candidate-root example:

```bash
python3 PROOFCORE/verifiers/locate_streamfold_payloads_rev0861.py \
  --candidate-root /path/to/cache-or-export \
  --mode minimum \
  --stage-dir /tmp/ev-streamfold-loose-minimum \
  --json
```

The streamfold payload bytes remain absent and publication remains blocked.

## rev0862 overlay note

rev0862 adds a ZIP-aware archive payload search lane for the active streamfold
payload recovery frontier. It scans real directories and ZIP artifacts by exact
byte count/SHA-256 and records a negative cloudtainer search over 12 visible
EvidenceVault ZIP artifacts. The canonical streamfold payload bytes remain
absent and publication remains blocked by rights status.
