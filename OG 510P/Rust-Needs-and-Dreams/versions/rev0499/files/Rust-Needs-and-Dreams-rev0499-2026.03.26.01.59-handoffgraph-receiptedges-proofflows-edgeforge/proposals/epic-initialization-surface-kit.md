# Epic proposal: Initialization Surface Kit

## Thesis
One of the strongest missing ecosystem contributions in Rust is a **portable contract for initialization and destruction surfaces**.

Rust is actively moving toward in-place initialization, immobile types, and guaranteed-destructor territory. But the ecosystem still lacks a reviewable, attachable way to state how values are actually assembled: where memory comes from, when the address becomes stable, what happens during fallible or async multi-phase setup, when weak/self references become valid, and what teardown guarantees follow.

In other words: Rust needs a boring, explicit `init-pack/v0` more than it needs one more constructor macro, one more pin helper, or one more self-referential workaround crate pretending the seam is solved.

The lane split in [`design/initialization-surface-lane-map.md`](../design/initialization-surface-lane-map.md) should now be treated as normative at the proposal layer so ordinary constructors, caller-allocated out-pointers, construct-then-pin, pinned-in-place/fallible assembly, cyclic bootstrap, unique-to-shared publication, self-referential borrow-carrying, and foreign-emplace/destructor-coupled lanes never collapse into one fake init verdict.

## Why now
The timing is unusually good:
- the 2026 flagships explicitly call out **immobile types and guaranteed destructors** and **in-place initialization**;
- the 2025H2 in-place-initialization goal says the language is still choosing among competing approaches and wants experiments with users like the Linux kernel and Crubit;
- std already documents semantically sharp construction surfaces like `MaybeUninit` out-pointers, `Rc::new_cyclic`, `Box::pin`, and nightly `UniqueArc`;
- `pin-init` and `pinned-init` already expose pinned, fallible, in-place constructors;
- `moveit` is already carrying constructor/emplacement semantics for Rust/C++ interop;
- `pin-project` has to provide `#[pinned_drop]` and `project_replace` because teardown semantics are part of the public surface;
- and crates like `self_cell` and `yoke` prove that self-referential / borrow-carrying assembly is not hypothetical.

That means the next major construction/destruction seam is visible before it has converged.
This is exactly when a reviewable contract is most valuable.

Sources:
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rust-project-goals/2025h2/in-place-initialization.html
- https://doc.rust-lang.org/std/mem/union.MaybeUninit.html
- https://doc.rust-lang.org/std/rc/struct.Rc.html
- https://doc.rust-lang.org/std/boxed/struct.Box.html
- https://doc.rust-lang.org/std/sync/struct.UniqueArc.html
- https://docs.rs/pin-init
- https://docs.rs/pinned-init
- https://docs.rs/moveit
- https://docs.rs/pin-project/latest/pin_project/attr.pin_project.html
- https://docs.rs/self_cell
- https://docs.rs/yoke/latest/yoke/struct.Yoke.html

## What should be built
The ranked execution path now lives in [`design/initialization-surface-pilot-program.md`](../design/initialization-surface-pilot-program.md), and the proposal layer should stay artifact-first and adapter-heavy rather than chasing one universal constructor abstraction.

A first credible version should ship:
1. `init-surface/v0`, `placement-init-profile/v0`, `init-sequence-profile/v0`, `pin-destruction-profile/v0`, `init-adapter-profile/v0`, `init-vector-set/v0`, `init-check-report/v0`, and `init-pack/v0`
2. one std pilot across `MaybeUninit`, `Box::pin`, and `Rc::new_cyclic`
3. one nightly-notes pilot around `UniqueArc` as a uniquely-owned-to-shared construction lane
4. one pinned-init pilot around `pin-init` / `pinned-init`
5. one self-referential or borrow-carrying pilot around `self_cell` / `yoke`
6. one interop/systems pilot around `moveit`
7. docs and CI that make rollback, weak/self exposure, and teardown semantics explicit

The winning version is small, semantic, and adapter-heavy.
It should make today’s awkward init surfaces legible together rather than prematurely canonizing one abstraction.

## Initial pilots
The proving order should remain explicit: std out-pointer + construct-then-pin baseline first, cyclic bootstrap second, unique-to-shared publication third, pinned in-place/fallible lanes fourth, self-referential borrow-carrying fifth, foreign-emplace/destructor-coupled sixth.

- **Std placement lane** — prove where caller-controlled allocation and no-extra-move construction really begin and end
- **Pinned lane** — show exactly which guarantees arrive via `Box::pin`, pin-init helpers, and projection/destructor helpers
- **Cyclic/self lane** — document when weak/self handles are valid and what “not fully constructed yet” means in practice
- **Interop lane** — compare Rust-native and C++-style constructor/emplacement expectations
- **Teardown lane** — make pinned destruction, explicit close, leak/forget stance, and rollback behavior visible before integration work begins

## Milestones
1. **v0 artifacts + vocabulary**
   - publish schemas and minimal examples
   - document placement, phase, rollback, and teardown vocabulary
2. **v0.2 std and pinned-init pilots**
   - ship std placement/cyclic pilot
   - run vectors over success/failure/rollback behavior
3. **v0.3 self-ref and interop depth**
   - add self-referential and C++/foreign emplacement lanes
   - capture async/fallible construction differences where present
4. **v1 ecosystem pilots**
   - at least three materially different adopters use the artifact family without sharing one exact construction strategy

## Success metrics
- Library authors can review construction and teardown semantics without reconstructing them from unsafe docs and folklore.
- Adapter costs between builder-style, in-place, cyclic, self-referential, and pinned-init lanes become visible before integration work starts.
- Future language features land into a prepared ecosystem with explicit migration notes.
- Atlas-style guidance can recommend pointer- or init-heavy stacks with actual semantic evidence attached.
- Rust avoids fragmenting this seam into many incompatible “almost placement new” worlds.

## Archive fit
This proposal fills a real gap in the archive:
- **Pointer Surface Kit** handles pointer/reference semantics once you have a value in a place;
- **Validity Surface Kit** handles invalid values and initialization invariants;
- **Async Lifecycle Kit** handles task ownership and shutdown choreography;
- **Interop Commons Kit** handles how shared seams emerge;
- **FFI Boundary Kit** handles boundary generation and build integration.

But none of those is the portable contract for **where values are assembled, what intermediate states exist, and what teardown guarantees follow**.
Initialization Surface Kit is the missing substrate for a part of Rust that the language roadmap is explicitly trying to make first-class.
