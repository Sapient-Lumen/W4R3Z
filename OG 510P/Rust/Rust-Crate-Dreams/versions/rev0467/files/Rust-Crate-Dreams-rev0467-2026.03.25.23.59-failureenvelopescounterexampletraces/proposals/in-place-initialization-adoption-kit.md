---
id: P-0447
title: In-Place Initialization Adoption Kit — placement topology, constructor-lane comparison, address-commit receipts, and failure-cleanup evidence above pin-init, moveit, Crubit `Ctor`, and future language support
status: idea
domains: [language, memory, pinning, ffi, cxx, async, kernel, devtools]
last_reviewed: 2026-03-22
evidence:
  - https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  - https://rust-lang.github.io/rust-project-goals/2025h2/in-place-initialization.html
  - https://rust-lang.github.io/rust-project-goals/2025h2/autoreborrow-traits.html
  - https://docs.rs/moveit/latest/moveit/
  - https://docs.rs/pin-init/latest/pin_init/
  - https://github.com/google/crubit/blob/main/support/ctor.rs
  - https://lpc.events/event/19/contributions/2018/attachments/1769/3837/handout.pdf
---

# Problem

Rust now has unusually explicit pressure toward **in-place initialization** and **pinned construction**:

- the official 2026 roadmap keeps “Beyond the `&`” focused on field projections, reborrow traits, and design alignment on in-place initialization;
- the 2025H2 in-place-initialization goal names five concrete drivers: avoiding stack overflow for large heap values, C++ interop, C out-pointer constructors that must pin immediately, async fn in dyn trait, and self-referential types;
- `moveit`, `pin-init`, and Crubit `Ctor` each prove part of the story in practice;
- and the latest pin-init material shows teams already need field-wise composition, fallible initialization, pinned field embedding, and projection support.

But the ecosystem still lacks one boring, reviewable crate that lets downstream teams answer:

1. **where initialization actually happens**,
2. **which constructor family / move semantics are in play**,
3. **when the final address becomes authoritative**,
4. **how failure and cleanup behave**,
5. **and what changed when one initialization strategy is replaced by another**.

The missing crate is **not** another macro-only experiment, another grand language proposal, or another one-off pinning helper.

The missing crate is a **support-contract layer** for in-place initialization adoption.

# What it provides

- `init-profile.toml` — declares chosen constructor families, address-stability expectations, fallibility posture, and embedding requirements.
- `placement-topology.receipt.json` — records where bytes are first written, where the final address lives, whether the value was stack-bounced, and whether caller-provided storage was involved.
- `constructor-lane.report.json` — compares by-value Rust construction, `pin-init`, `moveit::New`, Crubit `Ctor`, local out-pointer adapters, and future language-aligned modes.
- `address-commit.receipt.json` — states when the final address becomes authoritative, when pinning begins, and which moves are forbidden after that point.
- `failure-cleanup.report.json` — records partial-init edges, rollback/destructor behavior, and which paths may leave initialized state behind.
- `init-transition.diff.json` — classifies strategy changes across revisions.
- `init-support-bundle.manifest.json` — portable bundle manifest joining profiles, receipts, examples, raw command lines, and notes.
- `cargo init-adopt explain` — explains one case in receiver-facing language.
- `cargo init-adopt diff` — compares two revisions and highlights changed constructor authority or cleanup posture.
- `cargo init-adopt bundle` — emits one reviewable bundle for design review, audits, or upstream language discussions.

# What the crate should provide other people

1. **Placement honesty** — “constructed in place” should become a reviewable claim, not a hunch.
2. **Constructor-family truth** — users should be able to see whether they are in a Rust by-value lane, a pinned-initialization lane, a C out-pointer lane, or a C++ constructor lane.
3. **Address-commit receipts** — code review should be able to see exactly when movement stops being allowed.
4. **Failure-cleanup evidence** — fallible initialization should say what stays initialized, what is destroyed, and who owns cleanup.
5. **Migration safety** — teams need a compact way to compare “current macro/crate approach” versus “future language support” without pretending those are already equivalent.
6. **Casebook portability** — maintainers should be able to hand realistic examples to reviewers, upstream compiler/lang teams, or downstream adopters.

