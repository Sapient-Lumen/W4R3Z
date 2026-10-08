# Unsafe-field invariant frontier — 2026-03-22

The archive now has enough unsafe/safety proposals that future passes should stop treating them as one blurry “unsafe review” bucket.

## Current stack

1. **P-0460 Unsafe Field Invariant Ledger Kit**
   - Owns the shared contract layer for:
     - field authority
     - mutation lanes
     - trusted constructors
     - field-scoped witness coverage
     - field-contract drift
2. **P-0120 Unsafe Contract Auditor Kit**
   - Owns broader unsafe-obligation inventory, authority imports, interpreter-boundary honesty, and witness fidelity.
   - Use this when the hard problem is the overall unsafe-obligation map, not specifically field-carried invariants.
3. **P-0121 FFI Boundary & Bindings Conformance Kit**
   - Owns ownership/layout/unwind/error/callback truth across language boundaries.
   - Use this when the hard problem is interop, not local field authority.
4. **P-0485 Verification Campaign Workbench Kit**
   - Owns campaign-wide comparison, policy evaluation, and multi-lane evidence composition.
   - Use this when the hard problem is comparing many witnesses, not defining a field contract.
5. **P-0465 BorrowSanitizer Workflow & Evidence Kit**
   - Owns a specific witness/workflow lane for aliasing-oriented dynamic evidence.
   - Use this when the hard problem is running or comparing a specific witness technology.

## Shared judgment after this pass

The strongest missing crate in this sub-frontier is not another checker and not another proof-shaped promise.
It is a **contract layer** that lets maintainers, reviewers, adopters, and auditors inspect what field invariants mean in practice.

## Design guardrails

When working in this frontier, keep these truths separate:

1. **authority truth** — where the invariant claim came from;
2. **mutation truth** — which paths can change the field;
3. **constructor truth** — which paths are trusted to establish the invariant;
4. **witness truth** — what evidence touched the field contract;
5. **drift truth** — how the field contract changed across revisions.

Do not let any of the following stand in for an honest unsafe-field answer:

- “unsafe blocks are reviewed”
- “safety docs exist”
- “Miri passed”
- “the field is private”
- “the constructor validates inputs”

Those are useful signals, not a full field-invariant contract.
