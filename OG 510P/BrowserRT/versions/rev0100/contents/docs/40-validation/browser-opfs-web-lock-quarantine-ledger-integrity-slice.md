# Browser OPFS/Web Lock quarantine ledger integrity slice — rev0074

Current task: `browser:opfs-web-lock-quarantine-ledger-integrity-proof`  
Current audit: `facility:storage-lane-quarantine-ledger-integrity-contract-audit`

This managed Chromium proof exercises the same import-integrity boundary through the real BrowserRT OPFS/Web Lock guarded block-store path. The proof first creates real timed-out guarded OPFS operations, lets them settle into late-success and late-failure quarantine buckets, exports a `brt.storageLane.timedOutOperationQuarantine.v1` ledger, then attempts malformed ledger imports before the valid import.

Malformed imports must **fail closed** and remain **atomic**. The checked malformed cases include missing counts, `counts.total mismatch`, missing bucket arrays, duplicate opId rows, missing opId rows, and unsupported schema. Each rejection is classified as `timed-out-quarantine-import-rejected` / `rejected-ledger-integrity`; no partial quarantine rows are installed and the lane is not made unhealthy by the rejected import.

The valid ledger then imports, backpressures the storage lane, requires reviewed/scoped clearance, and proves recovery with a later guarded OPFS write.

Non-claims: Managed Chromium only. This does not prove cross-browser OPFS/Web Locks behavior, cryptographic ledger integrity, production audit attestation, provider cancellation, rollback, no-mutation-on-timeout, fsync durability, crash or power-loss safety, quota survival, eviction survival, persistent-storage retention, throughput, latency SLOs, or production readiness.

Exact guardrail phrase: not cryptographic, not production.
