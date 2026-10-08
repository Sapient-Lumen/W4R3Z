# Design: Lending Surface Kit (`cargo lending`, `lending-pack/v0`)

## Goal
Define a portable contract for specifying, validating, diffing, and reviewing **borrow-friendly sequence surfaces** in Rust: owned iterators, streaming/lending iterators, async streams, nightly `AsyncIterator`-style surfaces, generator-backed producers, and related adapters.

This should help answer questions like:
- does this API yield owned items, borrowed items, mutable borrowed items, or futures that borrow,
- when do yielded values become invalid,
- which adapters preserve semantics and which allocate/clone/box/buffer/erase borrows,
- what runtime, pinning, cancellation, and `Send` assumptions exist,
- and what evidence shows two sequence surfaces are actually compatible.

It should **not** replace `Iterator`, the `futures` crate, Tokio, parser libraries, or every cursor abstraction.
It should make the semantics of those surfaces reviewable and comparable.

The next credible execution move is now a ranked pilot program in [`design/lending-surface-pilot-program.md`](./lending-surface-pilot-program.md): sync lending first, then async bridges, then borrow-callback / async-closure lanes, then pin/runtime-sensitive adapters, then domain pilots.

## References (signals)
- Rust’s 2025 async goals say the next generation of async libraries has been blocked on stable solutions for async traits and streams.
  https://rust-lang.github.io/rust-project-goals/2025h1/index.html
  https://blog.rust-lang.org/2025/04/08/Project-Goals-2025-March-Update/
- The 2025H2 Polonius goal explicitly targets accepting lending iterators, and the 2026 flagships call out lending iterators as part of “unblocking dormant traits”.
  https://rust-lang.github.io/rust-project-goals/2025h2/polonius.html
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Return type notation exists because Rust needs a way to express bounds on returned opaque values, including the Send-bound problem for async functions in traits.
  https://rust-lang.github.io/rfcs/3654-return-type-notation.html
- Async closures are explicitly about allowing async callables to return futures that borrow from captures.
  https://rust-lang.github.io/rfcs/3668-async-closures.html
- RFC 2996 positions async iterators as a core async abstraction and states the intent to add today’s `Stream` concept to the standard library as `AsyncIterator`.
  https://rust-lang.github.io/rfcs/2996-async-iterator.html
- `streaming-iterator`, `lending-iterator`, and `lender` are proof that the ecosystem already needs borrow-friendly sequence APIs on stable Rust.
  https://docs.rs/streaming-iterator
  https://docs.rs/lending-iterator/latest/lending_iterator/
  https://docs.rs/lender
- `futures-core::Stream`, `tokio-stream`, and nightly `std::async_iter::AsyncIterator` show the current split between de facto, runtime-specific, and emerging std surfaces.
  https://docs.rs/futures-core/latest/futures_core/stream/trait.Stream.html
  https://docs.rs/tokio-stream
  https://doc.rust-lang.org/std/async_iter/trait.AsyncIterator.html

## Design principles
1. **Borrowing mode is first-class.** Giving, streaming, lending, poll-based async, generator-backed, and reborrow-aware surfaces are related but not identical.
2. **Invalidation rules beat ergonomic gloss.** The artifact must say exactly when yielded values cease to be valid.
3. **Adapters must be honest.** Allocation, cloning, boxing, pinning, buffering, runtime dependence, and lifetime erasure belong in adapter profiles.
4. **Async specifics stay explicit.** Wake behavior, cancellation, backpressure, `Send`, and `!Send` posture are not incidental details.
5. **Do not standardize too early.** The kit should support “not ready yet” analyses as well as successful common seams.
6. **Vectors over vibes.** Fusedness, cancellation, exhaustion, buffering reuse, and invalidation need executable evidence.
7. **Interop is the point, not universalization.** The goal is comparable surfaces and migrations, not one mega-trait.
8. **Pilot order matters.** Sync lending, async bridging, borrow-callbacks, and domain consumers should not all be treated as equally mature on day one.

## Artifact family

### 1) `lending-surface/v0`
Describes a borrow-friendly sequence surface.

Fields should include:
- surface id and version
- sync / async / generator / cursor kind
- item shape (`T`, `&T`, `&mut T`, `Result<T, E>`, future-returning, etc.)
- exhaustion semantics
- fusedness expectations
- invalidation rules
- cancellation / drop semantics
- object safety / dyn posture
- `Send` / `Sync` / `Unpin` / pinning posture
- no_std / alloc / runtime assumptions
- explicit exclusions

### 2) `borrow-mode-profile/v0`
Describes the borrowing model a surface uses.

Fields should include:
- profile id
- giving / streaming / lending / poll-based async / async-fn / generator-backed mode
- whether borrows can outlive adapter calls
- whether values may borrow from `self`
- mutable/exclusive borrow semantics
- reborrow support or limitations
- borrow invalidation trigger
- whether results can be returned from callers without lifetime collapse

