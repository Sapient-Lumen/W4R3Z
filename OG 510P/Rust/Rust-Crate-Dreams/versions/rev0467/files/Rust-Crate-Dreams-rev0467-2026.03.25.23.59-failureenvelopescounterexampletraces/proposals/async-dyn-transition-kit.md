---
id: P-0458
title: Async Dyn Transition Kit — dispatch-recipe ledgers, async-trait/dynosaur migration receipts, and future-proof trait-object adoption bundles
status: idea
domains: [async, language, traits, dyn, migration, devtools, runtimes, libraries]
last_reviewed: 2026-03-21
evidence:
  - https://rust-lang.github.io/rust-project-goals/2025h1/async.html
  - https://rust-lang.github.io/rust-project-goals/2026/flagships.html
  - https://rust-lang.github.io/async-fundamentals-initiative/explainer/async_fn_in_dyn_trait.html
  - https://rust-lang.github.io/async-fundamentals-initiative/explainer/async_fn_in_dyn_trait/avoiding_allocation.html
  - https://docs.rs/async-trait
  - https://docs.rs/trait-variant
  - https://docs.rs/dynosaur
  - https://docs.rs/dynify
  - https://docs.rs/mockall/latest/mockall/
---

# Problem

Rust is finally closing one of the most visible gaps in Async Rust: the ability to use `dyn` with traits that contain `async fn` or other return-position `impl Trait` methods. The official roadmap now treats `async fn in dyn Trait` as part of the 2026 async story, and the 2025 async goal already treated it as a concrete implementation track alongside return type notation, pin ergonomics, and generators.

But ordinary maintainers are still stuck in an awkward middle:

- a large body of production code still depends on `async-trait`,
- newer code can combine native async-in-traits with `trait-variant`,
- `dynosaur` offers a concrete bridge for dynamic dispatch over traits using `async fn` or `-> impl Trait`,
- and future language support will not map one-to-one onto every existing proc-macro pattern, object-safety workaround, or allocation strategy.

The missing crate is not “a better async runtime” and not “yet another proc macro for async traits.”

The missing crate is a **transition workbench** that helps teams describe, compare, and review their chosen dynamic-dispatch strategy while Async Rust evolves.

# What it provides

- `async-dyn-plan.toml` — declares the trait family, current dispatch recipe, target toolchain window, allocation policy, and migration intent.
- `dispatch-recipe.json` — records whether a trait uses `async-trait`, native AFIT + `trait-variant`, `dynosaur`, `dynify`, or a local adapter.
- `object-surface.diff.json` — compares what changed in the trait object surface between two approaches.
- `allocation-profile.json` — records whether futures are boxed, buffered, caller-provided, or currently unknown.
- `migration.receipt.json` — captures why a project picked a given recipe, which caveats remain, and what future language work may retire it.
- `native-readiness.receipt.json` — records whether native `async fn in dyn Trait` is expected to preserve the current public promise or trigger a fresh review.
- `tooling-interop.report.json` — records macro-ordering, mockability, and canonical-import constraints that affect whether a recipe is really adoptable.
- `cargo async-dyn plan` — inventory async traits and candidate dynamic-dispatch paths.
- `cargo async-dyn compare` — compare two recipes for one trait family.
- `cargo async-dyn rehearse` — produce a dry-run migration bundle without rewriting code.
- `*.asyncdynbundle.zip` — shareable artifact for design review, library migration planning, or upstream bug reports.

# What the crate should provide other people

1. **A boring comparison artifact** for `async-trait`, `trait-variant`, `dynosaur`, and future native dyn support.
2. **A migration receipt** that explains why a crate is still boxed, macro-backed, or dual-surfaced.
3. **A trait-object design review bundle** maintainers can share across teams and releases.
4. **A way to separate stable user promises from temporary implementation recipes**.
5. **A bridge** between today’s proc-macro ecosystem and tomorrow’s native async dyn story.

# Persona / who it’s for

- maintainers of async libraries with trait-object use-cases
- runtime and service-framework authors
- teams migrating off `async-trait`
- compiler/language contributors who need real-world transition casebooks

# Users & user stories

- **Library maintainer**: “Tell me which of our async traits still rely on `async-trait`, and what a `dynosaur` or future-native path would imply.”
- **Framework author**: “Document where we promise dynamic dispatch and where we only promise static dispatch.”
- **Reviewer**: “Show me whether this migration changed allocation assumptions or only the dispatch recipe.”
- **Language contributor**: “Collect a conservative casebook of object-safety and migration pain from real crates.”

# Prior art (and why it’s insufficient)

