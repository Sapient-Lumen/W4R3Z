# Storage-lane timeout-quarantine clearance receipt lane-binding slice

Revision: rev0084  
Release proof: `scheduler:storage-lane-quarantine-clearance-receipt-lane-binding-proof`

This lane binding slice closes a direct maintenance footgun in timeout-quarantine clearance receipts. A valid `clearanceReceipt.v1` is bound to the lane and operation rows it cleared. Direct registration must not be able to re-bind that receipt to a different lane, and a self-consistent receipt whose declared lane disagrees with its cleared row lanes must fail receipt validation.

The proof creates mixed late-success and late-failure timeout quarantine, clears it with a reviewed/fingerprint-bound manifest, and then checks the direct registration boundary:

```text
valid receipt for storage lane + register with maintenance lane
  -> timed-out-quarantine-clearance-receipt-lane-mismatch
  -> rejected-clearance-receipt-lane-binding

receipt lane maintenance + cleared row lane storage
  -> rejected-clearance-receipt-integrity

rejected wrong-lane registration
  -> does not suppress stale quarantine ledger import
  -> non-empty import still forces storage-lane backpressure

valid lane-bound registration
  -> stale replay rejects
  -> later write verifies after lane remains healthy
```

Non-claims: this is browser-light synthetic-provider evidence only. It is not provider cancellation, rollback, no-mutation-on-timeout, OPFS durability, quota/eviction survival, cross-browser behavior, cryptographic attestation, tamper-proof storage, throughput, latency, SLO, or production readiness evidence.