# Persona / who it’s for

- maintainers of pin-heavy libraries and wrappers
- Rust-for-Linux and embedded maintainers
- Rust/C/C++ interop authors
- async/runtime contributors exploring caller-provided storage
- reviewers of unsafe construction abstractions

# Users & user stories

- **Kernel-facing maintainer**: “Show that this C out-pointer value becomes pinned at creation and never takes a stray memcpy hop.”
- **C++ interop author**: “Compare a `moveit`/`Ctor` constructor lane against a plain Rust by-value lane and make the semantic gap visible.”
- **Library author**: “Record whether our large boxed value is really built in its final allocation or still stack-bounced first.”
- **Reviewer**: “I need one compact artifact for address commit, partial-init behavior, and transition risk instead of a long unsafe-code debate.”
- **Language experimenter**: “Bundle realistic cases showing what today’s crates need from future language support.”

# Prior art (and why it’s insufficient)

- The 2025H2 goal explicitly says multiple external crates already implement in-place initialization with macros, but the goal is to learn from them and choose a language direction.
- `pin-init` already provides safe initialization of pinned data structures, `PinUninit`, pointer-init traits, and helpers like `Rc::pin_with` / `Arc::pin_with`.
- `moveit` already provides `New`, `CopyNew`, and `MoveNew` around `Pin<&mut MaybeUninit<T>>`.
- Crubit `ctor.rs` explicitly compares itself against `moveit`, `pin-init`, and the upstream in-place-init proposal, and documents that it only allows pinned initialization.

What remains missing is a **review-artifact layer** above those tools.
Those crates help *do* initialization. This crate would help other people *understand what happened and what it means*.

# Design goals

1. **Receiver-facing truth first** — optimize for what downstream reviewers and adopters need to know.
2. **Proposal-neutral** — useful before and after language stabilization.
3. **Address-commit explicitness** — never leave “when pinning really begins” implicit.
4. **Failure honesty** — cleanup and partial-init edges are first-class, not footnotes.
5. **Interop-grade language** — C out-pointers and C++ constructors must be modeled directly.
6. **Portable casebooks** — every claim should be exportable as a small bundle.

# MVP surface

- Minimal types: `InitProfile`, `PlacementTopologyReceipt`, `ConstructorLaneReport`, `AddressCommitReceipt`, `FailureCleanupReport`, `InitTransitionDiff`, `InitSupportBundle`
- Minimal functions:
  - `capture_topology()`
  - `classify_constructor_lane()`
  - `capture_address_commit()`
  - `capture_failure_cleanup()`
  - `diff_init_strategy()`
  - `write_bundle()`
- Feature flags:
  - `pin-init`
  - `moveit`
  - `ffi`
  - `serde`
  - `cargo`
  - `casebook`

# Compatibility story

- Works above `pin-init`, `moveit`, Crubit `Ctor`, and local out-pointer adapters.
- Should remain useful if the final language design differs from today’s crates.
- Can record “future language-aligned” strategies as provisional without declaring them equivalent.
- Must degrade honestly when some placement or cleanup facts cannot be observed automatically.

# Conformance & fixtures

- large heap value created in final allocation rather than via stack bounce,
- C out-pointer constructor that must pin immediately,
- C++ constructor lane that is not the same as Rust memcpy move,
- field-embedded pinned value that has both inner and outer address-commit moments,
- caller-provided storage for `async fn in dyn Trait` style futures,
- release drift when a constructor family changes.

# Path to boring stability

- stabilize a tiny artifact vocabulary first,
- keep constructor-family taxonomy intentionally small,
- treat uncertain or inferred topology as caveated output,
- and prefer realistic scenarios over abstract type theory in the first versions.

