# Epic Proposal: Borrowing Frontier Stack (`cargo borrowfront`, `borrowing-frontier-pack/v0`)

## One-sentence pitch
Build a thin Rust companion layer for the **borrowing frontier** that links **trait-family truth**, **pointer/reference truth**, **lending/sequence truth**, **initialization/destruction truth**, and **migration/consumer handoffs** into one portable review boundary without pretending the language frontier is already settled or that one workaround crate has already won.

## Deliverables
- reference command:
  - `cargo borrowfront`
- schemas:
  - `borrowing-frontier-brief/v0`
  - `borrowing-frontier-subject/v0`
  - `borrowing-frontier-pack/v0`
  - `borrowing-frontier-diff/v0`
  - `borrowing-frontier-handoff/v0`
- adapters/importers for:
  - `trait-surface/v0`
  - `dyn-dispatch-profile/v0`
  - `return-shape-profile/v0`
  - `pointer-surface/v0`
  - `projection-family-profile/v0`
  - `receiver-coercion-profile/v0`
  - `lending-surface/v0`
  - `borrow-mode-profile/v0`
  - `sequence-adapter-profile/v0`
  - `init-surface/v0`
  - `init-sequence-profile/v0`
  - `pin-destruction-profile/v0`
  - `acceptance-pack/v0`
  - `migration-pack/v0`
  - optional canonical-learning / support / atlas handoffs
- docs:
  - native-vs-adapter-vs-blocked guide
  - custom-pointer and receiver guide
  - lending and async-bridge comparison guide
  - in-place-init and self-referential migration guide
  - consumer-lossiness guide for docs / atlas / support / assistants

## Why now (signals)
- Rust’s 2026 flagship themes explicitly keep **Beyond the `&`** and **Unblocking dormant traits** active, with milestones around field projections, reborrow traits, in-place initialization, the next-generation trait solver, and the Sized hierarchy.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- The 2025H2 reborrow-traits goal says user-space types still cannot take advantage of autoreborrowing, says this blocks ergonomics for generalized references, and says the shiny future includes removing `Pin` special-casing and enabling Rust-for-Linux custom reborrowable reference types; it also explicitly names users of the `reborrow` crate as a migration population.
  https://rust-lang.github.io/rust-project-goals/2025h2/autoreborrow-traits.html
  https://docs.rs/reborrow/latest/reborrow/
- The 2025H2 field-projections goal says Rust makes extensive use of smart pointers, modified references, and custom pointer types and is trying to design an explicit language feature for projection.
  https://rust-lang.github.io/rust-project-goals/2025h2/field-projections.html
- The 2025H2 in-place-initialization goal says the ecosystem already has multiple approaches that the language now wants to evaluate and learn from rather than leaving the space fragmented forever. Userland crates like `pinned-init`, `pin-init`, and `moveit` show that the pressure is real and not theoretical.
  https://rust-lang.github.io/rust-project-goals/2025h2/in-place-initialization.html
  https://docs.rs/pinned-init
  https://docs.rs/pin-init
  https://docs.rs/moveit/latest/moveit/
- RFC 3519 and RFC 3621 keep the custom-pointer story concrete: Rust wants custom receiver types to participate more naturally, and the derive-smart-pointer RFC is explicitly about allowing custom smart pointers to work with trait objects and `self: SmartPointer<Self>` receivers without claiming the whole underlying trait machinery is ready for general stabilization.
  https://rust-lang.github.io/rfcs/3519-arbitrary-self-types-v2.html
  https://rust-lang.github.io/rfcs/3621-derive-smart-pointer.html
- RFC 2996 and the current async/dyn roadmap keep trait-family and lending pressure coupled. `AsyncIterator` is real, but object-safe and consumer ergonomics remain incomplete, while crates like `dynosaur` and `lending-iterator` demonstrate useful userland approximations rather than final closure.
  https://rust-lang.github.io/rfcs/2996-async-iterator.html
  https://docs.rs/dynosaur
  https://docs.rs/lending-iterator/latest/lending_iterator/
- The existing workaround ecology is now durable enough that “wait for the language” is no longer a sufficient archive response. `pin-project`, `ouroboros`, and `self_cell` each keep solving different parts of the frontier, which is exactly the pattern that calls for a review/migration layer above the crates instead of yet another winner-take-all abstraction.
  https://docs.rs/pin-project
  https://docs.rs/ouroboros
  https://docs.rs/self_cell

## The missing seam
Rust now has serious activity on smart pointers, receivers, lending iteration, async trait families, pinning, and in-place construction, but it still lacks the **portable frontier boundary** that answers:

