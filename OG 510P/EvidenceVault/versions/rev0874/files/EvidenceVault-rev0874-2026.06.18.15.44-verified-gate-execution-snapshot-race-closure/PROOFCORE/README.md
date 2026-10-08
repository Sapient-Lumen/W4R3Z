# EvidenceVault PROOFCORE — rev0855 streamfold sumcheck lane gate

rev0855 takes the rev0854 recommended target, `streamfold_sumcheck_toy_v2_family`, and makes it executable without pretending the missing canonical payloads are present.

## New claim implemented

`claims/ev-streamfold-sumcheck-lane.rev0855.claim.json` states that the rev0854 parent frontier checkpoint can be replayed, that the 17-path streamfold payload gate exactly matches the carried canonical index and remains absent from this overlay, and that a transparent toy sumcheck transcript verifier accepts a known-good transcript while rejecting a tampered first-round polynomial.

Run it:

```bash
python3 PROOFCORE/verifiers/verify_streamfold_sumcheck_lane_rev0855.py --fixture PROOFCORE/fixtures/accept/ev-streamfold-sumcheck-lane.rev0855.accept.json
python3 PROOFCORE/verifiers/verify_streamfold_sumcheck_lane_rev0855.py --fixture PROOFCORE/fixtures/reject/ev-streamfold-sumcheck-lane.rev0855.reject.json --expect-fail
```

The raw toy sumcheck verifier can also be run directly:

```bash
python3 PROOFCORE/verifiers/verify_sumcheck_transcript_rev0855.py --fixture PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0855/fixtures/sumcheck_accept.rev0855.json
```

Explicit non-claim: this is not a zk-SNARK, not zero knowledge, not succinct, and not proof-system soundness for absent streamfold payloads.

---

# EvidenceVault PROOFCORE — rev0854 parent-linked frontier lane

rev0854 adds a second transparent PCD lane. The new lane does not attempt to verify missing `streamfold` or `zkrtp` protocol payloads. It does something narrower and riskier to leave unfinished: it makes proofcore completion itself machine-checkable.

## New claim implemented

`claims/ev-proofcore-frontier.rev0854.claim.json` states that the rev0853 PCD checkpoint can be replayed as history and that the P0 proofcore frontier recomputes to eight concrete completion groups. The recommended next group is `streamfold_sumcheck_toy_v2_family`, because the canonical index shows ABI/IR, public-input-or-commitment, and attestation/receipt roles for that family.

Run it:

```bash
python3 PROOFCORE/verifiers/verify_proofcore_frontier_rev0854.py --fixture PROOFCORE/fixtures/accept/ev-proofcore-frontier.rev0854.accept.json
python3 PROOFCORE/verifiers/verify_proofcore_frontier_rev0854.py --fixture PROOFCORE/fixtures/reject/ev-proofcore-frontier.rev0854.reject.json --expect-fail
```

or use:

```bash
python3 scripts/validate_proofcore_frontier_pcd_rev0854.py
```

Explicit non-claim: this is not a zk-SNARK, not zero knowledge, and not proof-system soundness for absent payloads.

---

## Previous rev0853 PROOFCORE README

# EvidenceVault PROOFCORE — rev0853 first executable PCD lane

This directory starts the proof-carrying-data lane that rev0852 only planned. It is intentionally small and honest:

- it does **not** claim a zk-SNARK, zero knowledge, succinctness, or proof-system soundness for the recovered project payloads;
- it does provide one runnable proof-carrying envelope for a real local claim: this overlay's manifest, patch-chain, proofcore-lane, and rights-block state can be checked from public data;
- it adds a canonical-path-to-role map for the indexed proof-adjacent payloads so `zkrtp`, `streamfold`, receipts, witnesses, schemas, ABI IR, and verifiers have somewhere concrete to attach when the full tree is recovered.

## First claim implemented

`claims/ev-overlay-integrity.rev0853.claim.json` states that the extracted overlay bundle is internally consistent as an overlay artifact and remains publication-blocked. The certificate in `certificates/ev-overlay-integrity.rev0853.pcd.json` is a **transparent deterministic PCD envelope**, not a cryptographic SNARK proof.

Run it:

```bash
python3 PROOFCORE/verifiers/verify_pcd_envelope.py --fixture PROOFCORE/fixtures/accept/ev-overlay-integrity.rev0853.accept.json
python3 PROOFCORE/verifiers/verify_pcd_envelope.py --fixture PROOFCORE/fixtures/reject/ev-overlay-integrity.rev0853.reject.json --expect-fail
```

