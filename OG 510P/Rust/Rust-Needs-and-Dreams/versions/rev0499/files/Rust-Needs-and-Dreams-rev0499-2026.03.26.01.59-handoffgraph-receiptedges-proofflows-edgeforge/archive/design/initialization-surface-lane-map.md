# Design: Initialization Surface lane map (ordinary constructors, out-pointers, construct-then-pin, pinned in-place, cyclic/weak bootstrap, unique-to-shared publication, self-referential borrow-carrying, and foreign-emplace lanes)

## Goal
Sharpen **Initialization Surface Kit** so the archive stops treating “how values are initialized” as one bucket.

Rust already has materially different initialization and teardown lanes, and they differ in **where storage comes from**, **when an address becomes stable**, **whether partial assembly is visible**, **when weak/self or borrowed handles become valid**, **whether publication is one-way**, and **what sort of teardown guarantee follows**.

The archive should therefore keep initialization review grounded in a lane map instead of one flattened “constructor support” story.

## Signals from the current ecosystem
- Rust’s 2026 flagship themes keep **prototype immobile types and guaranteed destructors** under “Just Add Async” and **design alignment on in-place initialization** under “Beyond the `&`”. That means staged construction and teardown semantics are now core roadmap terrain, not niche crate folklore.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The 2025H2 in-place-initialization goal says the project is explicitly comparing multiple competing proposals and real ecosystem experiments, including the Linux kernel and Crubit, before choosing a direction.
  https://rust-lang.github.io/rust-project-goals/2025h2/in-place-initialization.html
- `MaybeUninit` documents out-pointers explicitly as a caller-controlled allocation lane that can avoid extra moves.
  https://doc.rust-lang.org/std/mem/union.MaybeUninit.html
- `Pin` and `Box::pin` keep “construct, then pin” as a real mainstream lane rather than an implementation detail.
  https://doc.rust-lang.org/std/pin/index.html
  https://doc.rust-lang.org/std/boxed/struct.Box.html
- `Arc::new_cyclic` documents an allocated-but-not-fully-constructed phase in which `Weak` exists before `T` is fully placed, and `upgrade` on that weak pointer fails until construction completes.
  https://doc.rust-lang.org/std/sync/struct.Arc.html
- `UniqueArc` explicitly says it is more flexible than `Arc::new_cyclic` for **fallible or async constructors**, which makes uniquely-owned-to-shared publication a separate lane rather than a detail of cyclic construction.
  https://doc.rust-lang.org/std/sync/struct.UniqueArc.html
- `pin-init` / `pinned-init`, `pin-project`, `self_cell`, `yoke`, and `moveit` each expose distinct lane families around pinned in-place assembly, projection/destruction, self-referential or borrow-carrying setup, and C++/foreign emplacement.
  https://docs.rs/pin-init
  https://docs.rs/pinned-init
  https://docs.rs/pin-project/latest/pin_project/attr.pin_project.html
  https://docs.rs/self_cell
  https://docs.rs/yoke/latest/yoke/struct.Yoke.html
  https://docs.rs/moveit

## The lanes

### 1) Ordinary constructor / builder lane
This is the familiar `new()` / builder / fully-formed return-value lane.

What defines it:
- caller receives a fully usable value at the end of construction
- staging is mostly hidden
- move-before-return is usually unremarkable
- teardown usually defaults to ordinary `Drop`

What it is good for:
- the baseline lane that many downstream consumers expect
- comparing adapter costs from simpler construction into more specialized lanes

What it must **not** silently become:
- a claim that address stability existed before return
- a claim that fallible async or partial-init behavior was reviewed
- a claim that pinning, cyclic setup, or destructor guarantees are irrelevant

### 2) Caller-allocated / out-pointer / uninit lane
This is the lane where storage comes first and initialization happens into that storage.

What defines it:
- caller-controlled storage or allocation placement
- `MaybeUninit` / spare-capacity / raw-slot posture
- explicit “write into this place” behavior
- move avoidance is part of the meaning

Why it deserves a separate lane:
- storage authority and initialization authority are split
- initialization can now be reviewed relative to a fixed destination
- the safety boundary depends on partial-init and assume-init posture, not just constructor ergonomics

Design rule:
- preserve storage origin, initialization responsibility, and assume-init boundary separately from ordinary constructor claims

### 3) Construct-then-pin lane
This is the mainstream lane where a value becomes stable only after a pinning step.

What defines it:
- construction happens first
- pinning happens as a later transition (`Box::pin`, pinned wrapper conversion, etc.)
- address stability begins at a different moment than allocation

Why it deserves a separate lane:
- this lane is neither “ordinary constructor” nor “pinned in-place from the start”
- downstream consumers need to know whether moves before pinning were permitted
- adapter costs into or out of this lane can be semantically meaningful

Design rule:
- preserve pre-pin movement policy and post-pin immobility policy separately rather than laundering them into generic “pinned support”

### 4) Pinned in-place / fallible-or-async assembly lane
This is the lane associated with `pin-init`-style construction where the destination is pinned from the moment initialization meaningfully begins.

