# Design: Pointer Surface Kit (`cargo pointer`, `pointer-pack/v0`)

## Goal
Define a portable contract for specifying, validating, diffing, and reviewing **custom pointer-like and reference-like surfaces** in Rust: ref-counted pointers, pinned wrappers, foreign-language references, intrusive pointers, handle-backed views, custom reborrowable references, and related adapters.

This should help answer questions like:
- what counts as identity for this surface,
- what “clone” means in user-visible terms,
- when a unique or mutable view may be obtained,
- what kinds of projection/reborrow/move-projection are supported,
- whether methods can be called through it and whether dyn dispatch works,
- what conversions are lossless versus allocation-heavy, runtime-checked, or unsafe,
- and what evidence shows the abstraction behaves as claimed.

It should **not** replace std pointer types, settle Rust’s memory model, or create one giant smart-pointer trait hierarchy.
It should make pointer semantics reviewable and comparable.

## References (signals)
- Rust’s 2025H2 flagship theme is “Beyond the `&`”, explicitly aimed at making user-defined smart pointers as ergonomic as built-in references.
  https://rust-lang.github.io/rust-project-goals/
  https://blog.rust-lang.org/2025/11/19/project-goals-update-october-2025/
- The 2026 flagships continue this lane with field projections, reborrow traits, and in-place-initialization alignment.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- RFC 3519 says user-defined smart pointers are second-class citizens today and motivates arbitrary self types partly from Rust-for-Linux and foreign-language reference semantics.
  https://rust-lang.github.io/rfcs/3519-arbitrary-self-types-v2.html
- RFC 3621 exists to let custom smart pointers work with trait objects and says the stabilized behavior depends on the derive macro rather than exposing a stable manual expansion.
  https://rust-lang.github.io/rfcs/3621-derive-smart-pointer.html
- The field-projections goal says the solution should be broad enough for complex projection problems such as pin projections and `RcuMutex<T>`.
  https://rust-lang.github.io/rust-project-goals/2025h2/field-projections.html
- The reborrow-traits goal says the existing `Pin<&mut T>` compiler special-case could likely be reimagined to rely on a `Reborrow` trait.
  https://rust-lang.github.io/rust-project-goals/2025h2/autoreborrow-traits.html
- Rust-for-Linux still depends on unstable smart-pointer-related language features.
  https://rust-lang.github.io/rust-project-goals/2025h2/Rust-for-Linux-language.html
- Std docs show that `Arc`/`Rc`/`Pin` already expose materially different semantics around identity, uniqueness, clone-on-write, weak references, and pinning.
  https://doc.rust-lang.org/std/sync/struct.Arc.html
  https://doc.rust-lang.org/std/rc/struct.Rc.html
  https://doc.rust-lang.org/std/pin/index.html
  https://doc.rust-lang.org/std/pin/struct.Pin.html
- The ergonomic-ref-counting goal and the broader shared-ownership crate ecology now justify an explicit shared-ownership lane map instead of one generic “cheap clone” story.
  https://rust-lang.github.io/rust-project-goals/2025h2/ergonomic-rc.html
  https://docs.rs/triomphe/latest/triomphe/
  https://docs.rs/arc-swap
- Pin ergonomics remains an active goal because pinned borrowing syntax, pin-aware method receivers, and related ergonomics are still being designed.
  https://rust-lang.github.io/rust-project-goals/2025h2/pin-ergonomics.html

## Design principles
1. **Identity is first-class.** Allocation identity, metadata-insensitive pointer identity, and value equality are different truths.
2. **Cheap clone is not a trivial label.** Alias creation, clone-on-write preparation, weak dissociation, and deep duplication must stay distinct.
3. **Uniqueness needs honest evidence.** Safe checks, unsafe obligations, and temporary witnesses are not interchangeable.
4. **Projection families stay explicit.** Shared, mutable, pinned, and move-projection semantics are related but not identical.
5. **Receiver/dyn posture is part of the surface.** Can you call methods, coerce, unsize, or dyn-dispatch through this thing?
6. **Unsafe invariants stay attached, not erased.** The kit should point to raw invariants and preconditions rather than pretending they vanished.
7. **Adapters matter.** Conversion cost, borrow loss, clone-on-write, runtime validation, and allocation are the interesting parts.
8. **Do not over-standardize the memory model.** v0 should record operational guarantees and attachments, not attempt to canonicalize all provenance or aliasing theory.

## Artifact family

### 1) `pointer-surface/v0`
Top-level declaration of a pointer-like surface.

Fields should include:
- crate / module / type identity
- pointer family (`shared_rc`, `shared_arc`, `pinned_wrapper`, `foreign_ref`, `handle_view`, `intrusive`, `custom`)
- pointee kind (`sized`, `dst`, `trait_object`, `opaque_foreign`, etc.)
- identity posture (`value_eq`, `allocation_id`, metadata-insensitive pointer id, mixed)
- stable operations exposed (clone, downgrade, projection, reborrow, make_mut, pin access, method receiver)
- whether the surface claims Rust-reference semantics, modified-reference semantics, or foreign/runtime-defined semantics
- raw invariant/documentation attachments

### 2) `alias-uniqueness-profile/v0`
Captures user-visible sharing and mutation semantics.

Fields should include:
- ownership posture (shared / exclusive / move-only / borrowed / hybrid)
- clone semantics (cheap alias, deep copy, clone-on-write prep, unsupported)
- weak / downgrade / cycle posture
- uniqueness witness kinds (`safe_get_mut`, `runtime_check`, `unsafe_obligation`, `temporary_flag`, `none`)
- mutation gates and what invalidates them
- thread / `Send` / `Sync` assumptions where relevant
- foreign-runtime or kernel assumptions where relevant

