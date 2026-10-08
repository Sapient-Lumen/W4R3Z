# Change summary — rev0874

rev0874 closes a demonstrated verified-bytes/executed-bytes split instead of adding another registry.

## Corrected

- Reproduced the exact rev0873 gate passing preflight, executing substituted validator bytes, restoring the original, passing postflight, and reporting success.
- Rebuilt `scripts/overlay_gate.py` as a self-contained inventory-verifying bootstrap that executes coverage and all checks from one private verified snapshot.
- Isolated the gate and child interpreters with Python `-I -S`, scrubbed Python path/startup variables, and added source plus snapshot postflight revalidation.
- Added deterministic source-swap, `PYTHONPATH`, local stdlib-shadow, and inherited ZIP-snapshot regressions.

## Audited

- Swept 12 retained sibling ZIPs / 7,305 file members. All 113 unique exact canonical paths found were already available; zero new or duplicate bytes were admitted.
- Preserved current coverage: 109 exact current-path files, 125 rehydratable files, and 4,461 unavailable files.

## Still blocked

No rights decision was invented. Root/component rights closure, all 17 selected StreamFold payloads, and canonical `README.md` remain unresolved.

---

# rev0873 — descriptor-bound ZIP validation and transport snapshot

- Reproduced a severe rev0872 false-success boundary: one ZIP was structurally validated, then a pathname replacement caused the final report to carry a non-ZIP replacement's SHA-256 while retaining the original size.
- Refactored `scripts/validate_zip_container.py` to open once, snapshot once, validate all structure and payloads on the immutable descriptor snapshot, and revalidate retained source bytes plus path identity before success.
- Added deterministic regressions for exact-parent false success, current pathname replacement, same-inode mutation, stable operation, and the inherited rev0872 root/path boundary.
- Audited canonical README patch states and the 64-file OCF v244 batch-output family; admitted zero guessed bytes. Coverage is unchanged.

# rev0872 — root-substitution closure and canonical path identity

- Reproduced a rev0871 root-exchange defect against exact parent script hashes: materialization wrote into a replacement directory, and coverage hashed replacement bytes.
- Added `scripts/root_anchor.py` and retained one root device/inode/type identity across canonical reads, external-target validation, and exact-byte writes.
- Closed both already-exact success branches so a detached or replacement root cannot be approved after inspection.
- Replaced path-alias normalization with strict canonical spelling across seven active consumers, including the overlay-chain and both patch-recovery parsers.
- Added four deterministic root-swap regressions, stable-root coverage/write checks, and symlink-root rejection.
- Fixed a release-boundary self-mutation defect: six entrypoints now disable bytecode before local imports, and nine sandbox probes reject any emitted `__pycache__` or `.pyc`.
- Re-ran exact-byte recovery frontiers; no candidate met path, size, and full SHA-256, so coverage remains 109 exact and 125 rehydratable files.

See `AUDIT/ROOT_ANCHOR_PATH_IDENTITY_REV0872.md`.

---

# rev0871 — exact PCB digests and one safe recovery writer

- Recovered two indexed PCB subject digest files, **144 exact bytes**, from full digest strings preserved in the cumulative patch.
- Increased exact current-path coverage to **109 files** and rehydratable coverage to **125 files / 4,973,641 bytes**.
- Added `scripts/safe_materialize.py` and migrated the patch-corpus, overlay-history, rev0870, and rev0871 recovery tools to the same descriptor-bound no-clobber implementation.
- Added regressions proving pre-existing mismatch preservation, `O_EXCL` race-winner preservation, symlink rejection, exact race-winner acceptance, mode normalization, and descriptor read-back.
- Audited reverse overlay history, complete old-side patch streams, embedded scalars/subobjects, and 174 content-addressed PACT objects. No unverified bytes were admitted.

See `AUDIT/EMBEDDED_DIGEST_RECOVERY_SAFE_MATERIALIZATION_REV0871.md`.

---

# rev0870 change summary

## Exact byte recovery

Recovered four complete canonical OCF source files totaling 53 bytes, each accepted only after path-specific size and SHA-256 equality with `INDEX/files.csv`:

