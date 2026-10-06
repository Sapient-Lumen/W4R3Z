# Storage-lane quarantine restore expected fingerprint contract audit slice

Task: `facility:storage-lane-quarantine-restore-expected-fingerprint-contract-audit`

This browser-light audit keeps the expected-fingerprint restore gate wired across runtime code, TypeScript surface notes, release-light proof, managed Chromium proof, validation docs, manifest, impact map, surface inventory, package scripts, Makefile, changelog, and first-read docs.

The audit checks for `expectedQuarantineFingerprint`, `expectedReceiptFingerprint`, `expectedPreClearanceFingerprint`, `rejected-quarantine-ledger-expected-fingerprint`, and `rejected-clearance-receipt-expected-fingerprint` so the restore path cannot silently drift back to accepting any block-valid quarantine ledger or clearance receipt.

This audit is not runtime evidence by itself. It does not claim cryptographic attestation, tamper-proof storage, provider cancellation, durability, quota/eviction behavior, or production readiness.

The browser proof is explicitly wired through the current manifest.


rev0093 update: blank expected-fingerprint restore intent now fails closed before decode/import/registration; whitespace is not treated as an omitted pin. The release and Managed Chromium proofs share assertion coverage through `tools/lib/quarantine_restore_expected_fingerprint_harness.mjs`. This is still operator intent checking, not cryptographic attestation or tamper-proof storage.
