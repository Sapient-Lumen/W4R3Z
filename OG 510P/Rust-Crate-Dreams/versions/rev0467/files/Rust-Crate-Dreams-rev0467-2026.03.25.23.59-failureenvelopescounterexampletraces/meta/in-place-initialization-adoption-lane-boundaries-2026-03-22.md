# In-Place Initialization Adoption lane boundaries — 2026-03-22

This note keeps **P-0447 In-Place Initialization Adoption Kit** from collapsing into neighboring lanes.

## What belongs in P-0447

P-0447 owns:
- placement-topology receipts,
- constructor-lane reports,
- address-commit receipts,
- failure-cleanup reports,
- and portable init support bundles.

## What does not belong here

### Not the same as `pin-init`, `moveit`, or Crubit `Ctor`
Those crates perform or model initialization.
P-0447 exists to publish **reviewable support artifacts above them**.

### Not the same as P-0440 Projection & Reborrow Semantics Kit
P-0440 focuses on projection/reborrow/aliasing witness truth.
P-0447 focuses on the earlier question of how a value first gets constructed in a stable place.

### Not the same as P-0460 Unsafe Field Invariant Ledger Kit
P-0460 tracks field-level invariant authority and post-construction mutation lanes.
P-0447 focuses on initial placement, address commit, and cleanup posture.

### Not the same as P-0121 FFI Boundary & Bindings Conformance Kit
P-0121 owns language-boundary ownership/layout/error/unwind/callback truth.
P-0447 may feed evidence into that lane, but it does not replace the wider FFI contract.

## Guardrails

Do not let any of the following stand in for an honest in-place-initialization contract:
- “the API returns a pinned pointer,”
- “the crate uses `MaybeUninit`,”
- “the value is built on the heap,”
- “the constructor is fallible,”
- or “this mirrors C++ constructors.”

A crate can have all of those truths and still leave placement topology, address commit, cleanup behavior, or strategy drift unresolved.