- `sources/ocf_llm/examples/discovery_sdt_demo_v247/output.txt`
- `sources/ocf_llm/examples/dsc_summary_v1.json`
- `sources/ocf_llm/examples/dsc_buc_summary_v1.json`
- `sources/ocf_llm/examples/dsc_cbb_summary_v1.json`

Coverage moved from 103 to **107 exact canonical files** and from 119 to **123 rehydratable files**.

## Audit and refactor

- Added a bounded verify-first/no-clobber recovery engine.
- Audited 270 duplicate identity groups and found no additional unresolved path with bytes already available.
- Refactored `canonical_coverage.py` to bind path traversal, regular-file identity, hashing, and post-read path identity to stable descriptors.
- Added regressions for root-symlink aliases, same-size path replacement, in-place mutation, overwrite attempts, and symlink-parent escape.
- Confirmed that this cloudtainer can follow a directory symlink despite `O_NOFOLLOW`; component opens now bind explicit no-follow metadata before/after open to the descriptor inode.
- Found and fixed a recovery-writer cleanup bug where an `O_EXCL` overwrite refusal could unlink the pre-existing file it had protected.
- Refactored the rev0869 validator to enforce historical baselines monotonically on later revisions instead of falsely failing after legitimate recoveries.
- Removed a wasteful 32-second recursive replay of the entire historical ZIP-builder suite from every current gate. The active validator now reruns the exact inherited bytes and demonstrated local-extra exploit; the complete rev0869 suite remains a one-time release check.

Rights and StreamFold blockers are unchanged.

---

# Change summary — rev0869

rev0869 delivers two exact canonical files and closes two demonstrated build/transport integrity defects.

## Recovered

- Restored `sources/ocf_llm/examples/refused_set_empty_v1.json` and `sources/pact/PACT_workdir/eval_real_registry_semantic_scan/out/violations.json` as exact two-byte `[]` files, each matching indexed SHA-256 `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`.
- Raised exact at-path coverage from 101 to **103 files** and rehydratable coverage from 117 to **119 files**.

## Corrected

- Closed a rev0868 local/central pathname split: a local-header-only `0x7075` Unicode Path field carrying `../escape.txt` was previously accepted while the central name stayed safe. Unsupported extra fields are now rejected and local/central flags and extraction versions must agree exactly.
- Replaced mutable enumerate-then-read packaging with a complete hash/stat source snapshot, per-file identity/digest checks, two whole-tree revalidations, and final published-inode/byte verification.

## Tested

- Retained the complete rev0868 adversarial ZIP/reproducibility suite.
- Added exploit regression for the local-only Unicode pathname alias and mutation regressions for same-size content replacement, late file addition, and file-to-symlink swap.

## Still blocked

No owner-approved root rights decision or StreamFold payload bytes were added. Canonical `README.md` remains the sole unresolved present-path mismatch.

---

# Change summary — rev0868

## Recovered bytes

- Restored one exact canonical source file: `sources/ocf_llm/examples/output_credential_demo_v242/credential_digest.txt` (72 bytes; SHA-256 `9027fea3c23dae8180fda581b02836c4f081a730ab2955346b9522d8c9c97ac8`).
- Acceptance is hash-gated: the surviving report value plus LF had to match canonical path, size, and SHA-256. No adjacent credential or proof material was inferred.
- At-path exact coverage rises from 100 to **101 files**; unavailable canonical files fall from 4,470 to **4,469** when recovery objects are included.

## Refactored and hardened

- Added `scripts/validate_zip_container.py` to reject ambiguous source ZIPs before extraction and verify archived bytes against the embedded overlay manifest.
- Added `scripts/build_deterministic_zip.py` for stable ordering/metadata, symlink refusal, temporary-archive validation, atomic publication, and a regression-pinned `0644` output mode.
- Added adversarial tests for duplicate names, traversal, case collisions, symlink entries, local/central header disagreement, prefixed/trailing bytes, occupied-output preservation, and repeat-build byte identity.
- Made the rev0867 historical-recovery validator forward-compatible: fixed recovery identities remain exact, while later hash-proved coverage may improve monotonically.

