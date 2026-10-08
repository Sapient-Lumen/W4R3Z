# Design: Borrowing Frontier Stack (Trait Surface + Pointer Surface + Lending Surface + Initialization Surface)

## Goal
Treat **Trait Surface Kit**, **Pointer Surface Kit**, **Lending Surface Kit**, and **Initialization Surface Kit** as one shared **Borrowing Frontier Stack**.

The missing contribution is not one more smart-pointer crate, one more trait macro, one more stream facade, or one more pinned-constructor helper.
It is a **reviewable, migration-aware substrate** for the part of Rust that is being actively reopened by the language roadmap:
- smart pointers and custom receivers beyond `&` / `&mut`,
- lending and reborrow-friendly sequence APIs,
- dyn-capable async and RPITIT-heavy trait families,
- and in-place / pinned initialization and destruction semantics.

Those are not the same thing, and the stack only works if they stay distinct:
- **trait-family truth** — dyn posture, return-shape guarantees, split-family structure, and adapter costs;
- **pointer/reference truth** — identity, aliasing, reborrow, projection, receiver, and foreign-semantic posture;
- **borrowing-sequence truth** — yield/borrow modes, async/runtime posture, and adapter lossiness;
- **initialization/destruction truth** — placement, staged assembly, pinning, publication timing, and teardown guarantees.

The worthy contribution here is to make those truths **portable and composable** before the language frontier is fully settled.

## Why this seam matters now
Current official Rust work is unusually aligned around this exact frontier:
- Rust’s 2026 flagship themes explicitly group **Beyond the `&`** and **Unblocking dormant traits** as active long-range themes, with 2026 milestones around **field projections**, **reborrow traits**, **in-place initialization**, **next-solver stabilization**, and the **Sized hierarchy**.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The 2025H2 goals make the coupling even clearer:
  - **reborrow traits** aims to eliminate `Pin` reborrow special-casing, enable Rust-for-Linux custom reference types, and move users beyond userland facsimiles of reborrowing;
    https://rust-lang.github.io/rust-project-goals/2025h2/autoreborrow-traits.html
  - **pin ergonomics** aims to improve borrowing syntax, patterns, coercions, and receiver ergonomics for pinned values;
    https://rust-lang.github.io/rust-project-goals/2025h2/pin-ergonomics.html
  - **in-place initialization** explicitly says the ecosystem already has multiple competing crates and macros, and that the project now wants to learn from them instead of leaving the space fragmented forever;
    https://rust-lang.github.io/rust-project-goals/2025h2/in-place-initialization.html
  - **Polonius** is motivated directly by future patterns such as lending iterators.
    https://rust-lang.github.io/rust-project-goals/2025h2/polonius.html
- RFC 3519 says user-defined smart pointers are still second-class citizens today and motivates a `Receiver` trait partly from foreign-language and systems use cases that cannot honestly claim `&T` semantics.
  https://rust-lang.github.io/rfcs/3519-arbitrary-self-types-v2.html
- RFC 3654 and the async-traits roadmap make it clear that trait methods returning opaques need explicit reviewable bounds, while the 2026 goals continue pushing toward `async fn` in dyn traits.
  https://rust-lang.github.io/rfcs/3654-return-type-notation.html
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- RFC 2996 makes the shared `AsyncIterator` story explicit but also shows why the current object-safe / consumer ergonomics story remains incomplete.
  https://rust-lang.github.io/rfcs/2996-async-iterator.html

Taken together, this means the ecosystem frontier is no longer “wait for the language” and no longer “just build another workaround crate”.
It is “publish honest surfaces, vectors, adapters, and migration notes while the language converges”.

The userland workaround ecology is also now mature enough to matter strategically, not just tactically:
- `reborrow` explicitly exists to make generalized references more ergonomic through borrowing and reborrowing;
- `lending-iterator` explicitly presents fully generic lending iterators in stable Rust;
- `dynosaur` explicitly targets dynamic dispatch for traits using `async fn` and `-> impl Trait`;
- `pin-project`, `pinned-init`, `pin-init`, `moveit`, `ouroboros`, and `self_cell` keep solving different projection / in-place-init / self-referential niches.
That is exactly the pattern where the missing contribution is a **portable frontier layer above the crates**, not one more attempt to declare a final winner.

Related proposal:
- [`proposals/epic-borrowing-frontier-stack.md`](../proposals/epic-borrowing-frontier-stack.md)

## What each kit owns
### Trait Surface Kit
[`design/trait-surface-kit.md`](./trait-surface-kit.md) owns:
- dyn posture,
- return-shape guarantees,
- impl coverage,
- split-family / adapter truth,
- trait-family vectors and migration notes.

