# Epic proposal: Lending Surface Kit

## Thesis
One of the strongest missing ecosystem contributions in Rust is a **portable contract for borrow-friendly sequence surfaces**.

Rust has long had excellent owned-item iteration. What it still lacks is a reviewable, attachable way to describe and validate the next wave of APIs that yield borrows, mutate through borrows, return futures that borrow, or bridge between sync and async sequence forms.

In other words: Rust needs a boring, explicit `lending-pack/v0` more than it needs one more clever iterator crate or one more runtime-specific stream facade.

## Why now
The timing is unusually good:
- the 2025 async goal work said the next generation of async libraries was blocked on stable async traits and streams;
- RFC 3654 exists because the Send-bound problem and related opaque-return bounds are blocking interoperable async trait usage;
- the 2025H2 Polonius goal explicitly targets accepting lending iterators;
- the 2026 flagships elevate lending iterators as part of “unblocking dormant traits”;
- the reborrow-traits goal says user-space types still cannot achieve true reborrowing today;
- and stable-Rust crates like `streaming-iterator`, `lending-iterator`, and `lender` already prove that the demand is real.

That means the next major Rust ecosystem seam is visible before it has fully converged.
This is exactly when a reviewable contract is most valuable. The archive should now treat this as a **ranked pilot program**, not a wait-for-stability footnote.

Sources:
- https://rust-lang.github.io/rust-project-goals/2025h1/index.html
- https://rust-lang.github.io/rfcs/3654-return-type-notation.html
- https://rust-lang.github.io/rust-project-goals/2025h2/polonius.html
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h2/autoreborrow-traits.html
- https://docs.rs/streaming-iterator
- https://docs.rs/lending-iterator/latest/lending_iterator/
- https://docs.rs/lender

## What should be built
A first credible version should ship:
1. `lending-surface/v0`, `borrow-mode-profile/v0`, `sequence-adapter-profile/v0`, `yield-vector-set/v0`, optional `executor-runtime-profile/v0`, `sequence-check-report/v0`, `lending-pack/v0`, and pilot-scoping artifacts described in [`design/lending-surface-pilot-program.md`](../design/lending-surface-pilot-program.md)
2. one sync-lending pilot across `streaming-iterator` / `lending-iterator` / `lender`
3. one async-sequence bridge pilot across `futures-core::Stream`, `tokio-stream`, and nightly `AsyncIterator` notes
4. one borrowing-callback / async-closure pilot, clearly labeled experimental
5. one pin/runtime-sensitive adapter pilot so local-only, wake-sensitive, or pin-heavy assumptions become reviewable instead of hidden
6. docs and CI that make invalidation, cancellation, runtime dependence, and adapter lossiness explicit

The winning version is small, semantic, and adapter-heavy.
It should make today’s awkward surfaces legible together rather than prematurely canonizing one of them.

## Ranked pilot order
- **Sync lending first** — start with `streaming-iterator` / `lending-iterator` / `lender` and make invalidation / mutable-borrow / adapter-cost truth boring and explicit
- **Async bridge second** — compare `Stream`, experimental `AsyncIterator`, and runtime adapters with explicit cancellation / `Send` / local-executor truth
- **Borrowing callback third** — use async-closure / RTN-sensitive examples to show where returned futures borrow and what bounds are actually required
- **Pin/runtime lane fourth** — isolate local-only, pin-sensitive, or wake-sensitive adapters instead of letting them hide in footnotes
- **Domain lane fifth** — borrowed line/chunk iteration, protocol/frame decoding, parser/windowing, or similar lanes where borrow reuse materially changes the API story

## Milestones
1. **v0 artifacts + reference semantics**
   - publish schemas and minimal examples
   - document borrow modes, invalidation rules, and adapter cost vocabulary
2. **v0.2 adapters + vectors**
   - ship sync-lending pilot
   - run vectors over exhaustion, invalidation, fusedness, and adapter lossiness
3. **v0.3 async/runtime depth**
   - add runtime/executor profiles where needed
   - capture cancellation, wake, and `Send` assumptions explicitly
4. **v0.4 pilot widening**
   - use the ranked pilot order to decide whether async bridge, borrowing callback, or pin/runtime lanes are ready to widen
5. **v1 ecosystem pilots**
   - at least three materially different adopters use the artifact family without sharing one exact runtime/framework stack

## Success metrics
- Library authors can review borrowing sequence APIs without reconstructing semantics from examples and folklore.
- Adapter costs between owned, lending, and async surfaces become visible before integration work starts.
- Future language features land into a prepared ecosystem with explicit migration notes.
- Atlas-style guidance can recommend sequence stacks with actual semantic evidence attached.
- Rust avoids fragmenting this emerging seam into a dozen incompatible “better stream” universes.

## Archive fit
This proposal fills a real gap in the archive:
- **Interop Commons Kit** says how neutral shared seams are created;
- **Async Lifecycle Kit** says how tasks/services live and shut down;
- **Replay / Debugger / Observability** proposals explain how systems are inspected;
- and domain kits like Protocol, Dataset, Media, and Service explain higher-level contracts.

But none of those is the portable contract for **borrow-aware item production and sequence adaptation**.
Lending Surface Kit is the missing substrate for a part of Rust that the language roadmap is actively trying to unlock.