## Still blocked

No root rights decision was invented. The 17 selected StreamFold payloads and canonical `README.md` version remain unavailable.

---

# Change summary — rev0867

rev0867 converts implicit reverse-patch states into durable canonical recovery
bytes and refactors the gate so historical canonical surfaces cannot be confused
with live overlay availability.

## Substantive recovery

- Materialized 16 exact canonical versions totaling 88,101 bytes in a
  content-addressed recovery store.
- Added a replay engine that independently reconstructs those versions from the
  incremental overlay chain and admits only exact index path/size/SHA-256 matches.
- Added a safe external materializer: identical canonical index required, no
  overwrite, symlink ancestry rejected, and bundle overlap rejected.
- Reduced unprotected same-path mismatches from 17 to one. The active newer files
  remain untouched; `README.md` is the sole mismatch without a historical match.

## Audit and refactor

- Split **at-path representation** from **rehydratable byte availability** in
  `canonical_coverage.py` and `overlay_gate.py`.
- Added live anti-forgery checks for the recovery profile.
- Audited root rev0826 release/SBOM/manifest/dedupe/Makefile surfaces and labeled
  their correct role as historical canonical evidence, not current overlay truth.
- Made the rev0866 historical recovery validator resilient to later overlay edges
  while keeping its original 27-patch corpus frozen.

## Still blocked

No rights decision was invented. The root license/notice blocker, 4,470
unavailable canonical files, the unrecovered canonical README version, and all 17
selected StreamFold payloads remain open.

---

# Change summary — rev0866

rev0866 favors recovered bytes and executable safeguards over another doctrine layer.

## Recovered

- Restored 81 previously missing canonical indexed files totaling 546,423 bytes from complete new-side streams in the existing patch corpus.
- Restored 12 canonical source payloads totaling 13,568 bytes across dOCF and OCF LLM examples.
- Raised exact canonical coverage from 19 to 100 files and reduced missing indexed paths from 4,550 to 4,469.

## Added and refactored

- Added `scripts/recover_indexed_files_from_patches.py`, an exact size-and-hash-gated, external-target-only, no-clobber recovery engine.
- Added `scripts/canonical_coverage.py` as the shared live representation engine.
- Refactored `scripts/overlay_gate.py` to recompute coverage and reject stale manifest claims before any list or run operation.
- Added `AUDIT/PATCH_CORPUS_EXACT_RECOVERY_REV0866.*` and `scripts/validate_patch_corpus_recovery_rev0866.py`.
- Audited the canonical Makefile surface: 42 of 47 referenced script paths remain absent, so `make gate` is still not a valid overlay entrypoint.

## Deliberately unchanged

- Five patch candidates at existing paths were not overwritten because later overlay revisions changed their bytes.
- The recovered `RIGHTS/NOTICE.draft` is not promoted to a root notice or rights grant.
- Publication remains blocked, and no StreamFold target payload was recovered.

---

# Change summary — rev0865

rev0865 spends the session on real bytes and a concrete gate defect rather than adding another doctrine/search layer.

## Recovered

- Added the exact canonical `modelcontextprotocol/servers` README at `sources/pact/PACT_workdir/eval_real_registry_scan/servers_README.md` (356,744 bytes; SHA-256 `0f7174a89094f7695b899fad71c2e6d0fb12cd6041734d779aacd8a8bfe400c2`).
- Added file-level rights/attribution evidence for that unchanged README. Its exact adjacent upstream license assigns documentation excluding specifications to `CC-BY-4.0`; no broader PACT or archive conclusion is made.

## Audited

- Measured canonical representation directly from `INDEX/files.csv`: 19 exact files, 17 same-path mismatches, and 4,550 missing files out of 4,586 rows. Canonical `sources/` coverage is 1 exact file out of 3,476.
- Preserved the three absent README-analysis companion identities without fabricating replacements.

## Refactored

