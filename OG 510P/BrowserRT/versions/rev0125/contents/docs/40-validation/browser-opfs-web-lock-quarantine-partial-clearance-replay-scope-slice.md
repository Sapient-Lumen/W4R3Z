# Browser OPFS/Web Lock timeout-quarantine partial clearance replay scope slice

Revision: rev0087  
Task: `browser:opfs-web-lock-quarantine-partial-clearance-replay-scope-proof`

This managed Chromium proof runs the partial clearance replay-scope policy over a real `WebLockGuardedBlockStore` backed by OPFS.

## What it proves

The proof creates a synthetic mixed timeout-quarantine ledger, clears only the successful row, registers the partial clearance receipt, and verifies that exact replay of the original full ledger is rejected by row-level replay coverage rather than full-fingerprint replay suppression. It then imports the uncleared failed row alone and observes forced storage-lane backpressure. It also verifies that a forged/self-consistent full-count receipt with wrong rows does not suppress stale-ledger import, while a genuine full-clearance receipt still rejects exact stale replay.

A later guarded OPFS write verifies and Web Lock state drains to zero.

## Non-claims

This is managed Chromium/CDP evidence only. It does not claim cross-browser OPFS/Web Locks behavior, cryptographic attestation, tamper-proof storage, provider cancellation, rollback, no-mutation-on-timeout, exactly-once semantics, OPFS durability, fsync behavior, quota/eviction survival, throughput, latency SLOs, or production readiness.

Phrase anchor: Managed Chromium.

Phrase anchor: row coverage.

Uncleared row anchor: partial clearance leaves the uncleared row eligible to import/backpressure rather than being hidden by full-fingerprint replay suppression.
