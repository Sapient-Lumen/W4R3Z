# streamfold_sumcheck_toy_v2 rev0858

rev0858 hardens the active transparent PCD lane in two places:

1. Payload-admission outputs are now carried as portable absence receipts and verified by `verify_streamfold_payload_receipt_rev0858.py`.
2. The toy sumcheck transcript now uses a fixed, labeled operation log: absorb public context, absorb claim, absorb payload receipts, absorb each round polynomial, derive a labeled challenge, and absorb the final evaluation.

Accepted derived challenges for the tiny fixture over Fp97:

```text
r1 = 94
r2 = 68
final evaluation = 6
```

This remains a transparent harness. It is not a SNARK, not zero knowledge, not succinct, not a production Fiat-Shamir transform, not a recovered payload bundle, and not a rights grant.

Canonical streamfold payload bytes remain absent from this overlay. Candidate roots must still satisfy the rev0857 exact path/byte/SHA-256 gate before payloads can be admitted.