- Reversed the rev0864 report contract that could brick the bundle by writing an unmanifested report inside it.
- Reports now resolve outside the archive, use atomic replacement, and reject symlink ancestry.
- Integrity is mandatory for selected checks and runs both before and after other checks.
- Selected-check runs are labeled `NOT A FULL GATE`; every gate result exposes partial canonical coverage.

## Still blocked

No root license/notice or component-wide rights decision was invented. The canonical tree is still overwhelmingly absent, and all 17 StreamFold target payloads remain missing.

---

# Change summary — rev0864

rev0864 prioritizes byte recovery and operator-time reduction over new doctrine or proof lanes.

## Completed

- Recovered the exact 12,227-byte upstream `LICENSE` referenced by the canonical PACT MCP servers README, pinned to official commit `f4244583a6af9425633e433a3eec000d23f4e011`.
- Updated local-license-reference, rights-evidence, and component-readiness surfaces: the missing-reference count is now 0; the root rights blocker and all `NOASSERTION` component conclusions remain.
- Audited all 25 parent patch files and found no exact diff section for any of the 17 missing StreamFold payload paths. Patch-body recovery is now a retired path absent new source material.
- Replaced the multi-command overlay startup path with `python3 scripts/overlay_gate.py`.

## Still blocked

No root license/notice, archive-wide publication authorization, canonical StreamFold payload bytes, SNARK/zero-knowledge proof, or signed external attestation was added.

---

# Change summary — rev0857

rev0857 focuses on the riskiest active proofcore gap: the selected streamfold payload lane still has no canonical payload bytes in the overlay, and the transcript-binding harness needed stronger round-prefix binding.

## Added

- `PROOFCORE/verifiers/verify_streamfold_payload_candidate_rev0857.py`: executable candidate-root admission verifier for the 17 canonical `streamfold_sumcheck_toy_v2_family` payloads.
- `PROOFCORE/verifiers/verify_sumcheck_fs_prefix_transcript_rev0857.py`: transparent toy sumcheck verifier that binds previous public transcript-message hashes into challenge derivation.
- `PROOFCORE/verifiers/verify_streamfold_payload_admission_lane_rev0857.py`: parent-linked PCD-shaped lane that replays rev0856 before accepting rev0857 surfaces.
- `PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0857/*`: admission contract, protocol profile, transcript-prefix contract, absence reports, and accept/reject fixtures.
- `AUDIT/PAYLOAD_ADMISSION_TRANSCRIPT_PREFIX_REV0857.*`: audit/refactor of the active proofcore verifier and payload recovery surface.
- `scripts/validate_streamfold_payload_admission_rev0857.py`: targeted validator for the new lane.

## Still blocked

The overlay still contains none of the 17 canonical streamfold payload bytes. No rights grant, root license/notice, SPDX conclusion, RO-Crate rights assertion, SNARK proof, zero-knowledge proof, succinct proof, production Fiat-Shamir claim, or streamfold correctness claim was added.

# Change summary — rev0858

rev0858 focuses on the riskiest active proofcore gap: payload absence/admission checks needed portable evidence, and transcript binding needed a stricter operation surface than loose prior-message hashes.

## Added

- `PROOFCORE/verifiers/verify_streamfold_payload_receipt_rev0858.py`: recomputes rev0857 payload candidate verifier outputs and validates portable full/minimum absence receipts.
- `PROOFCORE/verifiers/verify_sumcheck_fs_framed_transcript_rev0858.py`: verifies a transparent toy sumcheck transcript as a fixed labeled absorb/challenge operation log.
- `PROOFCORE/verifiers/verify_streamfold_framed_receipt_lane_rev0858.py`: parent-linked PCD-shaped lane that replays rev0857 before accepting rev0858 surfaces.
- `PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/*`: payload receipt contract, absence receipts, framed transcript contract/profile, candidate-root attack matrix, and accept/reject fixtures.
- `AUDIT/FRAMED_TRANSCRIPT_RECEIPT_REV0858.*`: audit/refactor of payload receipts, framed transcript binding, and candidate-root symlink negative controls.
- `scripts/validate_framed_transcript_receipt_rev0858.py`: targeted validator for the new active lane.

## Refactored