- The async roadmap already names `async fn in dyn Trait`, return type notation, and Dynosaur as part of the evolving official story.
- `async-trait` remains the widely used bridge for dynamic dispatch today.
- `trait-variant` gives a useful split between base traits and sendable variants.
- `dynosaur` demonstrates that a more future-aligned bridge is possible.
- `dynify` shows there is also a constructor-style dyn-compatible variant path, which is similar enough to confuse planning but different enough to need explicit recipe identity.
- `mockall` proves that macro ordering and canonical imports are not trivia; tooling interop is part of the real migration surface.

What remains missing is a **maintainer-facing receipt layer** that says: “here is the dispatch recipe we use today, here is why, here is what changes if we migrate, and here are the caveats we still accept.”


## 2026-03-16 fixture-first refresh

This proposal is now stronger for two reasons.

### 1. The official async story is now visibly transition-shaped
The 2026 flagships explicitly keep **`async fn in dyn trait`** and **return type notation** inside the visible **Just Add Async** program.
That means a crate that helps maintainers compare **today’s recipe** against **tomorrow’s native support** is more timely than it looked when first proposed.

### 2. The archive now has a minimal receiver-facing fixture pack
The new fixture pack keeps these artifacts separate:

- `async-dyn-plan`
- `dispatch-recipe`
- `allocation-profile`
- `object-surface.diff`
- `migration.receipt`

That is the right shape because maintainers need to know whether a change altered only the recipe, or also the public promise and allocation posture.

### 3. The first scenarios are intentionally varied
The initial scenarios now cover:

- a common boxed `async-trait` service lane,
- a `trait-variant` send-split lane,
- and a constrained `dynosaur` lane where default heap assumptions are not acceptable.

That makes the proposal more honest about the fact that the missing crate is a **comparison and migration artifact**, not a universal replacement recipe.


## 2026-03-21 productization refresh

This proposal is now stronger because the archive stopped treating it as “some async trait migration helper” and instead treated it like a small support contract crate.

### What the current ecosystem makes explicit

The official 2026 flagships still list **stabilize `async fn in dyn trait`** as a milestone inside **Just Add Async**.
The explainer for `async fn in dyn trait` and its “using dyn without allocation” chapter make it clear that dynamic async dispatch is really about **object surface** and **allocation authority**, not just syntax.
At the same time, current bridge crates are meaningfully different:

- `async-trait` is a type-erasure path that keeps dyn support available today;
- `trait-variant` is a send-split and return-bound specialization path, not a dyn-trait solution by itself;
- `dynosaur` creates wrapper types that take the place of `dyn Trait` for async or `-> impl Trait` methods;
- `dynify` generates dyn-compatible variants with a constructor-style bridge;
- `mockall` documents compatibility constraints that turn macro composition into a real adoption gate.

That means the missing crate is not another bridge recipe.
It is the **boring comparison and migration contract above those recipes**.

### Additional review objects that should now stay first-class

The archive should now keep at least these truths separate for **P-0458**:

1. **recipe identity** — `async-trait`, `trait-variant`, `dynosaur`, `dynify`, local adapter, or mixed family;
2. **object surface** — whether the public promise actually includes dyn dispatch, generated wrappers, or only static dispatch;
3. **allocation posture** — boxed futures, caller-owned buffers, wrapper-owned storage, or unknown/manual review;
4. **tooling interop** — mockability, macro ordering, canonical import requirements, and comparable downstream ergonomics;
5. **native readiness** — whether future native support is expected to preserve the current promise or reopen the public-surface review.

### Resulting `0.1` direction

A worthy first implementation should export compact receipts for **recipe**, **allocation**, **tooling interop**, **object-surface drift**, and **native-readiness posture** before it attempts any codemod or rewrite ambitions.

# Design goals

1. **Recipe-first** — model dispatch strategies explicitly instead of hiding them in macros.
2. **Migration-safe** — compare approaches without rewriting code by default.
3. **Allocation-honest** — boxed, caller-owned, or wrapper-owned storage must be visible in receipts.
4. **Interop-aware** — macro ordering, mock support, and recipe-specific tooling constraints must not be hidden in footnotes.
5. **Future-aware, not future-assuming** — stay useful before and after native async dyn support stabilizes.
6. **Trait-family focused** — support grouped traits and generated variants, not just one trait at a time.

# MVP surface

- Minimal types: `AsyncDynPlan`, `DispatchRecipe`, `ObjectSurfaceDiff`, `AllocationProfile`, `NativeReadinessReceipt`, `ToolingInteropReport`, `AsyncDynReceipt`, `AsyncDynBundle`
- Minimal functions:
  - `inventory_traits()`
  - `classify_recipe()`
  - `compare_recipes()`
  - `render_receipt()`
  - `write_bundle()`
