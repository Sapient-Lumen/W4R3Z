# Gap: initialization surfaces, in-place construction, and destruction contracts

## What is missing
Rust is now explicitly pushing toward **in-place initialization** and **immobile types with guaranteed destructors**, but the ecosystem still lacks a reviewable way to describe how values are actually **brought into existence and torn down**.

Today there is no standard way to say:
- where a value is first assembled (stack, heap, arena, `MaybeUninit`, `Rc`/`Arc` unique state, foreign allocation, kernel object slot, out-pointer, pinned location),
- whether the address is stable before construction completes and whether moving is ever allowed,
- whether initialization is infallible, fallible, async, multi-phase, self-referential, cyclic, or foreign-driven,
- when weak/self references, borrows, projections, or handles become valid,
- what happens if a later initialization phase fails, unwinds, is cancelled, or leaks,
- whether destruction is ordinary `Drop`, pinned destruction, explicit close/teardown, guaranteed destructor territory, or intentionally best-effort,
- and which of those behaviors are stable public guarantees versus temporary workarounds around current language limits.

That gap matters more now because the Rust roadmap is no longer treating this as a niche corner. The 2026 flagship themes explicitly list **immobile types and guaranteed destructors** under “Just Add Async” and **in-place initialization** under “Beyond the `&`”. The 2025H2 in-place-initialization goal says there are multiple competing proposals and that the project wants to choose a path by experimenting with real users like the Linux kernel and Crubit. Meanwhile, the ecosystem already has point solutions like `pin-init`, `pinned-init`, `moveit`, `pin-project`, `self_cell`, and `yoke`.

So the missing contribution is not “yet another constructor macro”.
It is a **portable way to publish initialization and teardown truth while the language is opening this frontier**.

The new rule for the archive is explicit: keep **ordinary constructors, caller-allocated out-pointers, construct-then-pin, pinned-in-place/fallible assembly, cyclic/weak-self bootstrap, unique-to-shared publication, self-referential borrow-carrying, and foreign-emplace/destructor-coupled** as separate lanes rather than treating them as one “constructor support” bucket.

Sources:
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h2/in-place-initialization.html
- https://docs.rs/pin-init
- https://docs.rs/pinned-init
- https://docs.rs/moveit
- https://docs.rs/pin-project/latest/pin_project/attr.pin_project.html
- https://docs.rs/self_cell
- https://docs.rs/yoke/latest/yoke/struct.Yoke.html
- https://doc.rust-lang.org/std/mem/union.MaybeUninit.html
- https://doc.rust-lang.org/std/rc/struct.Rc.html
- https://doc.rust-lang.org/std/sync/struct.UniqueArc.html

## The current seam is awkward
Rust already has real construction and teardown ingredients, but their semantics are scattered across std docs, roadmap pages, crate docs, and unsafe notes:
- `MaybeUninit` explicitly supports out-pointers so the caller controls allocation and avoids unnecessary moves,
- `Box::pin` and `Pin<Ptr>` expose “construct then pin” or “allocate then pin” pathways,
- `Rc::new_cyclic` and the nightly `UniqueArc` docs show that cyclic and self-referential construction has a public, semantically sharp pre-fully-initialized phase,
- `pin-init` and `pinned-init` expose pinned, fallible, in-place constructors with unique `Rc`/`Arc` setup,
- `moveit` treats emplacement and constructor-style assembly as first-class because C++ interop and `!Unpin` types care about where initialization happens,
- `pin-project` has to model `#[pinned_drop]`, `UnsafeUnpin`, and projection rules because pinned teardown is not a footnote,
- and crates like `self_cell` and `yoke` prove that self-referential and borrow-carrying assembly patterns are already valuable enough to need reusable infrastructure.

So the ecosystem is not missing experimentation.
It is missing the **artifact family that records where initialization happens, what intermediate states exist, how failure/rollback works, and which destruction guarantees were actually checked**.