- `PROOFCORE/verifiers/verify_streamfold_payload_candidate_rev0857.py`: candidate-root symlink detection now checks the raw operator-supplied path before resolving it.
- `scripts/validate_streamfold_payload_admission_rev0857.py`: rev0857 is treated as a historical checkpoint when carried by rev0858.

## Still blocked

The overlay still contains none of the 17 canonical streamfold payload bytes. No rights grant, root license/notice, SPDX conclusion, RO-Crate rights assertion, SNARK proof, zero-knowledge proof, succinct proof, production Fiat-Shamir claim, or streamfold correctness claim was added.

# Change summary — rev0859

rev0859 focuses on the riskiest active proofcore failure found during this pass: the rev0858 payload-receipt verifier can emit an OK marker while not returning in this cloudtainer because its source-report recomputation is mediated through captured subprocess pipes.

## Added

- `PROOFCORE/verifiers/verify_streamfold_payload_receipt_inprocess_rev0859.py`: validates the rev0858 payload absence receipts by importing the rev0857 candidate verifier from the selected root and recomputing the source report in-process.
- `PROOFCORE/verifiers/verify_streamfold_payload_receipt_liveness_lane_rev0859.py`: parent-linked PCD-shaped lane that reconstructs rev0858 and checks its receipt/transcript surfaces without invoking the liveness-quarantined legacy endpoint.
- `PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0859/*`: receipt liveness contract and lane README.
- `AUDIT/PAYLOAD_RECEIPT_LIVENESS_REV0859.*`: audit/refactor record for the subprocess-pipe liveness risk and active in-process replay replacement.
- `scripts/validate_payload_receipt_liveness_rev0859.py`: targeted validator for the new active lane.

## Refactored

- `scripts/validate_framed_transcript_receipt_rev0858.py`: rev0858 is treated as a historical checkpoint when carried by rev0859, avoiding the liveness-quarantined endpoint.

## Still blocked

The overlay still contains none of the 17 canonical streamfold payload bytes. No rights grant, root license/notice, SPDX conclusion, RO-Crate rights assertion, SNARK proof, zero-knowledge proof, succinct proof, production Fiat-Shamir claim, or streamfold correctness claim was added.

## rev0860 — payload graft engine candidate staging

- Added `PROOFCORE/verifiers/prepare_streamfold_payload_graft_rev0860.py`, an exact-hash isolated staging engine for future streamfold payload recovery.
- Added full and minimum dry-run reports proving the current overlay still contains zero canonical streamfold payload bytes.
- Added a synthetic graft-engine self-test covering positive staging and reject controls for hash mismatch, path traversal, output inside the overlay, and candidate symlink ancestry.
- Added parent-linked `verify_streamfold_payload_graft_lane_rev0860.py` and a new transparent PCD-style claim/public-input/commitment/certificate lane.
- Refactored the rev0859 liveness validator into a historical checkpoint in rev0860 bundles so operators use rev0860 parent replay instead of rerunning stale endpoint assumptions.

Still blocked: no root license, notice, SPDX/RO-Crate rights assertion, canonical streamfold payload bytes, SNARK proof, zero-knowledge proof, succinct proof, production Fiat-Shamir claim, or streamfold correctness claim is invented.


# Change summary — rev0861

rev0861 focuses on the riskiest active proofcore recovery gap: rev0860 can stage
future streamfold payloads only when a candidate tree already preserves exact
canonical paths. That is safe but brittle. Real recovery may expose the right
bytes in caches, exports, object-store dumps, or differently rooted trees.

## Added

- `PROOFCORE/verifiers/locate_streamfold_payloads_rev0861.py`: scans one or more
  real candidate roots for expected `streamfold_sumcheck_toy_v2` payloads by exact
  byte count and SHA-256, without following symlinks.
- `PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0861/*`: loose locator contract,
  full/minimum no-candidate absence reports, synthetic self-test report, and lane
  README.
- `PROOFCORE/verifiers/verify_streamfold_loose_payload_locator_lane_rev0861.py`:
  parent-linked PCD-shaped verifier that replays rev0860 before accepting rev0861.
