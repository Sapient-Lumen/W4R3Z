# Payload receipt liveness audit — rev0859

rev0859 fixes the riskiest active seam found in the proofcore lane: the rev0858 payload-receipt verifier can emit its success marker while remaining live in a subprocess pipe wait in this cloudtainer. That is an operator-liveness failure, not a payload-integrity failure.

## Priority correction

The rev0858 receipt bytes and legacy verifier bytes are left intact because rev0858 public inputs and certificates bind their hashes. Instead, rev0859 adds an active in-process verifier:

```text
PROOFCORE/verifiers/verify_streamfold_payload_receipt_inprocess_rev0859.py
```

It loads the rev0857 payload candidate verifier from the selected root and recomputes the same source report without spawning a child process or capturing stdout/stderr pipes.

## What is now active

```bash
python3 PROOFCORE/verifiers/verify_streamfold_payload_receipt_inprocess_rev0859.py --receipt PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.full.rev0858.json
python3 PROOFCORE/verifiers/verify_streamfold_payload_receipt_inprocess_rev0859.py --receipt PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.minimum.rev0858.json
python3 PROOFCORE/verifiers/verify_streamfold_payload_receipt_inprocess_rev0859.py --receipt PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.reject_tampered_count.rev0858.json --expect-fail
```

The old endpoint remains carried as a historical hash-bound artifact, but it is liveness-quarantined and should not be used as the active proofcore command in this cloudtainer.

## Audit/refactor

The rev0859 audit scanned proofcore verifiers and scripts for subprocess surfaces. It found 24 Python files with `subprocess.run`, of which 19 use stdout pipes and 7 contain timeout guards. The immediate high-risk case is the rev0858 payload-receipt replay because it is inside the active PCD chain and is avoidable by in-process recomputation.


A second validation liveness cleanup was made after the audit: `scripts/validate_sumcheck_fs_lane_rev0856.py` now recognizes rev0856 as a historical checkpoint in rev0857+ bundles and exits through the carried-parent replay contract instead of rerunning the stale exact rev0856 lane subprocess surface.

## Still blocked

The 17 canonical streamfold payloads remain absent from this overlay. No root license, notice, SPDX conclusion, RO-Crate rights assertion, recovered payload bytes, SNARK proof, zero-knowledge proof, succinct proof, or streamfold correctness claim was added.