### 3) `projection-family-profile/v0`
Describes subviews and temporary access.

Fields should include:
- supported projection families (`shared`, `mutable`, `pinned`, `move`, `none`)
- structural pinning rules
- reborrow support / limitations
- temporary view lifetimes and invalidation triggers
- whether projection is safe, checked, unsafe, or macro/generated
- post-move husk / teardown posture where relevant
- known unsound / unsupported patterns

### 4) `receiver-coercion-profile/v0`
Describes method and trait-object interaction.

Fields should include:
- method-receiver support (`self`, `&self`, `&mut self`, arbitrary self types, custom receiver traits)
- deref-based vs receiver-trait-based behavior
- unsizing / coercion support
- dyn-dispatch posture
- trait-object limitations
- derive/proc-macro dependence
- feature-gate or nightly requirements

### 5) `pointer-transition-profile/v0`
Describes how one pointer surface maps to another.

Fields should include:
- source/target ids
- lossless / lossy / semantic-gap status
- allocation, clone, refcount, boxing, runtime-check, and lifetime effects
- change in identity / aliasing / mutation / pinning semantics
- safety preconditions
- unsupported cases
- MSRV / feature requirements

### 6) `pointer-vector-set/v0`
Golden vectors for pointer semantics.

Fields should include:
- vector id
- fixture/setup description
- expected identity and equality outcomes
- expected clone/share/unique/drop outcomes
- projection/reborrow/move-projection expectations
- receiver/dyn-dispatch expectations
- adapter-specific expected behavior
- negative cases and unsupported cases

### 7) `pointer-check-report/v0`
Records what was actually exercised.

Fields should include:
- surfaces and adapters checked
- vectors run / skipped
- pass/fail/partial status
- observed degradations or semantic mismatches
- runtime/toolchain/environment details
- attached logs, Miri runs, compile-fail tests, or minimal reproductions

### 8) `pointer-pack/v0`
Bundle of the above plus human-facing docs, migration notes, examples, and CI pointers.

## CLI shape
`cargo pointer` should be a thin orchestrator, not a replacement pointer library.

Potential commands:
- `cargo pointer init` — scaffold pointer-surface metadata
- `cargo pointer export` — emit pointer surfaces and attached profiles
- `cargo pointer check` — run vectors over selected surfaces/adapters
- `cargo pointer diff` — compare semantic changes across versions
- `cargo pointer pack` — bundle a `pointer-pack/v0`

The tool should prefer references to tests, docs, and fixtures rather than giant generated blobs.

## Initial targets
A first credible version should start where the seam is already real. Use [`design/pointer-surface-pilot-program.md`](./pointer-surface-pilot-program.md) as the ranked execution layer so the kit proves value lane-by-lane instead of posing as a universal smart-pointer standard:
1. **Std pointer pilot**
   - `Rc`
   - `Arc`
   - selected `Pin<Ptr>` forms
2. **Custom-smart-pointer pilot**
   - arbitrary-self-types / derive-smart-pointer-aligned experiments
   - one crate or prototype that exposes custom receiver behavior
3. **Foreign / systems pilot**
   - Rust-for-Linux-style custom `Arc` / intrusive-pointer notes
   - one foreign-reference or opaque-reference example
4. **Projection / reborrow pilot**
   - one case where projection or reborrow behavior is materially different from plain `Deref`
   - one case where move-projection or husk cleanup semantics are explicit and reviewable

The kit should support both **promotion** (a pointer surface is ready for ecosystem convergence) and **deferral** (language support is still moving, or semantics are still too unstable). The strongest next move is now an explicit pilot order: shared-ownership first, then pinned projection, then foreign-reference truth, then receiver/dyn posture, then transition/migration consumers. The shared-ownership pilot should now read [`design/pointer-shared-ownership-lane-map.md`](./pointer-shared-ownership-lane-map.md) together with the main kit so `Rc`, `Arc`, unique-to-shared construction, weakless borrowed-arc families, publication layers, and language-watch ergonomics do not collapse into one fake lane.

## What good adoption looks like
A good v1 does not need to solve all future pointer ergonomics in Rust.
It needs to prove that the ecosystem can publish honest pointer semantics.

Success would look like:
- one pointer surface report that makes identity, clone/share, and uniqueness semantics obvious,
- multiple transition profiles exposing real losses or safety preconditions,
- vectors catching drift in projection, reborrow, receiver, or dyn behavior,
- one Atlas or domain guide pointing to a real pointer contract,
- and migration notes that let future language features land into an already legible ecosystem.

## Boundaries with other archive proposals
- **Initialization Surface Kit** defines placement, staged assembly, and teardown timing; Pointer Surface Kit starts once a pointer-like surface exists and specifies its steady-state semantics.
- **Trait Surface Kit** defines trait families and return/dyn posture; Pointer Surface Kit defines the pointer-side receiver/coercion semantics those traits may rely on.
- **Lending Surface Kit** is about item production and borrowing sequences; Pointer Surface Kit is about pointer/reference-like ownership, projection, and receiver semantics.
- **FFI Boundary Kit** handles generated bindings and interop workflows; Pointer Surface Kit covers the semantics of Rust-side reference wrappers and pointer abstractions themselves.
- **Safety Evidence / Formal Verification / Sanitizer** kits can attach deeper assurance evidence, but Pointer Surface Kit defines the operational surface they are checking.

## Failure modes to avoid
- inventing one universal smart-pointer trait and calling it “interop”;
- hiding clone, aliasing, or runtime validation costs behind pretty names;
- flattening foreign references and Rust references into one fake semantics;
- treating unstable language experiments as if they were already settled;
- or pretending raw pointer/provenance questions have been fully solved by metadata.
