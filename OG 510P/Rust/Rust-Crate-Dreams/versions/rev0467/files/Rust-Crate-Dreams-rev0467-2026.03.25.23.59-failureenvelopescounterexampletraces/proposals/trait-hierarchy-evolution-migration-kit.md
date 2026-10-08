---
id: P-0449
title: Trait Hierarchy Evolution Migration Kit — supertrait-split ledgers, Receiver capability maps, and semver-aware migration receipts for evolving library APIs
status: idea
domains: [language, traits, semver, api-design, libraries, devtools]
last_reviewed: 2026-03-07
evidence:
  - https://rust-lang.github.io/rust-project-goals/2025h2/evolving-traits.html
  - https://doc.rust-lang.org/std/ops/trait.Receiver.html
  - https://docs.rs/tower/latest/tower/trait.Service.html
  - https://hackmd.io/%40rust-lang-team/Syx0GQUMT
---

# Problem

Rust is starting to confront an old pain point more directly: once an important public trait ships, evolving its hierarchy is hard.

The current official examples are not toy problems:

- making `Receiver` a conceptual supertrait of `Deref`,
- and splitting a real ecosystem trait like `tower::Service` into a weaker base trait plus a stronger `Sync`-or-`Send` flavored form.

These are the kinds of changes that library authors often *wish* they could make, but avoid because they do not have a good way to estimate who breaks, what blanket impls need to exist, what semver story is plausible, or how to explain the migration to downstreams.

The missing crate is not “trait aliases but in user space.”

The missing crate is a **migration planner** that helps maintainers model trait hierarchy changes before and during adoption.

# What it provides

- `trait-evolution.toml` — declares the current trait surface, proposed split/supertrait shape, and migration policy.
- `capability-ledger.json` — records which types/impls satisfy the old trait, the proposed base trait, and the proposed stronger trait.
- `receiver-map.json` — optional mapping of custom receiver-like types and `Receiver`-relevant capability assumptions.
- `impl-closure.report.json` — shows where blanket impls, forwarding impls, or bridging traits are required to preserve usability.
- `migration.receipt.json` — records semver assumptions, compatibility shims, caveats, and downstream review notes.
- `cargo trait-evolve plan` — analyzes one crate/workspace for hierarchy-split impact.
- `cargo trait-evolve explain` — shows why one impl set is compatible, ambiguous, or breaking under the proposed evolution.
- `*.traitevolve.zip` — shareable artifact for API review, RFC discussion, or release planning.

# What the crate should provide other people

1. **A way to reason about trait evolution before shipping breakage.**
2. **A capability ledger** that distinguishes base-trait and stronger-trait adoption surfaces.
3. **A semver-aware migration receipt** for library teams and downstreams.
4. **A receiver-capability map** for smart-pointer or custom-receiver experiments.
5. **A bridge** between official trait-hierarchy design work and day-to-day library maintenance.

# Persona / who it’s for

- maintainers of foundational Rust libraries
- networking / async library authors using `Service`-like abstractions
- smart-pointer and custom receiver experimenters
- semver and release engineers

# Users & user stories

- **Library maintainer**: “If we split this trait into a weak base and strong subtrait, who breaks and what shims do we need?”
- **Tower-like ecosystem maintainer**: “Model a `LocalService` / `Service` split and attach a receipt to the design review.”
- **Smart-pointer author**: “Show whether our pointer type fits the `Receiver` assumptions we care about.”
- **Release engineer**: “Explain why this migration is additive, caveated, or actually breaking.”

# Prior art (and why it’s insufficient)

- The evolving-traits goal names concrete motivating cases, including `Receiver`/`Deref` and `tower::Service` splitting.
- `Receiver` already exists as a nightly trait.
- `tower::Service` is already a central ecosystem abstraction.

What remains missing is a **planning artifact layer** that helps people model hierarchy changes conservatively instead of debating them only in prose.

# Design goals

1. **Semver-first** — every proposed split should come with an explicit compatibility story.
2. **Capability-ledger oriented** — make impl coverage visible.
3. **Receiver-aware** — smart-pointer and custom receiver cases matter.
4. **Library-centric** — start from ordinary crate maintenance, not abstract trait theory.
5. **Reviewable** — outputs should help humans write RFCs, release notes, and migration guides.

