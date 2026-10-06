# Browser OPFS Web Lock quarantine clearance restore registration gate slice

Revision: rev0086  
Task: `browser:opfs-web-lock-quarantine-clearance-restore-registration-gate-proof`

## Purpose

This Managed Chromium proof checks the real OPFS/Web Locks handoff boundary for clearance receipt restore. The risk is that a persisted clearance receipt can survive profile restart, but restore must fail closed if the receipt cannot be registered for the lane being restored.

## Browser flow

Phase 1 uses real guarded OPFS:

- create a synthetic storage-lane timeout-quarantine ledger;
- import and reviewed/scoped-clear it;
- create a lane-scoped clearance receipt;
- persist the receipt as an OPFS content-addressed block;
- close Chromium while keeping the browser profile.

Phase 2 relaunches the same profile and origin:

- verify the persisted receipt block is still present;
- try to restore the storage receipt into the maintenance lane;
- verify restore rejects as `rejected-clearance-receipt-lane-binding` and does not install replay guard state;
- import the stale ledger and observe forced storage-lane backpressure;
- restore the receipt into the storage lane with `block-store-restore-clearance-receipt` provenance;
- verify stale replay is rejected and a later guarded OPFS write verifies;
- cleanup and confirm final Web Lock state drains to zero.

## Earned claim

In managed Chromium, BrowserRT can persist a timeout-quarantine clearance receipt through the guarded OPFS block-store path, carry it across a clean browser/profile restart, and reject wrong-lane restore before stale replay guard state is installed.

## Non-claims

This does not claim cross-browser behavior, OPFS fsync durability, power-loss safety, crash safety, quota or eviction survival, automatic recovery, no-mutation-on-timeout, exactly-once semantics, cryptographic attestation, tamper-proof storage, latency SLOs, or production readiness.


## rev0086 audit anchor

This restore registration gate slice records wrong-lane restore behavior: registration rejects before replay guard state installs, the valid restore path is lane-bound, and the Managed Chromium side proves the OPFS/Web Locks handoff. This is not cryptographic attestation and not production readiness.
