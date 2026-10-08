# streamfold_sumcheck_toy_v2 — rev0859 receipt liveness lane

rev0859 keeps the rev0858 framed transcript and payload absence receipts intact, but replaces the active receipt replay endpoint with an in-process verifier.

The risk fixed here is operational: the legacy rev0858 payload-receipt verifier recomputes the rev0857 source report through a subprocess with captured stdout/stderr pipes. In this cloudtainer it can print the success marker and still not return. The active rev0859 verifier imports the rev0857 candidate verifier from the selected root and recomputes the source report directly.

Active checks:

```bash
python3 PROOFCORE/verifiers/verify_streamfold_payload_receipt_inprocess_rev0859.py --receipt PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.full.rev0858.json
python3 PROOFCORE/verifiers/verify_streamfold_payload_receipt_inprocess_rev0859.py --receipt PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.minimum.rev0858.json
python3 PROOFCORE/verifiers/verify_streamfold_payload_receipt_inprocess_rev0859.py --receipt PROOFCORE/lanes/streamfold_sumcheck_toy_v2/rev0858/payload_absence_receipt.reject_tampered_count.rev0858.json --expect-fail
python3 scripts/validate_payload_receipt_liveness_rev0859.py
```

Non-claims: this is not a rights grant, not a recovered payload bundle, not a streamfold correctness proof, not a SNARK, not zero knowledge, and not succinct.