Its question is:
> what does this trait family promise, and how does it evolve?

### Pointer Surface Kit
[`design/pointer-surface-kit.md`](./pointer-surface-kit.md) owns:
- identity / alias / uniqueness truth,
- projection and reborrow families,
- receiver/coercion posture,
- foreign or kernel-facing non-reference semantics,
- pointer transition profiles.

Its question is:
> what kind of reference-like thing is this, and what operations are actually valid through it?

### Lending Surface Kit
[`design/lending-surface-kit.md`](./lending-surface-kit.md) owns:
- borrowing-mode profiles,
- yield semantics,
- async/runtime assumptions,
- adapter truth across iterator/stream/lending families,
- executable sequence vectors.

Its question is:
> how are values yielded or borrowed over time, and what runtime/language assumptions does that require?

### Initialization Surface Kit
[`design/initialization-surface-kit.md`](./initialization-surface-kit.md) owns:
- placement and address-stability truth,
- staged/fallible/async assembly,
- weak/self exposure timing,
- pinned construction and replacement,
- destruction / guaranteed-drop posture.

Its question is:
> how does a value come into existence, become safely usable, and get torn down?

## Shared stack thesis
A serious contribution here should let a reviewer answer all of these without reconstructing semantics from RFC memory, macro docs, unsafe comments, and folklore:
1. What are the semantic claims of the trait family?
2. What reference/pointer semantics are required to call or implement it honestly?
3. What borrowing or yielding semantics does it expose over time?
4. Does use of the surface depend on pinning, in-place initialization, or guaranteed destruction assumptions?
5. Which parts are native language support, which parts are adapter/macro/workaround behavior, and which parts remain watch/wait?
6. What migration path exists as the language frontier moves?

If the stack cannot answer those six questions, it is not yet ecosystem infrastructure.

## Recommended execution posture
The stack now needs a shared execution layer, captured in:
- [`design/borrowing-frontier-pilot-program.md`](./borrowing-frontier-pilot-program.md)
- [`design/initialization-surface-lane-map.md`](./initialization-surface-lane-map.md)
- [`design/initialization-surface-pilot-program.md`](./initialization-surface-pilot-program.md)

That pilot program should prove the stack in the following order:
1. **pointer/receiver lane** — `Pin`, projections, receiver posture, and trait-family contracts
2. **lending/reborrow lane** — borrowing sequences and explicit language/runtime blockers
3. **dyn-return lane** — async/RPITIT trait families plus in-place return/initialization assumptions
4. **foreign/kernel lane** — custom reference semantics, out-ptr/pinned-init posture, and honest non-`&T` behavior
5. **migration/consumer lane** — atlas/docs/migration-facing import paths and readiness verdicts

That ordering is intentional.
The archive should not jump straight to universal abstraction crates, giant language-manifest schemas, or one fake “borrowing support” badge.
It should first prove that Rust projects can publish enough surface truth to make real reviews and migrations legible.

## Design principles
1. **Do not flatten language-adjacent seams into one mega-kit.** Trait, pointer, lending, and initialization semantics must remain distinct owners.
2. **Adapters stay visible.** Macro shims, boxed dyn bridges, pinned constructors, userland reborrow facsimiles, and domain wrappers are part of the truth, not embarrassing details to hide.
3. **Watch/wait is a first-class result.** Some seams are blocked on language/compiler work; the stack must be able to publish “not ready yet” honestly.
4. **Migration matters.** The point is not just describing today’s workaround; it is preserving a clean path as next-solver, reborrow traits, field projections, pin ergonomics, and in-place initialization evolve.
5. **Foreign semantics are not bugs.** Kernel/C++/FFI reference-like types may be valuable precisely because they are not Rust references.
6. **Shared vocabulary beats premature convergence.** The stack should make competing approaches comparable before trying to standardize one of them.

## What an epic contribution would look like in practice
A serious contribution here would:
- give trait-heavy crates a way to publish dyn / return-shape / split-family truth;
- give pointer-like crates a way to publish identity / aliasing / projection / receiver truth;
- give lending and async-sequence crates a way to publish borrow-mode and adapter truth;
- give pinned / out-ptr / self-referential / interop constructors a way to publish staged assembly and teardown truth;
- and give Atlas / Migration / Docs / Support consumers a stable handoff instead of asking them to infer everything from source and folklore.

## Anti-goals
Do not turn this stack into:
- one universal smart-pointer trait,
- one universal `Stream` replacement,
- one giant trait-system manifesto,
- one constructor empire,
- or one fake “Rust borrowing maturity” score.

The stack is a **review boundary and migration substrate**, not a substitute language design process.