- what exact trait / pointer / lending / initialization subject is under review;
- what semantics are native language/compiler behavior versus macro- or adapter-provided behavior;
- what depends on nightly features, accepted RFCs, project-goal experiments, or unstable solver behavior;
- what migration path exists from today’s workaround crate to tomorrow’s language-native surface;
- what comparisons are apples-to-apples and what are really different semantic families;
- what downstream docs / atlas / support / assistant consumers may safely conclude;
- and what remains honestly in a watch/wait state.

Without that layer, maintainers keep reconstructing the story from RFC memory, nightly experiments, crate docs, proc-macro expansions, unsafe comments, benchmark snippets, and issue archaeology.

## Reference CLI shape
- `cargo borrowfront record`
  - emit `borrowing-frontier-subject/v0` for one concrete frontier review subject
- `cargo borrowfront attach-trait`
  - import trait-family, dyn, and return-shape artifacts
- `cargo borrowfront attach-pointer`
  - import pointer/reference, projection, and receiver artifacts
- `cargo borrowfront attach-lending`
  - import lending / sequence / async-bridge artifacts
- `cargo borrowfront attach-init`
  - import placement / staged-init / pin / teardown artifacts
- `cargo borrowfront attach-acceptance`
  - import solver, nightly, or pattern-acceptance artifacts when relevant
- `cargo borrowfront diff --against <prior-pack|ref|path>`
  - emit `borrowing-frontier-diff/v0`
- `cargo borrowfront render --for <docs|atlas|migration|support|assistant>`
  - emit `borrowing-frontier-handoff/v0`
- `cargo borrowfront pack`
  - produce `borrowing-frontier-pack/v0`
- `cargo borrowfront verify-pack <path>`
  - verify schema versions, checksums, and imported-attachment integrity

This should stay a **thin composition layer**.
It should not replace trait crates, pointer crates, async runtimes, pin-projection helpers, or future language work.

## What `borrowing-frontier-pack/v0` should contain
- `manifest.json`
- `borrowing-frontier-brief.json`
- one or more `borrowing-frontier-subject.json`
- imported trait / pointer / lending / init attachments
- optional acceptance / compatibility / migration attachments
- optional docs / support / atlas handoffs
- optional `borrowing-frontier-diff.json`
- one or more `borrowing-frontier-handoff.json` summaries
- checksums, provenance, freshness, and generator identity

## Design principles
- **Native language progress stays distinct from userland approximation.**
- **Trait truth is not pointer truth.**
- **Lending truth is not async-runtime ownership.**
- **Initialization truth is not constructor syntax.**
- **Accepted RFC or project-goal motion is not shipped stable support.**
- **Migration horizon matters because this frontier is actively moving.**
- **Blocked or partial results are first-class outcomes, not embarrassment.**
- **Consumer summaries are intentionally lossy and say so.**
- **The stack remains thin.**

## Early implementation order
1. pointer / receiver lane
2. lending / reborrow lane
3. dyn-return plus initialization lane
4. foreign / kernel / interop lane
5. migration / consumer lane

That order matches the archive’s pilot logic: first make concrete reference-like and receiver semantics legible, then compare borrowing-sequence lanes, then join trait-family and initialization truth where async/dyn pressure is strongest, then handle foreign semantics, and only then widen toward ecosystem recommendations.

## Non-goals
- a universal smart-pointer trait
- one true lending iterator crate
- a replacement for async runtimes or `Stream`
- a constructor macro empire
- pretending nightly experiments, accepted RFCs, and stable support are interchangeable
- collapsing all borrowing-adjacent progress into one fake readiness badge

## Success bar
This becomes worthy when a maintainer or downstream consumer can answer:
- what exact frontier subject is under review;
- which parts are native, adapter-provided, macro-provided, or still blocked;
- what pointer/receiver semantics really apply;
- what lending or async-sequence semantics really apply;
- what initialization and teardown guarantees really apply;
- what changed versus a prior review point;
- and whether the honest outcome is adopt, compare, migrate partially, or wait,

without flattening the story into one vague “borrowing support” claim.

## Read this with
- `design/borrowing-frontier-stack.md`
- `design/borrowing-frontier-pilot-program.md`
- `gaps/trait-surfaces-dyn-posture-return-shapes-and-impl-truth.md`
- `gaps/reference-surfaces-smart-pointers-and-custom-borrow-contracts.md`
- `gaps/lending-surfaces-borrowing-streams-and-sequence-interop.md`
- `gaps/initialization-surfaces-in-place-construction-and-destruction-contracts.md`
- `design/trait-surface-kit.md`
- `design/pointer-surface-kit.md`
- `design/lending-surface-kit.md`
- `design/initialization-surface-kit.md`
