# Epic proposal: Pointer Surface Kit

## Thesis
One of the strongest missing ecosystem contributions in Rust is a **portable contract for pointer-like and reference-like surfaces**.

Rust is now actively trying to make user-defined smart pointers feel like first-class language participants. But the ecosystem still lacks a reviewable, attachable way to state what a pointer abstraction means: identity, aliasing, uniqueness, projection families, receiver/coercion posture, clone cost, weak-pointer behavior, and conversion truth.

In other words: Rust needs a boring, explicit `pointer-pack/v0` more than it needs one more clever smart-pointer crate or another half-standardized unsafe pattern.

## Why now
The timing is unusually good:
- 2025H2 made “Beyond the `&`” a flagship Rust theme;
- 2026 flagships keep pushing field projections, reborrow traits, and in-place-initialization alignment;
- RFC 3519 says custom smart pointers are still second-class citizens today;
- RFC 3621 exists because custom smart pointers need dyn/trait-object support, not just prettier syntax;
- the reborrow-traits work explicitly points at replacing the current `Pin<&mut T>` special-case with a real reborrow story;
- and Rust-for-Linux still depends on unstable smart-pointer-related language features.

That means the next major pointer/design seam is visible before it has fully converged.
This is exactly when a reviewable contract is most valuable.

Sources:
- https://rust-lang.github.io/rust-project-goals/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://rust-lang.github.io/rfcs/3519-arbitrary-self-types-v2.html
- https://rust-lang.github.io/rfcs/3621-derive-smart-pointer.html
- https://rust-lang.github.io/rust-project-goals/2025h2/autoreborrow-traits.html
- https://rust-lang.github.io/rust-project-goals/2025h2/Rust-for-Linux-language.html

## What should be built
A first credible version should ship, and it should do so through a ranked pilot program rather than pretending all pointer families are equally mature on day one:
1. `pointer-surface/v0`, `alias-uniqueness-profile/v0`, `projection-family-profile/v0`, `receiver-coercion-profile/v0`, `pointer-transition-profile/v0`, `pointer-vector-set/v0`, `pointer-check-report/v0`, and `pointer-pack/v0`
2. one std pilot across `Rc`, `Arc`, and selected `Pin<Ptr>` forms
3. one custom-smart-pointer pilot around arbitrary-self-types / derive-smart-pointer-aligned experiments
4. one foreign/systems pilot around Rust-for-Linux-style or foreign-reference semantics
5. docs and CI that make identity/share/uniqueness/projection/receiver assumptions explicit

The winning version is small, semantic, and adapter-heavy.
It should make today’s awkward pointer surfaces legible together rather than prematurely canonizing one abstraction.

## Initial pilots
Treat [`design/pointer-surface-pilot-program.md`](../design/pointer-surface-pilot-program.md) as the execution anchor.

- **Shared-ownership lane** — prove what clone, uniqueness, weak references, unique-to-shared construction, weakless borrowed-arc families, publication wrappers, and mutation actually mean for `Rc`/`Arc`-style APIs without letting ergonomic-ref-counting syntax flatten those differences
- **Pinned lane** — show exactly which projection and invalidation rules survive through `Pin`
- **Foreign-reference lane** — document a pointer surface that intentionally does not claim ordinary Rust-reference exclusivity
- **Receiver/dyn lane** — compare pointer forms that do or do not support method receivers, coercions, and trait-object dispatch
- **Move-projection lane** — capture when a pointer-like surface supports move projection and what happens to the husk that remains

## Milestones
1. **v0 artifacts + vocabulary**
   - publish schemas and minimal examples
   - document identity, uniqueness, projection, and transition vocabulary
2. **v0.2 std and custom pilots**
   - ship std-pointer pilot
   - run vectors over identity/share/unique/drop/projection/reborrow behavior
3. **v0.3 foreign and receiver depth**
   - add receiver/dyn posture
   - capture foreign/runtime-defined reference semantics explicitly
4. **v0.4 projection-family depth**
   - compare plain field access, pinned projections, and move-projection/post-move cleanup stories
5. **v1 ecosystem pilots**
   - at least three materially different adopters use the artifact family without sharing one exact pointer implementation strategy

## Success metrics
- Library authors can review pointer abstractions without reconstructing semantics from unsafe docs and folklore.
- Adapter costs between pointer forms become visible before integration or FFI work starts.
- Identity and uniqueness claims become checkable instead of being inferred from type names.
- Future language features land into a prepared ecosystem with explicit migration notes.
- Atlas-style guidance can recommend pointer-heavy stacks with actual semantic evidence attached.
- Rust avoids fragmenting this seam into many incompatible “almost-reference” universes.

## Archive fit
This proposal fills a real gap in the archive:
- **Initialization Surface Kit** handles staged construction and teardown timing;
- **Trait Surface Kit** handles trait families and dyn/return-shape truth;
- **Lending Surface Kit** handles borrowing-aware sequence production;
- **FFI Boundary Kit** handles generated boundary code;
- **Safety / Sanitizer / Verification** proposals handle deeper assurance and checking.

But none of those is the portable contract for **pointer-like identity, aliasing, projection, receiver, and lifecycle semantics**.
Pointer Surface Kit is the missing substrate for a part of Rust that the language roadmap is explicitly trying to make first-class.


## Lane-map sharpen (rev0323)
Read [`design/pointer-shared-ownership-lane-map.md`](../design/pointer-shared-ownership-lane-map.md) alongside the pilot before proposing any shared-ownership contribution. The archive should now treat ordinary `Rc`, ordinary `Arc`, unique-to-shared construction, weakless or borrowed-arc families (`triomphe`-style), publication/storage layers (`arc-swap`-style), and language-watch ergonomic-ref-counting work as distinct but connected review lanes rather than one fake ‘Arc ergonomics’ bucket.
