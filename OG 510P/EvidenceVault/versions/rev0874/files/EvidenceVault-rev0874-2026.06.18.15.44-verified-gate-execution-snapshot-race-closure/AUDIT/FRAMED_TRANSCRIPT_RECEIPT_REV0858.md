# Framed transcript and payload receipt audit — rev0858

Status: `framed_transcript_receipts_active_payloads_still_missing`

rev0858 focuses on the active proofcore risk rather than adding another registry surface. The streamfold payloads are still absent, so the work is to make that absence/admission boundary more executable and less ambiguous.

## Payload receipt

The rev0857 candidate-root verifier can now be recomputed through rev0858 payload receipts:

```bash
python3 PROOFCORE/verifiers/verify_streamfold_payload_receipt_rev0858.py --receipt PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.full.rev0858.json
python3 PROOFCORE/verifiers/verify_streamfold_payload_receipt_rev0858.py --receipt PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.minimum.rev0858.json
```

The receipts record the deterministic absence result for the current overlay. They do not copy payload bytes, admit candidate bytes, grant rights, or prove streamfold correctness.

## Framed transcript

rev0857 bound challenges to previous public message hashes. rev0858 makes the transcript shape explicit as a fixed operation log: labeled absorbs and labeled challenges. The accepted toy fixture has `9` operations over `Fp97`:

```text
r1 = 94
r2 = 68
final evaluation = 6
```

Reject controls now cover reordered absorb operations and challenge-label swaps. This is still not a SNARK, not zero knowledge, not succinct, and not a production Fiat-Shamir transform.

## Candidate-root symlink audit/refactor

A concrete bug-risk was corrected: `resolve_candidate_root` previously resolved the operator-supplied path before checking whether it was a symlink. rev0858 checks the raw candidate path first, then resolves it. The validator exercises four negative controls: missing expected payload, hash/size mismatch, candidate payload symlink, and candidate-root symlink.

## Remaining blocker

All 17 canonical `streamfold_sumcheck_toy_v2_family` payload bytes are still absent from this overlay. Publication remains blocked pending rights decisions.