# Scorecard

- Impact: 5/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A crate and cargo subcommand that compare one case across two initialization strategies, emit a placement-topology receipt, an address-commit receipt, a failure-cleanup report, and a portable bundle.

# De-risk plan

1. Start with **observation and comparison**, not code transformation.
2. Pilot on one real large-heap case and one real pinned out-pointer case.
3. Keep address-commit and cleanup fields tiny and explicit.
4. Add language-proposal adapters only after the receipt vocabulary proves useful.

# Non-goals

- Not a new language feature.
- Not a replacement for `pin-init`, `moveit`, or Crubit.
- Not a theorem prover for initialization soundness.
- Not a universal macro for all constructor styles.

# Architecture & API sketch

```rust
pub struct AddressCommitReceipt {
    pub case_id: String,
    pub final_allocation_site: String,
    pub constructor_lane: String,
    pub pin_begins_at: Option<String>,
    pub move_forbidden_after: Option<String>,
    pub caveats: Vec<String>,
}

pub fn capture_topology(profile: &InitProfile, case: &InitCase) -> Result<PlacementTopologyReceipt>;
pub fn classify_constructor_lane(case: &InitCase) -> ConstructorLaneReport;
pub fn capture_address_commit(case: &InitCase) -> Result<AddressCommitReceipt>;
pub fn capture_failure_cleanup(case: &InitCase) -> FailureCleanupReport;
pub fn diff_init_strategy(old: &InitBundle, new: &InitBundle) -> InitTransitionDiff;
pub fn write_bundle(bundle: &InitSupportBundle, out: &std::path::Path) -> Result<()>;
```

Bundle draft: `init-profile.toml`, `placement-topology.receipt.json`, `constructor-lane.report.json`, `address-commit.receipt.json`, `failure-cleanup.report.json`, `init-transition.diff.json`, `notes.md`.

# Security / safety model

- Never silently treat “currently seems pinned” as proof of an address-commit boundary.
- Preserve exact constructor-family classification and caveats in every receipt.
- Keep partial-init / cleanup uncertainty visible.
- Support redaction of proprietary headers, paths, or generated fragments in export bundles.

# Maintenance & governance plan

- Track Rust language work on in-place initialization, field projections, and reborrowing without binding core artifacts to unstable syntax.
- Keep adapters thin and data-driven.
- Maintain a small public casebook of kernel, C++, heap-large-value, and async examples.
- Encourage ecosystem adapters instead of one monolithic execution engine.

# Milestones

## 0.1
- one placement topology receipt
- one address-commit receipt
- one failure-cleanup report
- one comparison bundle

## 0.2
- constructor-lane comparison
- release drift diff
- CI helpers
- richer field-embedding scenarios

## 1.0
- stable artifact schema set
- public casebook
- adapters for `pin-init`, `moveit`, and Crubit `Ctor`

# Open questions

- What is the smallest constructor-family taxonomy that still helps reviewers?
- Which placement facts can be captured automatically versus maintainer-declared?
- How should caller-provided storage for async trait-object returns be represented without overcommitting to one language design?
- When should a strategy change count as “semantic drift” versus mere refactoring?

# Sources

- Rust in 2026 flagships: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- In-place initialization goal: https://rust-lang.github.io/rust-project-goals/2025h2/in-place-initialization.html
- Reborrow traits goal: https://rust-lang.github.io/rust-project-goals/2025h2/autoreborrow-traits.html
- `moveit` docs: https://docs.rs/moveit/latest/moveit/
- `pin-init` docs: https://docs.rs/pin-init/latest/pin_init/
- Crubit `Ctor`: https://github.com/google/crubit/blob/main/support/ctor.rs
- “Initialization in Rust with pin-init” handout: https://lpc.events/event/19/contributions/2018/attachments/1769/3837/handout.pdf
