# Gap: lending surfaces, borrowing streams, and sequence interop

## What is missing
Rust is getting closer to the language features needed for a **next generation of borrow-friendly sequence APIs**, but the ecosystem still lacks a reviewable way to describe, compare, and validate those surfaces.

Today there is no standard way to say:
- whether a sequence API yields owned items, shared borrows, mutable borrows, or futures that themselves borrow,
- whether invalidation happens on the next `next`/`poll_next` call, on cancellation, on drop, or on adapter boundaries,
- which adapters between `Iterator`, `StreamingIterator`/`LendingIterator`, `Stream`, nightly `AsyncIterator`, generators, and custom cursor APIs are lossless,
- which runtimes, pinning assumptions, boxing choices, or `Send` expectations are required,
- which combinators preserve borrow-friendliness and which necessarily allocate, clone, buffer, or erase lifetimes,
- and which APIs are genuinely future-facing versus stopgaps caused by current language limits.

Rust’s own roadmap now makes this seam much harder to ignore. The 2025 async goals said the next generation of async libraries has been blocked on stable solutions for async traits and streams. The 2025H2 Polonius goal explicitly targets accepting lending iterators. And the 2026 flagship goals call out “unblocking dormant traits,” including lending iterators, as one of the major ecosystem-shaping lanes.

That means the missing contribution is not just “a nicer iterator crate.”
It is a **portable way to publish sequence-surface truth while the language opens new doors**.

Sources:
- https://rust-lang.github.io/rust-project-goals/2025h1/index.html
- https://rust-lang.github.io/rust-project-goals/2025h2/polonius.html
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rfcs/3654-return-type-notation.html
- https://rust-lang.github.io/rfcs/2996-async-iterator.html

## The current seam is awkward
Rust already has working pieces, but they are split across eras and abstractions:
- `Iterator` is the dominant owned-item baseline,
- `streaming-iterator` exists because standard iterators cannot yield items borrowing from the iterator itself, and explicitly cites `std::io::Lines` as an example that must allocate a `String` per line,
- `lending-iterator` and `lender` show that stable Rust can express generic lending patterns with GAT-heavy APIs,
- `futures-core::Stream` remains the de facto async sequence trait,
- Tokio still documents that its stream utilities had to move into `tokio-stream` because `Stream` was not in `std` for Tokio 1.0,
- RFC 2996 says the plan is to add `Stream` to the standard library as `AsyncIterator`,
- and today `std::async_iter::AsyncIterator` exists only as a nightly experimental API.

So the ecosystem is not missing experimentation.
It is missing the **artifact family that records what a given sequence surface promises, what borrowing modes it supports, how adapters behave, and which edge cases have actually been checked**.

Sources:
- https://doc.rust-lang.org/std/iter/
- https://docs.rs/streaming-iterator
- https://docs.rs/lending-iterator/latest/lending_iterator/
- https://docs.rs/lender
- https://docs.rs/futures-core/latest/futures_core/stream/trait.Stream.html
- https://docs.rs/tokio/latest/tokio/stream/index.html
- https://doc.rust-lang.org/std/async_iter/trait.AsyncIterator.html
- https://rust-lang.github.io/rfcs/2996-async-iterator.html

## Why this matters
This gap matters because many high-value Rust workloads want sequence APIs that are both **borrow-friendly** and **composable**:
1. **zero-copy and low-allocation pipelines** — parsers, codecs, line readers, chunkers, windowed algorithms, and database or columnar cursors want to reuse buffers instead of allocating fresh owned items;
2. **async I/O and protocol stacks** — borrowed frames, borrowed decode results, and streamed body processing need honest pinning/cancellation/runtime semantics;
3. **future language-feature adoption** — once async traits, better async closures, return-type notation, reborrow traits, and Polonius-enabled patterns mature, the ecosystem needs a disciplined way to converge instead of spawning five incompatible “better stream” experiments;
4. **interop and migration** — libraries need to state when they can adapt between owned iterators, lending iterators, and async streams, and what is lost when they do;
5. **debugging and review** — invalidation, fusedness, cancellation, and “borrow survives how long?” rules are exactly the sort of subtle semantics that rot into folklore if they are not made explicit.

The reborrow-traits goal is especially telling here: it argues that user-space types cannot achieve true reborrowing today, which hurts ergonomics for types like `Pin<&mut T>` and other exclusive-reference wrappers. That is not a niche curiosity. It is a signal that sequence and cursor APIs built on borrowing semantics are about to get more important, not less.

Sources:
- https://rust-lang.github.io/rust-project-goals/2025h2/autoreborrow-traits.html
- https://rust-lang.github.io/rfcs/3668-async-closures.html
- https://rust-lang.github.io/rfcs/3654-return-type-notation.html
- https://blog.rust-lang.org/2025/04/08/Project-Goals-2025-March-Update/
- https://blog.rust-lang.org/2025/10/28/project-goals-2025h2/

## What “good” looks like
A worthy contribution here is **not** one universal iterator/stream crate, one runtime-owned `StreamExt` empire, or one political attempt to crown a single async ecosystem.

It is a shared lending/sequence surface boundary:
- one `lending-surface/v0` describing the sequence surface, semantic invariants, and supported ownership/borrowing modes,
- one `borrow-mode-profile/v0` describing whether a surface is giving, streaming, lending, async, poll-based, generator-backed, or reborrow-aware,
- one `sequence-adapter-profile/v0` describing mappings between surfaces and where allocation, boxing, cloning, buffering, or lifetime erasure occurs,
- one `yield-vector-set/v0` describing golden cases for exhaustion, fusedness, invalidation, cancellation, backpressure, and adapter semantics,
- one optional `executor-runtime-profile/v0` describing runtime assumptions, pinning posture, `Send`/`!Send` expectations, and wake/drop behavior where async is involved,
- one `sequence-check-report/v0` recording which vectors and adapters were actually checked,
- and one `lending-pack/v0` bundle for docs, CI, migration notes, and long-term archaeology.

That would let Rust teams treat sequence semantics as **reviewable ecosystem infrastructure** instead of a mix of trait docs, macro examples, issue threads, and oral tradition.

## Non-goals
This gap should not be used to:
- replace `Iterator`, `Stream`, or `AsyncIterator` with a grand unified supertrait,
- flatten sync iteration, async polling, and runtime lifecycle into one fake model,
- hide allocation, boxing, or borrow-erasure costs behind “ergonomic” adapters,
- or treat every domain-specific cursor or parser API as though it must be standardized immediately.

The job is smaller and sharper:
**make borrowing-aware sequence surfaces legible, honest, and checkable while the language and ecosystem are opening this frontier.**


## Why the archive should treat this as a staged execution problem now
The current Rust roadmap no longer treats lending-style APIs as a fringe curiosity. The async flagship says the next generation of async libraries has been blocked on stable async traits and streams; the 2025H2 Polonius goal explicitly ties lending iterators to borrow-checker progress; the reborrow-traits goal says userland still cannot achieve true reborrowing; and the 2026 flagships keep both lending iterators and reborrow progress in active view. That means the gap is not only “we need better language features”. It is also “we need a reviewable ecosystem seam that can advance in ranked pilots while the language keeps moving.”

The archive should therefore prefer a ranked pilot program over a search for one perfect trait. The immediate question is not “what is the final universal sequence API?” but “which borrowing sequence lanes can we describe, compare, and test honestly today?”
