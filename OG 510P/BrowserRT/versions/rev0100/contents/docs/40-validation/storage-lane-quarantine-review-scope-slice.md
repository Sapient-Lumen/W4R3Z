# Storage-lane quarantine review scope slice — rev0078

Current release-light task:

```text
scheduler:storage-lane-quarantine-review-scope-proof
```

This slice proves the browser-light side of the timeout-quarantine review-scope boundary. It uses synthetic provider work to create mixed late-success and late-failure rows after `BRT_STORAGE_OPERATION_TIMEOUT`, exports/imports the `brt.storageLane.timedOutOperationQuarantine.v1` ledger, and verifies that a review manifest is authoritative for clearing scope.

Important checks:

```text
quarantineFingerprint / reviewFingerprint remain bound to the current quarantine set
missing reviewFingerprint is rejected
stale reviewFingerprint is rejected
timed-out-quarantine-clear-review-manifest-scope-override is rejected
timed-out-quarantine-clear-review-manifest-count-mismatch is rejected
clearTimedOutOperationQuarantine() only recovers after a scope-bound review manifest clears the current rows
```

This fixes a risky maintenance boundary: a reviewer should not approve one scoped quarantine review and then have a caller merge in different `opIds`, categories, or lane-wide intent during clear. The manifest itself supplies the clearing scope.

Non-claims: this is not browser OPFS/Web Locks evidence, not cryptographic attestation, not tamper-proof storage, not cancellation, not provider cancellation, not rollback, not no-mutation-on-timeout, and not production readiness.

Audit phrases: review manifest, scope override, review fingerprint, provider cancellation non-claim.