or use the session validator:

```bash
python3 scripts/validate_proofcore_pcd_rev0853.py
```

## Why this counts as forward motion

Explicit non-claim: this is not a zk-SNARK.

The project now has the shape PCD work needs: claim, public inputs, witness policy, verifier, accept fixture, reject fixture, certificate envelope, manifest, and a path-role map. The next lane can replace the transparent local verifier with a recovered `zkrtp` or `streamfold` verifier/receipt while keeping the same envelope contract.

## rev0856 transcript-bound streamfold sumcheck lane

rev0856 upgrades the active `streamfold_sumcheck_toy_v2` harness from arithmetic-only
toy transcript checking to deterministic transcript-bound challenge checking.
The active lane verifier is:

```bash
python3 PROOFCORE/verifiers/verify_streamfold_sumcheck_fs_lane_rev0856.py \
  --fixture PROOFCORE/fixtures/accept/ev-streamfold-sumcheck-fs-lane.rev0856.accept.json
```

The raw transcript verifier is:

```bash
python3 PROOFCORE/verifiers/verify_sumcheck_fs_transcript_rev0856.py \
  --fixture PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0856/fixtures/sumcheck_fs_accept.rev0856.json
```

This is not a production Fiat-Shamir transform, not a zk-SNARK, not zero
knowledge, not succinct, and not a canonical streamfold receipt verifier. It is a
substantive harness hardening step that binds the challenge to public context,
`payload_manifest_sha256`, rights-block state, prior transcript messages, and the
current round polynomial.

## rev0857 payload admission and transcript-prefix lane

The active proofcore lane is now:

```bash
python3 scripts/validate_streamfold_payload_admission_rev0857.py
```

rev0857 makes the streamfold payload gate executable:

```bash
python3 PROOFCORE/verifiers/verify_streamfold_payload_candidate_rev0857.py --mode full
python3 PROOFCORE/verifiers/verify_streamfold_payload_candidate_rev0857.py --candidate-root /path/to/full/canonical/tree --mode minimum
python3 PROOFCORE/verifiers/verify_streamfold_payload_candidate_rev0857.py --candidate-root /path/to/full/canonical/tree --mode full
```

The first command verifies the current overlay absence state. The candidate-root commands verify exact path, byte length, SHA-256, `INDEX/files.csv` agreement, JSON object parseability, and role coverage for either the four-file minimum recovery set or all 17 canonical streamfold payloads.

rev0857 also supersedes the rev0856 transcript-bound toy harness with a prefix-bound variant:

```bash
python3 PROOFCORE/verifiers/verify_sumcheck_fs_prefix_transcript_rev0857.py --fixture PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0857/fixtures/sumcheck_fs_prefix_accept.rev0857.json
```

This binds each challenge to previous public transcript-message hashes and the running claim before the round. It is not a zk-SNARK, not zero knowledge, not succinct, not a production Fiat-Shamir transform, and not a streamfold correctness proof.

## rev0858 framed transcript and payload absence receipts

rev0858 is the active proofcore endpoint. It does three concrete things:

1. Carries recomputable payload absence receipts for the full 17-file streamfold payload frontier and the 4-file minimum recovery set.
2. Replaces loose transcript-prefix binding with a fixed operation log: labeled absorbs and labeled challenges.
3. Adds a candidate-root symlink audit/refactor so the raw candidate root path is rejected if it is a symlink before path resolution.

Current command:

```bash
python3 scripts/validate_framed_transcript_receipt_rev0858.py
```

This remains transparent PCD-style scaffolding. It is not a SNARK, not zero knowledge, not succinct, not a production Fiat-Shamir transform, and not a rights grant. The canonical streamfold payload bytes remain absent from this overlay.

## rev0859 payload receipt liveness lane

rev0859 closes an operator-liveness risk found in the active PCD chain: the rev0858 payload-receipt verifier can emit its success marker while still waiting on a captured subprocess pipe in this cloudtainer. The rev0858 bytes are not mutated, because the rev0858 public inputs and certificate bind those historical hashes. Instead, rev0859 makes the active replay path in-process:

```bash
python3 PROOFCORE/verifiers/verify_streamfold_payload_receipt_inprocess_rev0859.py --receipt PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.full.rev0858.json
python3 PROOFCORE/verifiers/verify_streamfold_payload_receipt_inprocess_rev0859.py --receipt PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.minimum.rev0858.json
python3 PROOFCORE/verifiers/verify_streamfold_payload_receipt_inprocess_rev0859.py --receipt PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.reject_tampered_count.rev0858.json --expect-fail
python3 scripts/validate_payload_receipt_liveness_rev0859.py
```

