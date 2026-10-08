# Design: Initialization Surface Kit (`cargo initsurf`, `init-pack/v0`)

## Goal
Define a portable contract for specifying, validating, diffing, and reviewing **initialization and destruction surfaces** in Rust: in-place construction, out-pointer assembly, pinned initialization, cyclic/self-referential setup, fallible or async multi-phase assembly, and the teardown/destructor guarantees that follow.

Read the normative lane split in [`design/initialization-surface-lane-map.md`](./initialization-surface-lane-map.md) and the ranked execution path in [`design/initialization-surface-pilot-program.md`](./initialization-surface-pilot-program.md).

This should help answer questions like:
- where does a value begin life and who controls that storage,
- when does its address become stable and can it ever move again,
- which phases of initialization can fail or suspend,
- when are weak/self handles, borrows, or projections legal to use,
- what happens on rollback, unwind, cancellation, or leak,
- and what evidence shows the object is torn down the way its docs claim.

It should **not** replace `MaybeUninit`, `Pin`, `Drop`, `pin-init`, `moveit`, `self_cell`, or `yoke`.
It should make their semantics reviewable and comparable.

## References (signals)
- Rust’s 2026 flagship themes explicitly list **immobile types and guaranteed destructors** under “Just Add Async” and **in-place initialization** under “Beyond the `&`”.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The 2025H2 in-place-initialization goal says multiple competing proposals exist and that the project wants to experiment with real users like the Linux kernel and Crubit to pick a direction.
  https://rust-lang.github.io/rust-project-goals/2025h2/in-place-initialization.html
- `MaybeUninit` docs explicitly describe out-pointers as a way for callers to control allocation and avoid unnecessary moves.
  https://doc.rust-lang.org/std/mem/union.MaybeUninit.html
- `Pin` docs say pinning prevents a value from being moved or otherwise invalidated at its current location.
  https://doc.rust-lang.org/std/pin/index.html
  https://doc.rust-lang.org/std/pin/struct.Pin.html
- `Box::pin` is a mainstream standard-library pathway for pinned heap construction.
  https://doc.rust-lang.org/std/boxed/struct.Box.html
- `Rc::new_cyclic` exposes a semantically important pre-fully-initialized phase where a weak self-handle exists before the value is placed.
  https://doc.rust-lang.org/std/rc/struct.Rc.html
- Nightly `UniqueArc` documents a uniquely-owned-to-shared construction lane and explicitly says it is more flexible than `Arc::new_cyclic` for fallible or async constructors.
  https://doc.rust-lang.org/std/sync/struct.UniqueArc.html
- `pin-init` and `pinned-init` both expose safe/fallible pinned initialization and unique `Rc`/`Arc` setup.
  https://docs.rs/pin-init
  https://docs.rs/pinned-init
- `moveit` treats in-place construction of Rust and C++ objects as a first-class need.
  https://docs.rs/moveit
- `pin-project` documents `UnsafeUnpin`, `#[pinned_drop]`, and `project_replace`, proving that pinned teardown and replacement semantics are public review surfaces.
  https://docs.rs/pin-project/latest/pin_project/attr.pin_project.html
- `self_cell` and `yoke` show real stable-Rust patterns for self-referential or borrow-carrying assembly.
  https://docs.rs/self_cell
  https://docs.rs/yoke/latest/yoke/struct.Yoke.html

## Design axioms
The lane split is normative: keep **ordinary constructors, caller-allocated out-pointers, construct-then-pin, pinned-in-place/fallible assembly, cyclic/weak-self bootstrap, unique-to-shared publication, self-referential borrow-carrying, and foreign-emplace/destructor-coupled** as distinct review lanes.