This artifact keeps “borrow-friendly” from degenerating into a vague label.

### 3) `sequence-adapter-profile/v0`
Describes how one surface maps to another.

Fields should include:
- source/target surface ids
- lossless / lossy status
- allocation, buffering, cloning, boxing, and pinning costs
- whether borrow-erasure occurs
- whether wake/cancel semantics change
- runtime assumptions
- unsupported combinators or edge cases
- feature/MSRV requirements

### 4) `yield-vector-set/v0`
Golden vectors for sequence semantics.

Fields should include:
- vector id
- fixture/setup description
- expected yields and timing/order where relevant
- invalidation expectations
- fusedness expectations
- cancellation / drop / wake expectations
- adapter-specific expected behavior
- negative cases and unsupported cases

This is where “the adapter works” becomes an actual claim.

### 5) optional `executor-runtime-profile/v0`
Captures runtime-specific async behavior when it matters.

Fields should include:
- runtime/executor identity
- spawn/local-set assumptions
- wake scheduling expectations
- cooperative yielding or backpressure assumptions
- cancellation/drop guarantees relied upon
- `Send` / local-only constraints
- feature flags and platform caveats

Not every surface needs this, but async borrowing APIs often do.

### 6) `sequence-check-report/v0`
Records what was actually exercised.

Fields should include:
- surfaces and adapters checked
- vectors run / skipped
- pass/fail/partial status
- observed degradations
- runtime/environment details
- attached logs, traces, or minimal reproductions

### 7) `lending-pack/v0`
Bundle of the above plus human-facing docs, migration notes, examples, and CI pointers.

## CLI shape
`cargo lending` should be a thin orchestrator, not a replacement runtime.

Potential commands:
- `cargo lending init` — scaffold a lending surface
- `cargo lending export` — emit surface and adapter artifacts
- `cargo lending check` — run yield vectors across selected surfaces/adapters
- `cargo lending diff` — compare semantic and adapter changes across versions
- `cargo lending pack` — bundle a `lending-pack/v0`

The tool should prefer pointers to fixtures/examples/tests rather than giant generated blobs.

## Initial targets
A first credible version should start where the seam is already real:
1. **Sync lending pilot**
   - `streaming-iterator`
   - `lending-iterator`
   - `lender`
   - selected adapters to/from ordinary `Iterator`
2. **Async sequence pilot**
   - `futures-core::Stream`
   - `tokio-stream`
   - nightly `std::async_iter::AsyncIterator` comparison notes
3. **Borrowing callback / async-closure pilot**
   - borrow-friendly async producer patterns using async closures / AFIT / return-type-notation-sensitive APIs
   - explicitly record returned-future bounds, `Send`/`'static` posture, and capture-borrowing semantics
4. **Pin/runtime-sensitive pilot**
   - isolate local-only, pin-sensitive, or wake/cancel-dependent adapters without pretending broad portability
5. **One domain pilot**
   - line/chunk readers, protocol frame decoders, parser cursors, or row/record windows where borrow reuse is materially valuable

The kit should support both **promotion** (a surface is ready to standardize around) and **deferral** (the language is not ready yet, or the semantics are still too divergent). The pilot-program document should be treated as the ranked execution order.

## What good adoption looks like
A good v1 does not need to settle the final async-iterator design for all Rust.
It needs to prove that the ecosystem can publish honest sequence semantics.

Success would look like:
- one lending surface report that makes invalidation and borrowing rules obvious,
- multiple adapter profiles that expose real allocation or lifetime-erasure tradeoffs,
- vectors catching semantic drift across combinators or adapters,
- one Atlas entry or domain guide that can point to a real sequence-surface contract,
- and migration notes that let future language/library improvements land into an already legible ecosystem.

## Boundaries with other archive proposals
- **Interop Commons Kit** defines how shared building blocks emerge across crates; Lending Surface Kit is a concrete high-priority seam where that pattern may soon matter.
- **Async Lifecycle Kit** is about task ownership, shutdown, and service reliability; Lending Surface Kit is about item production, borrowing, invalidation, pin/runtime posture, and adapter truth.
- **Replay Kit** and **Debugger Experience Kit** handle observability/debugging; Lending Surface Kit defines the semantic surfaces that those tools need to understand.
- **Protocol / Event / Service / Dataset / Media kits** may consume lending surfaces internally, but they are broader application-domain contracts.

## Failure modes to avoid
- creating a new universal `StreamExt` empire and calling it interop;
- hiding borrow invalidation or allocation behind pleasant API names;
- flattening sync and async semantics into one fake model;
- standardizing nightly-era designs before the language settles;
- or assuming runtime-specific conventions are “just how Rust works”.
