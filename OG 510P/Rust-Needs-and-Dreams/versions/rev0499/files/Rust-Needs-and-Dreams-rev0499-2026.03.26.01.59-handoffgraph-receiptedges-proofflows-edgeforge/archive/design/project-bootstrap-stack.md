# Design note: Project Bootstrap Stack (Adoption Decision + Starter Pack + Workspace Environment)

## Goal
Define the thin execution bridge that turns a **Rust adoption recommendation** into a **reviewable starter repo** plus a **realized workspace environment** without flattening those layers into one fake “template” verdict.

This note exists because the archive already has strong notes for:
- choosing Rust or a crate lane (`design/adoption-decision-stack.md`),
- realizing a starter repo (`design/starter-pack-kit.md`), and
- realizing a workable local/editor/CI environment (`design/workspace-environment-stack.md`).

What is still missing is the explicit bridge between them.

## Read with
- `design/adoption-decision-stack.md`
- `design/starter-pack-kit.md`
- `design/workspace-environment-stack.md`
- `design/canonical-learning-stack.md`
- `design/package-admission-stack.md`
- `design/ecosystem-atlas-kit.md`

## Why this seam matters now
- Rust’s 2025 vision work says the ecosystem still needs better help navigating crates.io and clearer advice on a good “starter set” of crates. That means the problem is not just package search; it is **turning a recommendation into a responsible beginning**.
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- The 2025 State of Rust survey says documentation remains canonical while more learning and navigation are now mediated by editors and LLM-like workflows. That raises the value of machine-usable, refreshable bootstrap artifacts instead of one-shot README folklore.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo’s current development work explicitly keeps plugins important and is actively discussing workspace/config discovery. Cargo is not trying to become the whole answer, but it is creating better seams that a thin bootstrap layer can import.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Rust’s 2026 flagship goals keep higher-level Rust workflows live through `cargo script`, public/private dependencies, SBOM-adjacent work, and related adoption-facing improvements.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- `cargo new` remains intentionally simple, while the ecosystem already contains many domain bootstrappers. The missing contribution is therefore not “yet another generator” so much as an **honest composition layer above multiple generators and starter sources**.
  https://doc.rust-lang.org/cargo/commands/cargo-new.html
  https://docs.rs/crate/cargo-generate/latest

## Problem statement
Today, Rust teams often blur five different activities together:
1. deciding whether Rust is appropriate;
2. choosing an initial crate/lane stack;
3. realizing a repo skeleton;
4. realizing the surrounding development environment; and
5. importing policy, package-review, support, and release posture.

That flattening causes several recurring failures:
- recommendations become hidden inside templates;
- starter repos quietly hard-code toolchain/editor/native assumptions;
- environment facts drift away from repo facts;
- policy and package-admission choices arrive too late;
- assistants and docs start speaking as if a generated working tree were the canonical design.

## Stack claim
A worthy contribution here is a **Project Bootstrap Stack**: a thin control-plane layer that preserves the handoff from **recommendation** to **starter realization** to **environment realization** to **downstream productization/support imports**.

It should not replace Cargo, `cargo new`, framework generators, Dev Containers, Nix, `rust-toolchain.toml`, or starter repos. It should make those pieces composable and reviewable.

## Layer boundaries
### 1) Adoption question and lane choice
Owned by the Adoption Decision Stack.

It answers:
- what problem or product lane is being considered,
- whether Rust is a fit,
- which ecosystem lane or starter family is recommended,
- which alternatives were serious,
- and which evidence justified the choice.

This layer should output a bounded recommendation, not a repo tree.

### 2) Starter realization
Owned by the Starter Pack Kit.

It answers:
- which starter family is being realized,
- which files or workspace shape are canonical,
- which renderer or generator was used,
- what overlays were applied,
- and what remains generated versus hand-owned.

This layer should output starter artifacts and render reports, not claim that the local environment is solved.

### 3) Workspace-environment realization
Owned by the Workspace Environment Stack.

It answers:
- toolchain, component, target, and editor posture,
- native dependencies and service prerequisites,
- secrets posture,
- local versus CI versus remote-workspace differences,
- and what was merely declared versus actually observed.