1. **Placement is not an implementation detail.** Stack, heap, arena, `MaybeUninit`, foreign allocation, and unique-to-shared RC/ARC setup are semantically different lanes.
2. **Initialization often has phases.** “Allocated”, “partially assembled”, “weak/self handles available”, “fully initialized”, and “shareable” are distinct states.
3. **Failure and cancellation are part of the contract.** Fallible constructors, unwind paths, async setup, and cancellation-sensitive assembly cannot be hidden under one success-path constructor signature.
4. **Pinning and teardown must stay explicit.** Structural pinning, pinned destruction, `project_replace`, guaranteed destructor assumptions, and leak/forget stance are not reducible to ordinary `Drop` docs.
5. **Adapters matter more than empires.** v0 should explain how existing construction styles relate; it should not try to replace them with a single abstraction.
6. **Publication is not the same as allocation.** Cyclic bootstrap, unique-to-shared setup, and self-borrowing lanes should keep “allocated”, “initializing”, “published”, and “shareable” distinct rather than narrating one instant constructor event.
7. **Teardown is part of the surface.** Guaranteed destructors, pinned drop, explicit close, and leak-tolerant lanes should be reviewable with the same care as construction.

## Core artifacts

### 1) `init-surface/v0`
High-level declaration of a subject’s construction/destruction surface.

Fields should include:
- subject identity (crate / type family / module / exported constructor set)
- surface family (`ordinary-constructor`, `builder`, `out-pointer`, `in-place`, `pin-init`, `self-referential`, `cyclic`, `foreign-emplace`, `other`)
- stability posture (`stable`, `experimental`, `nightly`, `crate-workaround`, `migration-lane`)
- intended domains (`async`, `kernel`, `ffi`, `embedded`, `data-structure`, `interop`, `general`)
- primary docs / examples / caveats

### 2) `placement-init-profile/v0`
Describes where memory comes from and what location guarantees exist.

Fields should include:
- storage origin (`stack`, `heap`, `arena`, `caller-provided`, `foreign`, `shared-allocation`, `other`)
- allocation owner and allocator assumptions
- address-stability timing (`stable-after-alloc`, `stable-after-pin`, `stable-after-finish`, `never-guaranteed`)
- move-before-finish policy
- move-after-finish policy
- `MaybeUninit` / out-pointer / spare-capacity usage
- zeroed vs uninitialized vs fully-initialized assumptions
- pinned destination requirement

### 3) `init-sequence-profile/v0`
Describes the phases of assembly.

Fields should include:
- phase graph (`allocate`, `seed-weak`, `write-fields`, `seal`, `publish`, `share`, `other`)
- infallible / fallible / async / callback-driven / foreign-driven classification
- exposure timing for:
  - borrows
  - projections
  - weak/self references
  - trait-object handles
  - external callbacks
- partial-initialization policy
- rollback / unwind / cancellation behavior
- what values or handles are invalid before completion
- thread/runtime assumptions

### 4) `pin-destruction-profile/v0`
Describes post-construction movement and teardown guarantees.

Fields should include:
- pin / immobility posture
- structural-pinning assumptions
- projection and replacement posture (`project`, `project_ref`, `project_replace`, none)
- `Unpin` / `UnsafeUnpin` / pinned-drop notes
- destructor family (`Drop`, `PinnedDrop`, explicit `close`, external release, `forget`-tolerant, leak-sensitive)
- guaranteed-destruction expectations (`required`, `best-effort`, `no-guarantee`, `future-language-lane`)
- teardown side effects / ordering assumptions
- cycle / weak cleanup notes

### 5) `init-adapter-profile/v0`
Describes how one construction surface maps to another.

Fields should include:
- source/target ids
- lossless / lossy / semantic-gap status
- allocation / copy / move / boxing / pinning / refcount effects
- fallibility/cancellation differences
- self-reference / weak-handle differences
- teardown-guarantee differences
- safety preconditions
- MSRV / feature-gate / nightly requirements

### 6) `init-vector-set/v0`
Golden vectors for construction/destruction semantics.

Fields should include:
- vector id
- setup description
- expected intermediate-state behavior
- expected failure/rollback behavior
- expected self-reference / weak-handle behavior
- expected projection / pin / replace behavior
- expected destructor / close / leak behavior
- negative cases and unsupported cases

### 7) `init-check-report/v0`
Records what was actually exercised.

Fields should include:
- surfaces and adapters checked
- vectors run / skipped
- pass/fail/partial status
- observed semantic mismatches
- toolchain / runtime / platform details
- attached logs, compile-fail tests, Miri runs, loom/shuttle hooks if relevant, or minimal reproductions