# MVP surface

- Minimal types: `TraitEvolutionPlan`, `CapabilityLedger`, `ReceiverMap`, `ImplClosureReport`, `MigrationReceipt`, `TraitEvolveBundle`
- Minimal functions:
  - `analyze_trait_surface()`
  - `compute_impl_closure()`
  - `build_receiver_map()`
  - `assess_semver_risk()`
  - `write_bundle()`
- Feature flags:
  - `rustdoc-json`
  - `cargo`
  - `serde`
  - `receiver`
  - `diff`

# Compatibility story

- Works on stable source today for planning purposes.
- Treats future language features and hierarchy changes as proposed shapes, not settled facts.
- Can operate in “ledger-only” mode when automatic compatibility assessment is uncertain.
- Should integrate well with public-API and semver tooling rather than replacing them.

# Conformance & fixtures

- A `tower::Service`-style split example.
- `Deref` / `Receiver` conceptual-supertrait example.
- Blanket-impl and forwarding-impl fixtures.
- Goldens for “purely additive”, “needs shim”, “downstream ambiguity”, and “clearly breaking” cases.

# Path to boring stability

- Stabilize the capability-ledger schema before deeper automation.
- Keep semver assessment conservative and explainable.
- Treat receiver-specific logic as an adapter, not core truth.
- Add richer codemod or docs-generation output only after the planning workflow proves useful.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that model one trait split or conceptual supertrait addition, emit an impl-capability ledger, and produce a migration receipt describing shim needs and semver risk.

# De-risk plan

1. Start with modeling and explanation, not code generation.
2. Validate on one real trait family such as `tower::Service`.
3. Keep semver categories few and conservative.
4. Add receiver-specific support only after the base ledger proves useful.

# Non-goals

- Not a new trait-system implementation.
- Not user-space emulation of the final language feature.
- Not a universal semver checker.
- Not a promise that every hierarchy change can be made painless.

# Architecture & API sketch

```rust
pub struct TraitEvolutionReport {
    pub capability_ledger: CapabilityLedger,
    pub impl_closure: ImplClosureReport,
    pub semver_risk: SemverRisk,
}

pub fn analyze_trait_surface(plan: &TraitEvolutionPlan) -> Result<TraitEvolutionReport>;
pub fn compute_impl_closure(plan: &TraitEvolutionPlan) -> ImplClosureReport;
pub fn assess_semver_risk(report: &TraitEvolutionReport) -> SemverRisk;
pub fn write_bundle(bundle: &TraitEvolveBundle, out: &Path) -> Result<()>;
```

Bundle draft: `trait-evolution.toml`, `capability-ledger.json`, `receiver-map.json`, `impl-closure.report.json`, `migration.receipt.json`, `notes.md`.

# Security / safety model

- Never silently classify ambiguous hierarchy changes as safe.
- Keep semver assumptions explicit and versioned.
- Support redaction of proprietary type names in shared bundles.
- Preserve the distinction between observed impl coverage and inferred compatibility.

# Maintenance & governance plan

- Track official trait-hierarchy and receiver design work.
- Keep semver categories compact and data-driven.
- Maintain a public casebook of representative trait-evolution scenarios.
- Publish guidance for library maintainers on interpreting “needs shim” versus “breaking”.

# Milestones

## 0.1
- plan schema
- capability ledger
- semver receipt

## 0.2
- impl-closure report
- receiver map adapter
- bundle export

## 1.0
- stable receipt schema
- public casebook
- report adapters

# Open questions

- What is the smallest useful semver taxonomy for trait evolution?
- How should impl-closure inference handle blanket impls conservatively?
- Which real-world trait families best stress-test the planner?

# Sources

- Evolving trait hierarchies goal: https://rust-lang.github.io/rust-project-goals/2025h2/evolving-traits.html
- `Receiver` trait docs: https://doc.rust-lang.org/std/ops/trait.Receiver.html
- `tower::Service`: https://docs.rs/tower/latest/tower/trait.Service.html
- Implementable trait aliases design meeting: https://hackmd.io/%40rust-lang-team/Syx0GQUMT
