# Payload graft engine audit — rev0860

Status: `candidate_graft_engine_ready_payloads_still_absent`.

## Why this was the risky seam

The active streamfold lane had exact absence receipts and a liveness-safe receipt verifier, but there was still no safe, executable path for admitting the missing canonical payload bytes. That made the next real recovery step easy to postpone or perform unsafely. rev0860 adds an isolated exact-hash graft engine instead of another prose-only registry.

## What changed

Added `PROOFCORE/verifiers/prepare_streamfold_payload_graft_rev0860.py`. With no candidate root it recomputes the current honest state: all 17 streamfold sumcheck payloads are absent from the overlay. With a mounted candidate tree it verifies exact path, byte count, SHA-256, JSON object parseability, and symlink-free path ancestry. With `--stage-dir`, it copies only the selected verified payloads into an isolated staging directory outside the overlay.

The current overlay still contains zero canonical streamfold payload files. The full recovery set is 17 files / 25066 bytes. The minimum first recovery set is four files.

## New executable surfaces

```bash
python3 PROOFCORE/verifiers/prepare_streamfold_payload_graft_rev0860.py --mode full --json
python3 PROOFCORE/verifiers/prepare_streamfold_payload_graft_rev0860.py --mode minimum --json
python3 PROOFCORE/verifiers/prepare_streamfold_payload_graft_rev0860.py --self-test --json
python3 PROOFCORE/verifiers/prepare_streamfold_payload_graft_rev0860.py --candidate-root /path/to/canonical/tree --mode minimum --stage-dir /tmp/ev-streamfold-minimum-graft --json
```

## Refactor/audit result

The attack matrix now covers missing candidate roots, hash/size mismatch, path traversal, output inside the overlay, and candidate symlink ancestry. The rev0860 lane verifier also parent-replays rev0859 by reversing the rev0860 patch and restoring rev0859 cyclic CHECKS surfaces.

## Still blocked

No payload bytes were invented. No rights grant, publication clearance, SNARK proof, zero-knowledge proof, succinct proof, production Fiat-Shamir claim, or streamfold correctness claim is added.
