# Projection & Reborrow Semantics lane boundaries — 2026-03-23

This note keeps **P-0440 Projection & Reborrow Semantics Kit** from collapsing into neighboring lanes.

## What belongs in P-0440

P-0440 owns:
- projection-authority receipts,
- borrow-semantics matrices,
- semantics-witness reports,
- projection-drift diffs,
- and portable projection support bundles.

## What does not belong here

### Not the same as `pin-project`, `pin-init`, `moveit`, or generalized-reborrow crates
Those crates implement projection, initialization, or reference ergonomics.
P-0440 exists to publish **reviewable support artifacts above them**.

### Not the same as P-0447 In-Place Initialization Adoption Kit
P-0447 focuses on where a value first comes into existence, address commit, and cleanup posture.
P-0440 focuses on what happens **after or around that construction** when the API projects or reborrows views.

### Not the same as P-0460 Unsafe Field Invariant Ledger Kit
P-0460 tracks field-level invariant authority and mutation lanes.
P-0440 focuses on projection/reborrow support claims and witness truth.

### Not the same as P-0120 Unsafe Contract Auditor Kit
P-0120 owns the broader unsafe obligation inventory and authority drift story.
P-0440 is a narrower semantics witness lane for advanced pointer-like APIs.

### Not the same as P-0121 FFI Boundary & Bindings Conformance Kit
P-0121 owns ownership, layout, callback, unwind, and cross-language support truth.
P-0440 may feed evidence into that lane, but it does not replace the full boundary contract.

## Guardrails

Do not let any of the following stand in for an honest projection/reborrow contract:
- “the crate uses `#[pin_project]`,"
- “the API returns `Pin<&mut T>`,"
- “Miri passed once,"
- “the wrapper type has a reborrow trait,"
- or “future language support will make this obsolete.”

A crate can have all of those truths and still leave authority, borrow-mode coverage, witness basis, or uncovered paths unresolved.
