# rev0091 browser OPFS/Web Lock quarantine receipt restore integrity slice

Current browser task: `browser:opfs-web-lock-quarantine-receipt-restore-integrity-proof`.

The Managed Chromium proof persists a timeout-quarantine clearance receipt through the real guarded OPFS block-store path, deliberately corrupts the final content-addressed OPFS block, verifies unverified restore opt-out rejection, and verifies that corrupt-block restore rejects before registering replay-guard state. After repairing the same content-addressed receipt block through `WebLockGuardedBlockStore.put()`, restore succeeds, stale quarantine replay is rejected, a later guarded OPFS write verifies, and final Web Lock state drains to zero.

Evidence markers:

- `block-store-lane:quarantine-clearance-receipt-restore-unverified-rejected`;
- `storage:opfs-block-corrupt`;
- `block-store-lane:quarantine-clearance-receipt-restore-block-integrity-rejected`;
- `storage:opfs-block-repair`;
- `block-store-lane:quarantine-clearance-receipt-restored`;
- `rejected-clearance-receipt-block-integrity`;
- `rejected-cleared-quarantine-replay`.

Non-claims: Managed Chromium/CDP only; no cross-browser OPFS/Web Locks behavior, organic corruption, power-loss proof, quota/eviction survival, cryptographic attestation, tamper-proof storage, durability, SLO, or production readiness claim.


This rev0091 slice explicitly treats persisted quarantine ledger and clearance receipt **block integrity** as a restore gate before any maintenance state is imported or registered.
