# In-place initialization frontier — 2026-03-22

The archive already had ideas around pinning, field projections, and unsafe fields. This pass clarifies where the **in-place initialization** lane begins and ends.

## Current stack

1. **P-0447 In-Place Initialization Adoption Kit**
   - Owns the reviewable contract layer for:
     - placement topology,
     - constructor-lane comparison,
     - address commit,
     - failure cleanup,
     - and transition drift.
2. **P-0440 Projection & Reborrow Semantics Kit**
   - Owns projection/reborrow/aliasing witness fixtures.
   - Use this when the hard problem is projection semantics more than construction topology.
3. **P-0460 Unsafe Field Invariant Ledger Kit**
   - Owns field-carried invariant authority, trusted constructors, mutation lanes, and witness scope.
   - Use this when the hard problem is post-construction invariant maintenance rather than how a value first comes into existence.
4. **P-0121 FFI Boundary & Bindings Conformance Kit**
   - Owns ownership/layout/error/unwind/callback truth across language boundaries.
   - Use this when the hard problem is the boundary contract, not the internal construction lane.

## Shared judgment after this pass

The strongest missing crate in this sub-frontier is not another macro and not another language-proposal explainer.
It is a **placement-and-constructor evidence layer** that lets maintainers, reviewers, adopters, and upstream language designers inspect what an initialization strategy really means in practice.

## Design guardrails

When working in this frontier, keep these truths separate:

1. **placement truth** — where bytes are first written and where the final allocation lives;
2. **constructor-lane truth** — by-value Rust, pinned-init, out-pointer, `moveit`, Crubit `Ctor`, or provisional future-language lane;
3. **address-commit truth** — when the final address becomes authoritative and moves become forbidden;
4. **failure-cleanup truth** — what initialization can fail, what gets destroyed, and who owns rollback;
5. **transition truth** — what changed when a crate switched strategies or adapters.

Do not let any of the following stand in for an honest answer:

- “we use `pin-init`,”
- “the type returns `Pin<Box<T>>`,”
- “the constructor is fallible,”
- “this is for C++ interop,”
- or “future language support will handle this.”

Those are useful signals, not a full in-place-initialization contract.
