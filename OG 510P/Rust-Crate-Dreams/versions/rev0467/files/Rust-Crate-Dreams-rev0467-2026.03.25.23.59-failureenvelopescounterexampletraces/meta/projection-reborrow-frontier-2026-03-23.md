# Projection / reborrow / pinning frontier — 2026-03-23

This note sharpens why **P-0440 Projection & Reborrow Semantics Kit** deserves a serious product pass now.

## Main judgment

Rust’s smart-pointer ergonomics frontier is now active in both language design and crate practice.
The 2026 flagships explicitly call out **field projections**, **reborrow traits**, and **in-place initialization**.
At the same time, the ecosystem already has real substrate in `pin-project`, `pin-init`, `moveit`, and generalized reborrow crates.

That means the missing crate is no longer “some way to experiment with pinning.”
The missing crate is a **reviewable semantics-support layer** above those experiments.

## Why this lane matters now

1. **Official momentum**
   - field projections, reborrow traits, and pinned/in-place construction are all active Rust goals.
2. **Real ecosystem substrate**
   - projection macros, pinned-init libraries, generalized reborrow crates, and address-sensitive construction tools already exist.
3. **Safety pressure**
   - Miri exists precisely because advanced unsafe abstractions still need witness discipline.
4. **Evidence that abstractions can still be wrong**
   - research like PinChecker strengthens the case for reusable witness and review artifacts.

## Sharper frontier claim after this pass

The next implementation work for **P-0440** should treat these as first-class review objects:

- `projection-authority.receipt.json`
- `borrow-semantics.matrix.json`
- `semantics-witness.report.json`
- `projection-support-bundle.manifest.json`

Those objects matter because the lane should answer four boring but high-value questions:

1. **authority** — which surface is authoritative for the support claim;
2. **mode coverage** — which borrow/projection modes are supported or caveated;
3. **witness basis** — what was seen under ordinary tests, Miri, imported evidence, or manual review;
4. **bundle portability** — what another maintainer can inspect without recreating the unsafe argument from scratch.

## Boundary reminder

P-0440 should not absorb:

- **P-0447** in-place initialization adoption,
- **P-0460** unsafe field invariant authority,
- **P-0120** broad unsafe-contract auditing,
- or **P-0121** full FFI boundary support.

Its job is the semantics-support layer for **projection / reborrow / pinning surfaces**, not the total unsafe universe.