The legacy rev0858 receipt verifier remains carried as a hash-bound historical artifact, but is liveness-quarantined and not the active endpoint. Parent replay for rev0859 reconstructs rev0858 and revalidates its receipt/transcript surfaces through the rev0859 in-process receipt verifier.

## rev0860 active lane — payload graft candidate-root staging

The active proofcore lane is now `streamfold_payload_graft_rev0860`. The point is practical: the 17 canonical `streamfold_sumcheck_toy_v2` payload paths are still absent, so rev0860 adds a safe way to admit them later without silently copying wrong bytes.

Use:

```bash
python3 scripts/validate_streamfold_payload_graft_rev0860.py
python3 PROOFCORE/verifiers/prepare_streamfold_payload_graft_rev0860.py --mode full --json
python3 PROOFCORE/verifiers/prepare_streamfold_payload_graft_rev0860.py --self-test --json
```

When a candidate-root canonical tree is available, run:

```bash
python3 PROOFCORE/verifiers/prepare_streamfold_payload_graft_rev0860.py --candidate-root /path/to/canonical/tree --mode minimum --stage-dir /tmp/ev-streamfold-minimum-graft --json
```

The rev0859 historical checkpoint is replayed by `PROOFCORE/verifiers/verify_streamfold_payload_graft_lane_rev0860.py`. rev0860 is still transparent and non-succinct: not a SNARK, not zero knowledge, not a rights grant, and not a recovered payload bundle.


## rev0861 active lane — loose payload locator and canonical staging

The active proofcore lane is now `streamfold_loose_payload_locator_rev0861`.
rev0860 made future payload grafting exact and safe, but it still assumed the
candidate root already had canonical paths. rev0861 addresses the more fragile
real recovery case: the right bytes may be in a loose cache, export, filesystem
search result, or unpacked object tree under non-canonical names.

Use:

```bash
python3 scripts/validate_streamfold_loose_payload_locator_rev0861.py
python3 PROOFCORE/verifiers/locate_streamfold_payloads_rev0861.py --mode full --json
python3 PROOFCORE/verifiers/locate_streamfold_payloads_rev0861.py --self-test --json
```

When a candidate-root cache/export is available, run:

```bash
python3 PROOFCORE/verifiers/locate_streamfold_payloads_rev0861.py \
  --candidate-root /path/to/cache-or-export \
  --mode minimum \
  --stage-dir /tmp/ev-streamfold-loose-minimum \
  --json
```

The locator matches by exact byte count and SHA-256, rejects symlink payloads,
blocks ambiguous duplicate hash matches, and stages only complete unique match
sets back to canonical paths outside the overlay. The rev0860 historical
checkpoint is replayed by
`PROOFCORE/verifiers/verify_streamfold_loose_payload_locator_lane_rev0861.py`.
rev0861 is still transparent and non-succinct: not a SNARK, not zero knowledge,
not a rights grant, not a recovered payload bundle, and not a streamfold
correctness proof.

## rev0862 active lane — ZIP-aware archive payload search

The active proofcore lane is now `streamfold_archive_payload_search_rev0862`.
rev0861 can locate loose payload bytes in directories, but a likely recovery
source is a ZIP/export artifact. rev0862 scans directories and ZIP archives by
exact byte count and SHA-256 without full extraction, then stages only complete
unique matches to canonical paths outside the overlay.

Use:

```bash
python3 scripts/validate_streamfold_archive_payload_search_rev0862.py
python3 PROOFCORE/verifiers/locate_streamfold_payload_archives_rev0862.py --mode full --json
python3 PROOFCORE/verifiers/locate_streamfold_payload_archives_rev0862.py --mode minimum --json
python3 PROOFCORE/verifiers/locate_streamfold_payload_archives_rev0862.py --self-test --json
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

The rev0862 cloudtainer ZIP search receipt scanned 12 visible EvidenceVault ZIP
artifacts and found zero `streamfold_sumcheck_toy_v2` payload matches. That is a
local negative receipt only. It is not proof the payloads do not exist elsewhere.
rev0861 is now the historical checkpoint replayed by the rev0862 lane verifier.
rev0862 is still transparent and non-succinct: not a SNARK, not zero knowledge,
not a rights grant, not a recovered payload bundle, and not a streamfold
correctness proof.

rev0862 note: the cloudtainer ZIP artifacts searched here are the EvidenceVault ZIP files visible in `/mnt/data` during this session; the receipt is intentionally marked non-portable.