Sources:
- https://doc.rust-lang.org/std/mem/union.MaybeUninit.html
- https://doc.rust-lang.org/std/pin/index.html
- https://doc.rust-lang.org/std/boxed/struct.Box.html
- https://doc.rust-lang.org/std/rc/struct.Rc.html
- https://doc.rust-lang.org/std/sync/struct.UniqueArc.html
- https://docs.rs/pin-init
- https://docs.rs/pinned-init
- https://docs.rs/moveit
- https://docs.rs/pin-project/latest/pin_project/attr.pin_project.html
- https://docs.rs/self_cell
- https://docs.rs/yoke/latest/yoke/struct.Yoke.html

## Why this matters
This gap matters because many high-value Rust workloads depend on honest construction/teardown semantics that are broader than “just call `new()`”:
1. **pinned and self-referential objects** — async internals, intrusive/data-structure code, and foreign handles care about address stability during and after initialization;
2. **kernel / embedded / systems work** — out-pointers, no-extra-move construction, and explicit teardown semantics are often first-order correctness concerns;
3. **C++ and foreign interop** — constructor/emplacement models and move semantics differ sharply from ordinary Rust moves, so the bridge needs declared truth rather than folklore;
4. **cyclic and weak-self patterns** — `Rc::new_cyclic`, `UniqueArc`, and similar patterns create a semantically meaningful “allocated but not fully constructed” phase;
5. **fallible or async assembly** — once construction spans multiple steps, teams need to know what gets cleaned up, leaked, retried, or exposed on failure or cancellation;
6. **future convergence** — if Rust lands in-place initialization and immobile/guaranteed-destructor features, the ecosystem will need migration artifacts instead of many incompatible homegrown constructor worlds.

A worthy contribution here is therefore not a single blessed init crate.
It is a way to treat **construction and destruction semantics as reviewable ecosystem infrastructure**.

Sources:
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h2/in-place-initialization.html
- https://doc.rust-lang.org/std/mem/union.MaybeUninit.html
- https://doc.rust-lang.org/std/rc/struct.Rc.html
- https://doc.rust-lang.org/std/sync/struct.UniqueArc.html
- https://docs.rs/pin-init
- https://docs.rs/pinned-init
- https://docs.rs/moveit

## What “good” looks like
A worthy contribution here is **not** one universal constructor trait, one magical builder macro, or one unsafe “placement new for Rust” empire.

It is a shared initialization/destruction surface boundary:
- one `init-surface/v0` describing the subject, supported construction families, and stability posture,
- one `placement-init-profile/v0` describing allocation/storage origin, address-stability assumptions, move-before-finish policy, and pinned destination posture,
- one `init-sequence-profile/v0` describing phases, fallibility, async/await or callback-driven steps, exposure timing for weak/self borrows, and partial-init rollback rules,
- one `pin-destruction-profile/v0` describing pinning, immobility, structural-projection assumptions, destructor/close behavior, leak/forget stance, and teardown guarantees,
- one `init-adapter-profile/v0` describing how ordinary `new`/builder APIs, out-pointers, `Box::pin`, `Rc::new_cyclic`, `UniqueArc`, `pin-init`, `moveit`, and self-referential helpers map to one another,
- one `init-vector-set/v0` describing golden cases for construction, failure, rollback, cyclic/self-reference exposure, projection, and teardown,
- one `init-check-report/v0` recording what vectors were actually checked,
- and one `init-pack/v0` bundle for docs, CI, migration notes, and archaeology.

That would let Rust teams reason about initialization and destruction surfaces using **explicit artifacts** instead of a mixture of constructor docs, unsafe comments, RFC memory, and crate-specific folklore.

See also the normative split in [`design/initialization-surface-lane-map.md`](../design/initialization-surface-lane-map.md) and the ranked rollout in [`design/initialization-surface-pilot-program.md`](../design/initialization-surface-pilot-program.md).

## Non-goals
This gap should not be used to:
- define all of Rust’s move, aliasing, or drop semantics,
- flatten ordinary constructors, builders, self-referential helpers, in-place constructors, and async startup flows into one fake universal model,
- bless one init macro or one pinning crate,
- or hide partial-initialization and teardown hazards behind cheerful “ergonomic init” marketing.

The job is smaller and sharper:
**make construction and destruction surfaces legible, honest, and checkable while Rust is trying to make them first-class.**