- `AUDIT/LOOSE_PAYLOAD_LOCATOR_REV0861.*`: audit/refactor record for loose-path
  payload recovery, duplicate-match blocking, symlink skipping, and unsafe-stage
  rejection.
- `scripts/validate_streamfold_loose_payload_locator_rev0861.py`: targeted
  validator for the new active lane.

## Refactored

- `scripts/validate_streamfold_payload_graft_rev0860.py`: rev0860 is treated as a
  historical checkpoint when carried by rev0861, avoiding stale active-endpoint
  assumptions.

## Still blocked

The overlay still contains none of the 17 canonical streamfold payload bytes. No
rights grant, root license/notice, SPDX conclusion, RO-Crate rights assertion,
SNARK proof, zero-knowledge proof, succinct proof, production Fiat-Shamir claim,
or streamfold correctness claim was added.

# Change summary — rev0862

rev0862 focuses on the riskiest remaining payload-recovery bottleneck: rev0861 can scan loose directories, but visible cloudtainer and future export material may arrive as ZIP artifacts. The new lane adds ZIP-aware archive search and records an actual negative search over the EvidenceVault ZIP artifacts visible in this session.

## Added

- `PROOFCORE/verifiers/locate_streamfold_payload_archives_rev0862.py`: scans real directories and ZIP archives for expected `streamfold_sumcheck_toy_v2` payloads by exact byte count and SHA-256, without full extraction.
- `PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0862/*`: archive search contract, full/minimum no-candidate absence reports, synthetic self-test report, cloudtainer ZIP negative search receipt, and lane README.
- `PROOFCORE/verifiers/verify_streamfold_archive_payload_search_lane_rev0862.py`: parent-linked PCD-shaped verifier that replays rev0861 before accepting rev0862.
- `AUDIT/ARCHIVE_PAYLOAD_SEARCH_REV0862.*`: audit/refactor record for ZIP-aware payload search and the negative search across visible EvidenceVault ZIP artifacts.
- `scripts/validate_streamfold_archive_payload_search_rev0862.py`: targeted validator for the new active lane.

## Refactored

- The active proofcore surface moves from directory-only loose payload location to a ZIP-aware archive payload search layer. rev0861 is now the historical parent checkpoint for rev0862.

## Still blocked

The overlay still contains none of the 17 canonical streamfold payload bytes. The cloudtainer ZIP search receipt found zero matches in the 12 visible EvidenceVault ZIP artifacts, but that is only a negative local search, not proof the payloads do not exist elsewhere. No rights grant, root license/notice, SPDX conclusion, RO-Crate rights assertion, SNARK proof, zero-knowledge proof, succinct proof, production Fiat-Shamir claim, or streamfold correctness claim was added.

# Change summary — rev0863

rev0863 recenters the bundle around mission, rights, identity, and cloudtainer-waste triage after rev0862 added ZIP-aware payload search.

## Added

- `AUDIT/MISSION_RECENTER_RIGHTS_IDENTITY_TRIAGE_REV0863.*`: a deep read of mission, missing pieces, severe/wasteful patterns, and correction paths.
- `RIGHTS/RIGHTS_DECISION_PACKET_REV0863.*`: a decision packet built from the existing rights ledger and license evidence scan, with no invented license conclusions.
- `PATCH_BUNDLE_MANIFEST.json`: a first-class overlay/patch-bundle identity surface separate from carried rev0826 canonical release metadata.
- `scripts/validate_mission_recenter_rights_identity_rev0863.py`: targeted validator for the new mission/right/identity surfaces.

## Refactored

- Prepended `README.md` and `OVERLAY_COMMANDS.md` with current rev0863 guidance so operators do not start from stale rev0855 headings.
- Preserved the rev0862 proofcore archive search lane as the active payload-search endpoint while changing session priority toward rights/identity/provenance closure.

## Still blocked

No root license, notice, SPDX/RO-Crate rights assertion, canonical streamfold payload bytes, SNARK proof, zero-knowledge proof, succinct proof, production Fiat-Shamir claim, streamfold correctness claim, or signed external attestation was added.
