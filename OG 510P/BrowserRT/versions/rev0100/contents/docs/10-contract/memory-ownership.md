# Memory ownership contract

BrowserRT treats memory ownership as part of the runtime contract.

## Ownership modes

- `owned`: one context owns the bytes.
- `transferred`: ownership moved; the sender must not touch the detached buffer.
- `shared`: multiple contexts may view the bytes; synchronization is required.
- `borrowed-read`: temporary read-only view.
- `borrowed-write`: temporary exclusive write view.
- `gpu-resident`: data is on the GPU; readback is explicit.
- `persistent`: data lives in storage and is referenced by block id/path.

## Lease rules

A memory lease must record:

- owner or shared slab id;
- byte range;
- read/write mode;
- trace id;
- release state;
- optional deadline.

Leases must be released exactly once. A future leak detector should fail tests
when a lease survives runtime shutdown.

## Transfer rules

Transferable buffers are the baseline hot path. SharedArrayBuffer is an advanced
capability tier, not a requirement.

## Shared-memory rules

Shared memory requires explicit synchronization and must never be used as a
silent global bag of state. Ring buffers, mailboxes, and progress counters are
allowed. Ambient mutable shared objects are not.