This layer should output a realized environment view, not pretend it chose the original project lane.

### 4) Downstream imports
Imported from other stacks as needed.

Typical imports:
- package-admission posture,
- support and canonical-learning posture,
- release/productization posture,
- maintenance and compatibility posture.

This layer should remain imported and bounded, not collapsed back into a starter template.

## Artifact family
This stack only needs a small artifact family:
- `bootstrap-question/v0` — what is being started, by whom, and under what constraints
- `bootstrap-plan/v0` — chosen lane, serious alternatives, selected starter family, selected environment posture, and explicit unknowns
- `bootstrap-handoff/v0` — references to adoption, starter-pack, and workenv artifacts plus freshness and owner info
- `bootstrap-check-report/v0` — whether the resulting first-run path actually worked, what remained manual, and where evidence was partial
- `bootstrap-pack/v0` — compact bundle tying the pieces together

Design rule: these are **composition artifacts**, not a new giant substrate.

## What a worthy contribution would look like in practice
### Thin UX surface
A credible contribution would look like:
- `cargo bootstrap plan`
- `cargo bootstrap derive`
- `cargo bootstrap check`
- `cargo bootstrap refresh`
- `cargo bootstrap pack`

or an equivalent companion tool that stays visibly above Cargo rather than pretending to be Cargo canon.

### Inputs
It should accept:
- an adoption brief or atlas lane,
- a selected starter family,
- a selected environment substrate or policy,
- optional org-local overlays,
- and bounded downstream imports.

### Outputs
It should produce:
- a reviewable starter working tree,
- a reviewable environment realization summary,
- a list of unresolved/manual follow-ups,
- freshness/ownership metadata,
- and machine-usable handoffs for docs, CI, editor integrations, or assistants.

### Positive properties
The contribution is worthy when it:
1. makes starter claims auditable instead of folkloric;
2. keeps adoption reasoning visible after repo creation;
3. keeps generator output distinct from canonical design truth;
4. makes environment drift visible early;
5. carries unknowns and partial checks forward instead of hiding them;
6. stays thin enough to wrap multiple existing generators and environment substrates.

## Ranked first execution lanes
### 1. Conservative CLI / internal tool
Best first lane because it minimizes GUI/runtime/native complexity while exercising workspace, docs, CI, and packaging posture honestly.

Expected imports:
- adoption recommendation,
- starter layout,
- workenv toolchain/editor posture,
- package-admission defaults,
- canonical-learning support profile.

### 2. HTTP/service baseline
Good second lane because it stress-tests secrets posture, service dependencies, observability, and deployment-adjacent handoffs.

### 3. Existing workspace / monorepo new component
High leverage because many real teams are not starting greenfield repos; they are inserting a new Rust component into an existing working tree with existing discovery and policy constraints.

### 4. Embedded / `no_std`
Important, but should follow once the archive proves the bridge on less target-specific ground.

### 5. Bounded assistant/editor rendering
Important long-term because editor/assistant mediation is rising, but it should stay last among the first lanes so the archive does not turn “assistant bootstrap” into the primary truth.

## Non-goals
- one universal project template;
- a hidden recommendation catalog;
- a new canonical registry of starters;
- flattening starter realization and environment realization into one output blob;
- treating the generated repo as the only durable truth.

## Failure modes to resist
- **Template absolutism:** acting as if every team should begin from one blessed scaffold.
- **Generator capture:** letting whichever bootstrapper ran last redefine the design.
- **Environment leakage:** hiding native/editor/CI assumptions in starter boilerplate.
- **Policy lag:** postponing package-admission or release posture until after the project has already spread.
- **Assistant canonization:** letting derived assistant/editor summaries replace authored starter facts and bounded checks.

## Practical archive consequence
This seam should now sit just below the top-ranked control-plane band:
- not above Build-State Evidence or Adoption Decision themselves,
- but above most additional narrow starter or environment sub-kits,
- because it operationalizes a live handoff that the ecosystem clearly still lacks.

In other words: the next worthy contribution is probably **not another template**. It is a thin, reviewable `cargo bootstrap` / `bootstrap-pack/v0` layer that turns recommendation into a fresh start without lying about how that start was produced.
