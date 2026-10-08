
# Async Dyn Transition Kit fixtures

These fixtures exist to make **P-0458 Async Dyn Transition Kit** look buildable instead of merely well-motivated.

The receiver-facing question is:

> what files should another maintainer receive in order to understand which async-dyn recipe a crate is using today, what it promises publicly, and what would change if it migrated?

## Minimal pack for 0.1

- `async-dyn-plan.schema.json` — migration intent, toolchain window, target traits, and redaction defaults.
- `dispatch-recipe.schema.json` — the current recipe (`async-trait`, `trait-variant`, `dynosaur`, local adapter, or unknown), plus object-surface and sendability facts.
- `allocation-profile.schema.json` — where boxing or caller-owned storage enters the picture.
- `object-surface.diff.schema.json` — conservative public-surface and recipe-change diff.
- `migration.receipt.schema.json` — why a team chose a recipe, what caveats remain, and whether manual review is required.
- `tooling-interop.report.schema.json` — mock/proc-macro compatibility constraints that affect whether a recipe is actually adoptable.
- `native-readiness.receipt.schema.json` — whether future native async dyn support is expected to preserve or reopen the current public promise.

## Design rules

- Keep **recipe choice**, **object surface**, and **allocation policy** separate.
- Keep **tooling interop** separate from core recipe semantics.
- Keep **implementation recipe changes** separate from **public-promise changes**.
- Preserve `manual_review_required` and `unknown` as honest outputs.
- Do not silently collapse runtime/executor questions into trait-object transition work.

## Intended first scenarios

1. `async_trait_boxed_service` — a common service trait family that still relies on `async-trait` and boxed futures.
2. `trait_variant_send_split` — a native async-in-traits base trait with a generated sendable variant where the object surface changed only partially.
3. `dynosaur_kernel_no_alloc` — a constrained environment that wants dynamic dispatch without normal heap-allocation assumptions.


## 2026-03-21 productization addendum

The current missing layer is now less about inventing one more bridge and more about publishing:

- one explicit `tooling-interop.report`, and
- one explicit `native-readiness.receipt`.

That keeps “we can compile this today” separate from “we can maintain and migrate this recipe sanely later.”
