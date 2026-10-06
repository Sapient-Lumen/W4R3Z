# Storage-lane quarantine lane-filter import guard slice

Current rev0084 release-light proof: `scheduler:storage-lane-quarantine-lane-filter-import-guard-proof`.

This slice protects the timeout-quarantine import boundary when a caller supplies a lane filter. A non-empty ledger whose rows do not match the requested lane must fail closed as `rejected-lane-filter-empty-import`; a mixed-lane ledger must fail closed as `rejected-lane-filter-partial-import` unless the caller explicitly sets `allowPartialImport: true`.

When partial import is explicit, the imported quarantine still forces storage-lane backpressure and a later write rejects as `rejected-lane-unhealthy` with `noMutation: true` until reviewed/scoped clearing and explicit recovery occur.

Non-claims: no provider cancellation, rollback, no-mutation-on-timeout, cryptographic attestation, tamper-proof storage, OPFS durability, quota/eviction survival, cross-browser behavior, SLO, or production-readiness claim.

Audit keywords: lane-filtered import; wrong-lane restore; partial import; allowPartialImport.