### 8) `init-pack/v0`
Bundle of the above plus human-facing docs, migration notes, examples, and CI pointers.

## CLI shape
`cargo initsurf` should be a thin orchestrator, not a replacement constructor framework.

Potential commands:
- `cargo initsurf init` — scaffold init-surface metadata
- `cargo initsurf export` — emit init/destruction artifacts
- `cargo initsurf check` — run vectors over selected surfaces/adapters
- `cargo initsurf diff` — compare semantic changes across versions
- `cargo initsurf pack` — bundle an `init-pack/v0`

The tool should prefer references to tests, docs, and fixtures rather than giant generated blobs.

## Initial targets
A first credible version should start where the seam is already visibly real:
1. **Std pilot**
   - `MaybeUninit` out-pointer lane
   - `Box::pin`
   - `Rc::new_cyclic`
   - nightly `UniqueArc` notes where relevant
2. **Pinned-init pilot**
   - `pin-init`
   - `pinned-init`
   - at least one `Rc`/`Arc` unique-to-shared story
3. **Pinned-drop / projection pilot**
   - `pin-project` with `#[pinned_drop]`
   - one `project_replace` example
4. **Self-referential / borrow-carrying pilot**
   - `self_cell`
   - `yoke`
5. **Interop / systems pilot**
   - `moveit` or a closely related C++/foreign emplacement story

The kit should support both **promotion** (a surface is stable enough for other people to rely on) and **deferral** (language support is still moving, so the artifact exists mainly to make the instability honest).

The ranked proving order now lives in [`design/initialization-surface-pilot-program.md`](./initialization-surface-pilot-program.md): std out-pointer + construct-then-pin baseline first, cyclic bootstrap second, unique-to-shared publication third, pinned in-place/fallible lanes fourth, self-referential borrow-carrying fifth, and foreign-emplace/destructor-coupled sixth.

## What good adoption looks like
A good v1 does not need to solve all future init semantics in Rust.
It needs to prove that the ecosystem can publish honest construction/destruction semantics.

Success would look like:
- one report that makes placement and address-stability posture obvious,
- multiple adapters exposing where `new`, in-place, pin-init, and cyclic/self-ref lanes diverge,
- vectors catching drift in rollback, weak-handle exposure, or teardown behavior,
- one Atlas or domain guide pointing to a real initialization contract,
- and migration notes that let future language features land into an already legible ecosystem.

## Lane-map consequence
The archive should now speak about initialization by lane first:
- ordinary constructor / builder lane
- caller-allocated / out-pointer / uninit lane
- construct-then-pin lane
- pinned in-place / fallible-or-async lane
- cyclic / weak-self bootstrap lane
- unique-to-shared publication lane
- self-referential / borrow-carrying lane
- foreign-emplace / destructor-coupled lane

That split is what keeps future borrowing, interop, async, and guaranteed-destructor revisions from collapsing initialization into one fake story.

## Boundaries with other archive proposals
- **Pointer Surface Kit** defines ownership/aliasing/projection semantics of pointer-like types after construction; Initialization Surface Kit defines how values come into existence in a location and what teardown guarantees follow.
- **Validity Surface Kit** defines initialization invariants, invalid values, niches, and boundary-ingress checks; this kit defines staged assembly, placement, rollback, and destruction semantics.
- **Async Lifecycle Kit** handles task scopes, graceful shutdown, and cancellation choreography for running async systems; this kit only covers object/service construction and teardown surfaces.
- **Interop Commons Kit** can later host shared constructor vocabulary if the seam converges, but Initialization Surface Kit is the concrete high-priority contract for getting there.
- **Compile Guidance Kit** can help make constructor/pin errors legible, but it does not define the init/teardown contracts themselves.

## Failure modes to avoid
- inventing one universal constructor trait and calling it “interop”;
- hiding partial initialization or rollback hazards behind builder ergonomics;
- flattening self-referential, cyclic, foreign-emplacement, and ordinary constructors into one fake happy-path manifest;
- treating future language goals as already-settled semantics;
- or pretending pinned teardown and guaranteed-destructor discussions are just implementation details.