What defines it:
- destination is fixed early
- assembly may be fallible, callback-driven, or async-shaped
- the lane often exists because moving would violate semantics
- rollback or partial-init behavior is part of the public review surface

Why it deserves a separate lane:
- it is not just “construct then pin, but nicer”
- it changes the timing of address stability
- it often carries different cleanup and publication semantics

Design rule:
- preserve fixed-destination posture, fallibility/cancellation semantics, and rollback behavior separately from construct-then-pin lanes

### 5) Cyclic / weak-self bootstrap lane
This is the lane where a self-reference or weak self-handle exists before the value is fully published.

What defines it:
- allocation exists before full construction completes
- weak/self handles may be minted during construction
- some operations are invalid until publication completes

Why it deserves a separate lane:
- `Arc::new_cyclic` and similar APIs expose a semantically real “not fully initialized yet” phase
- consumers need to know exactly what weak/self handles can do before publication
- this lane is especially sensitive to failure and publication timing

Design rule:
- preserve pre-publication handle validity, upgrade behavior, and rollback semantics explicitly

### 6) Unique-to-shared publication lane
This is the lane where a uniquely owned allocation is prepared privately and only later published into shared ownership.

What defines it:
- uniqueness during setup
- publication is a later step
- the lane can support fallible or async construction more naturally than closure-only cyclic helpers

Why it deserves a separate lane:
- it creates a real boundary between “construction authority” and “shared lifetime begins now”
- it often changes what partial results may exist and who may see them
- it should not be flattened into ordinary `Arc` or ordinary cyclic setup

Design rule:
- preserve unique-phase rights, publication transition, and post-publication capability loss explicitly

### 7) Self-referential / borrow-carrying lane
This is the lane where the final value contains data borrowing from colocated owned data or from a cart/owner relationship.

What defines it:
- internal borrow or dependent object tied to colocated owner/cart data
- construction API must prevent invalid moves or lifetime leakage
- teardown ordering is part of the guarantee

Why it deserves a separate lane:
- the semantic center is not just pinning or placement, but managed internal borrowing
- the lane can be stable-crate infrastructure even before language-native support exists
- consumers need to know what is borrowed from what, and when that relation becomes valid

Design rule:
- preserve owner/cart identity, dependent exposure timing, and teardown ordering separately from generic cyclic or pinned-init claims

### 8) Foreign-emplace / destructor-coupled lane
This is the lane where Rust is participating in another system’s emplacement or destruction contract.

What defines it:
- foreign constructor or out-pointer conventions matter
- relocation may be forbidden for non-Rust reasons
- teardown may be coupled to explicit foreign release or stronger destructor expectations

Why it deserves a separate lane:
- C++ interop and kernel-style constructors are not adequately described as “just another pin-init helper”
- foreign move/destructor rules can dominate the safe public contract
- this lane is where future guaranteed-destructor work matters most visibly

Design rule:
- preserve foreign allocation/constructor/destructor authority and move sensitivity separately from Rust-native placement lanes

## Review rules that follow from the lane map
1. Keep **storage origin** separate from **construction family**.
2. Keep **address-stability timing** separate from **allocation timing**.
3. Keep **construct-then-pin** separate from **pinned-in-place**.
4. Keep **cyclic bootstrap** separate from **unique-to-shared publication**.
5. Keep **self-referential borrow-carrying** separate from **weak-self cyclic setup**.
6. Keep **rollback / unwind / cancellation** separate from **success-path publication**.
7. Keep **teardown/destructor guarantees** separate from **construction convenience**.
8. Keep **foreign emplacement semantics** separate from **Rust-native constructor ergonomics**.

## What a worthy contribution should look like
The worthy contribution here is **not**:
- another constructor macro empire,
- another universal builder trait,
- another “placement new for Rust” slogan crate,
- or another fake init badge.

It is a thin `cargo initsurf` / `init-pack/v0` layer that can preserve:
- lane identity,
- placement and address-stability timing,
- phase/exposure timing,
- rollback and cancellation posture,
- publication transitions,
- teardown and guaranteed-destructor posture,
- adapter lossiness,
- and bounded downstream handoffs.

That means downstream reviewers can answer:
- *which initialization lane actually happened?*
- *when did the object become stable and safely usable?*
- *were weak/self or borrowed handles exposed before full publication?*
- *was this construct-then-pin or pinned-in-place from the start?*
- *what happens on failure, unwind, cancellation, leak, or explicit close?*
- *what may support, safety, interop, or migration consumers legitimately conclude?*

## Immediate archive consequences
Read this together with:
- `design/initialization-surface-kit.md`
- `design/initialization-surface-pilot-program.md`
- `gaps/initialization-surfaces-in-place-construction-and-destruction-contracts.md`
- `proposals/epic-initialization-surface-kit.md`

The next credible move is a ranked pilot path rather than one universal constructor abstraction: std out-pointer and construct-then-pin baseline first, cyclic bootstrap second, unique-to-shared publication third, pinned in-place/fallible lanes fourth, self-referential borrow-carrying fifth, foreign-emplace/destructor-coupled sixth, and language-watch migration notes throughout.
