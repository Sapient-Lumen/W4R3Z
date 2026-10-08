# Unsafe Field Invariant Ledger lane boundaries — 2026-03-22

This note keeps **P-0460 Unsafe Field Invariant Ledger Kit** from collapsing into neighboring lanes.

## What belongs in P-0460

P-0460 owns:
- field-level invariant authority,
- mutation-lane tracking,
- trusted-constructor receipts,
- field-scoped witness reports,
- and portable unsafe-field review bundles.

## What does not belong here

### Not the same as P-0120 Unsafe Contract Auditor Kit
P-0120 maps broader unsafe obligations and witness boundaries.
P-0460 is narrower: it focuses on invariants carried by fields and on the mutator/constructor authority around those fields.

### Not the same as P-0121 FFI Boundary & Bindings Conformance Kit
If the main hard problem is ownership, layout, unwind posture, callbacks, or error propagation across languages, that belongs primarily in P-0121.
P-0460 may note that an invariant-bearing field is influenced by FFI, but it does not replace cross-language boundary contracts.

### Not the same as P-0485 Verification Campaign Workbench Kit
P-0485 compares many evidence lanes and policy-evaluates whole campaigns.
P-0460 is narrower: it defines the field contract that witnesses may later attach to.

### Not the same as a privacy/visibility pattern
Module privacy, getters/setters, and sealed APIs can help constrain mutation.
P-0460 exists to publish **reviewable field-contract artifacts**, not only access-control patterns.

## Guardrails

Do not let any of the following stand in for an honest unsafe-field contract:
- “the field is private,”
- “the crate documents safety invariants,”
- “Miri passed,”
- “the constructor validates inputs,”
- or “future unsafe fields will make this obvious.”

A crate can have all of those truths and still leave field authority, safe mutator scope, constructor trust, or witness coverage unresolved.
