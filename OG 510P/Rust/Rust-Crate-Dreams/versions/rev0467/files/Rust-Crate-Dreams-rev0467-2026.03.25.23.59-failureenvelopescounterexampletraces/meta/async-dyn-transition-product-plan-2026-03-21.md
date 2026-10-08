# Async Dyn Transition Kit — product plan (2026-03-21)

This note sharpens **P-0458 Async Dyn Transition Kit** into a more implementation-ready `0.1` shape.

## Core question

If somebody started building **P-0458** this week, what should version `0.1` look like, what should it provide other people, and what should be left for later?

## Main judgment

The first implementation should not become a new bridge macro, a new executor abstraction, or a codemod-first migration bot.
It should provide one boring, reviewable **async dyn transition contract** above today's bridge crates and below future native language support.

`0.1` should make six things first-class:

1. **recipe identity** — `async-trait`, `trait-variant`, `dynosaur`, `dynify`, local adapter, or mixed family;
2. **object surface** — whether the public promise really includes dyn dispatch, generated wrappers, or only static dispatch;
3. **allocation posture** — boxed futures, caller-owned buffers, wrapper-owned storage, or manual review;
4. **send/locality split** — local-only base trait, generated `Send` variant, or mixed family;
5. **tooling interop** — mockability, macro ordering, canonical import requirements, and comparable downstream ergonomics;
6. **native readiness** — whether future native `async fn in dyn Trait` is expected to preserve the public promise or reopen the surface review.

## What `0.1` should provide other people

- one compact `async-dyn-plan.toml`
- one compact `dispatch-recipe.json`
- one compact `allocation-profile.json`
- one compact `object-surface.diff.json`
- one compact `tooling-interop.report.json`
- one compact `native-readiness.receipt.json`
- one compact `migration.receipt.json`
- one compact `async-dyn.summary.md`
- one compact `async-dyn.diff.json`
- one portable review/support bundle

## Commands worth shipping first

- `cargo async-dyn inventory`
- `cargo async-dyn inspect`
- `cargo async-dyn compare`
- `cargo async-dyn doctor`
- `cargo async-dyn bundle`

## What to import, not reinvent

- `async-trait` facts when a trait family is type-erased for dyn support
- `trait-variant` facts when a crate uses send-split generated variants
- `dynosaur` wrapper facts when a generated replacement for `dyn Trait` is in play
- `dynify` variant facts when a dyn-compatible constructor bridge exists
- `mockall` compatibility constraints when macro ordering or canonical imports affect adoption
- official async-fundamentals explainer facts for native-dyn trajectory and allocation assumptions

## Suggested `0.1` doctor warnings

- `recipe_identity_blurred_into_native_future_claim`
- `trait_variant_send_split_masquerades_as_dyn_support`
- `tooling_constraint_missing_for_macro_stack`
- `native_readiness_overclaimed_without_surface_review`
- `allocation_posture_unknown_for_dynamic_path`
- `generated_wrapper_and_boxed_object_surface_collapsed`

## First proving-ground scenarios

1. **A common `async-trait` service lane needs an explicit tooling-interop report because mock support depends on macro ordering and canonical imports.**
2. **A `trait-variant` send split is not the same thing as dyn-dispatch support and needs a native-readiness receipt rather than a future-proofing boast.**
3. **A `dynify` bridge must be named as its own recipe family instead of getting blurred into “local adapter” folklore.**
4. **A constrained `dynosaur` lane may stay blocked on native readiness because allocation and object-surface expectations are part of the public contract.**

## What to leave for later

- automated codemods
- deep proc-macro normalization across arbitrary macro stacks
- universal mock/framework adapters
- whole-ecosystem migration dashboards
- claiming that future native support makes today's recipe receipts obsolete