- Feature flags:
  - `cargo`
  - `serde`
  - `async-trait`
  - `dynosaur`
  - `dynify`
  - `trait-variant`
  - `mockall`

# Compatibility story

- Works before native `async fn in dyn Trait` stabilizes by treating current recipes as explicit strategies.
- Can remain useful after stabilization because teams will still need migration receipts and dual-support windows.
- Must tolerate macro-generated code and partial inference.
- Should preserve “unknown” categories rather than pretending it can fully analyze every proc-macro expansion.

# Conformance & fixtures

- One trait family using `async-trait` with boxed futures.
- One trait family using native async-in-traits plus `trait-variant`.
- One trait family using `dynosaur` for object-safe dynamic dispatch.
- Mixed static/dynamic-dispatch fixtures.
- Goldens for “dispatch recipe changed but public promise did not” and “allocation policy changed”.
- Goldens for “tooling constraints changed but recipe did not” and “native readiness is still manual-review territory”.

# Path to boring stability

- Stabilize the recipe vocabulary before any rewrite or codemod ambitions.
- Start with inventory + comparison + receipt generation.
- Treat macro analysis conservatively.
- Add tooling-interop and native-readiness receipts before codemods.
- Add migration assists only after maintainers trust the receipts.

# Scorecard

- Impact: 5/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 26/30**

# Minimum lovable MVP

A library and cargo subcommand that inventory one workspace’s async trait families, classify each current dispatch recipe, compare one alternative recipe, and emit a `migration.receipt.json` plus compact review bundle.

# De-risk plan

1. Start with read-only inventory and comparison, not code rewriting.
2. Support three concrete recipe families first: `async-trait`, `trait-variant`, and `dynosaur`.
3. Keep allocation reporting explicit and conservative.
4. Validate on one real library with both static and dynamic dispatch needs.

# Non-goals

- Not a new async runtime.
- Not a replacement for `async-trait`, `trait-variant`, or `dynosaur`.
- Not a promise that future native async dyn support exactly matches today’s shims.
- Not a general refactoring framework for all trait-system migrations.

# Architecture & API sketch

```rust
pub enum DispatchRecipeKind {
    AsyncTrait,
    TraitVariant,
    Dynosaur,
    NativeOnly,
    Unknown,
}

pub fn inventory_traits(root: &Path) -> Result<Vec<AsyncTraitInventory>>;
pub fn classify_recipe(inv: &AsyncTraitInventory) -> DispatchRecipeKind;
pub fn compare_recipes(plan: &AsyncDynPlan, inv: &AsyncTraitInventory) -> Result<ObjectSurfaceDiff>;
pub fn write_bundle(bundle: &AsyncDynBundle, out: &Path) -> Result<()>;
```

Bundle draft: `async-dyn-plan.toml`, `dispatch-recipe.json`, `object-surface.diff.json`, `allocation-profile.json`, `migration.receipt.json`, `notes.md`.

# Security / safety model

- Never infer that two recipes are semantically identical without evidence.
- Keep allocation and sendability assumptions visible.
- Record exact toolchain and crate versions used for analysis.
- Support path redaction for exported review bundles.

# Maintenance & governance plan

- Track official async roadmap items and stabilization windows closely.
- Keep recipe adapters thin and declarative.
- Maintain a small public casebook of trait families spanning static and dynamic dispatch.
- Publish interpretation guidance for boxed-future and sendability caveats.

# Milestones

## 0.1
- workspace inventory
- recipe classification
- basic migration receipt

## 0.2
- recipe comparison
- allocation reporting
- bundle export

## 1.0
- stable receipt schema
- public casebook
- CI/report adapters

# Open questions

- What is the smallest useful vocabulary for describing dynamic-dispatch recipes?
- How much proc-macro analysis is worth doing before the tool becomes brittle?
- Which tooling-interop constraints deserve first-class receipts versus free-form notes?
- Which recipe changes matter enough to count as a user-visible migration risk?

# Sources

- Async 2025H1 goal: https://rust-lang.github.io/rust-project-goals/2025h1/async.html
- Rust in 2026 flagships: https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- Async fn in dyn trait explainer: https://rust-lang.github.io/async-fundamentals-initiative/explainer/async_fn_in_dyn_trait.html
- `async-trait`: https://crates.io/crates/async-trait
- `trait-variant`: https://docs.rs/trait-variant
- `dynosaur`: https://docs.rs/dynosaur
- `dynify`: https://docs.rs/dynify
- `mockall`: https://docs.rs/mockall/latest/mockall/
