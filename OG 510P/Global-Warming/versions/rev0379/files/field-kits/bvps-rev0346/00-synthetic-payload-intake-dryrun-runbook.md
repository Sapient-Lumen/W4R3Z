# Rev0346 synthetic payload intake dry run

This field kit documents the synthetic payload files seeded into 24 of the 60 event-day packet skeletons.

The files are intentionally marked `SYNTHETIC DRY RUN PAYLOAD ONLY`. They test filesystem scanning, SHA-256 hashing, redacted-surrogate pairing, custody-form presence, QA-note presence, SQLite views, and claim-firebreak behavior.

Do not use these files as real Beaver Valley evidence. Do not use them to assert readiness, sufficiency, certification, green status, passed status, or closure.

## Operator sequence

1. Run `tools/scan_nuclear_emergency_bvps_synthetic_payloads_rev0346.py`.
2. Confirm 24 seeded packets and 96 payload files.
3. Confirm 36 packets remain missing payloads.
4. Confirm 0 packets are ready to claim.
5. Replace synthetic payloads only with real/anonymized evidence packets that preserve raw, redacted, custody, and QA files.
6. Keep loss caps active until adjudication, CAP/retest/verifier, and claim-kernel gates pass.
