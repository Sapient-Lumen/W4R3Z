# Storage-lane quarantine clearance lane-wide scope slice — rev0085

Current release-light task:

```text
scheduler:storage-lane-quarantine-clearance-lanewide-scope-proof
```

This slice hardens the timeout-quarantine clearance receipt boundary: `allowLaneWide: true` now means lane-wide within a concrete lane, not lane-ambiguous or cross-lane. A self-consistent clearance receipt with `allowLaneWide: true` and no `lane` is rejected before it can register as a stale-quarantine replay suppressor.

The release proof checks that:

```text
valid lane-wide receipt with lane=storage still validates
lane-ambiguous lane-wide receipt fails validation
lane-ambiguous direct registration fails closed
rejected registration does not suppress stale quarantine import/backpressure
valid lane-scoped receipt still rejects stale replay
later storage-lane write verifies after the valid path
```

Non-claims: this is browser-light synthetic storage evidence, not provider cancellation, rollback, no-mutation-on-timeout, OPFS durability, quota/eviction survival, cryptographic attestation, or production readiness.
