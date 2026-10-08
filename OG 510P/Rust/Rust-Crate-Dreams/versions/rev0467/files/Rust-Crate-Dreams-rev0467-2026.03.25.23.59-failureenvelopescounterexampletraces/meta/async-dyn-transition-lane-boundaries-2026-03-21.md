# async-dyn-transition lane boundaries — 2026-03-21

This note keeps **P-0458 Async Dyn Transition Kit** from collapsing into adjacent async or trait-system lanes.

## What this lane is for

This lane is for a **reviewable transition contract** over async-trait dyn-dispatch strategies while Rust moves toward native `async fn in dyn Trait`.
It should answer:

- which recipe family a crate uses today,
- what public object surface that recipe implies,
- what allocation/sendability posture rides along with it,
- which tooling interop constraints make the recipe adoptable or fragile,
- and whether future native support is expected to preserve or reopen the public promise.

## Keep this distinct from nearby lanes

### Distinct from `P-0532 Async Runtime Assurance Profile Kit`

`P-0532` is about runtime family, shutdown, allocation posture at runtime, and qualification evidence.
`P-0458` is about trait-object recipe and migration posture above that runtime substrate.

### Distinct from `P-0073 Async Replay Debugger Kit`

`P-0073` is replay/debugging.
`P-0458` is recipe comparison and migration truth.

### Distinct from generic macro/helper crates

`async-trait`, `trait-variant`, `dynosaur`, and `dynify` are substrate.
`P-0458` is the boring review contract above them.

### Distinct from compiler/language milestone tracking

Language stabilization notes are inputs, not the product.
`P-0458` exists because maintainers still need receipts during the transition window.

## Six truths this lane must keep separate

1. **recipe identity** — bridge family or local adapter in use today;
2. **object surface** — dyn-dispatch promise, generated wrapper, or static-only posture;
3. **allocation posture** — boxed, caller-owned, wrapper-owned, or manual review;
4. **send/locality split** — local-only base trait versus generated or manual `Send` variant;
5. **tooling interop** — macro ordering, mocking constraints, canonical imports, or other adoption gates;
6. **native readiness** — expected migration shape when native support arrives.

## Ordinary mistakes future passes must resist

Do not let the archive treat any of the following as interchangeable:

- `trait-variant` send splitting and dyn-dispatch support,
- `async-trait` type erasure and `dynosaur` wrapper generation,
- a `dynify` bridge and an unclassified “local adapter”,
- mock/tooling constraints and recipe semantics,
- native language milestones and present-day migration readiness,
- or allocation posture and object-surface promise.

## Preferred artifact vocabulary

- `dispatch-recipe`
- `allocation-profile`
- `object-surface.diff`
- `tooling-interop.report`
- `native-readiness.receipt`
- `migration.receipt`

If a future pass adds more detail, it should extend one of those objects before inventing a vague new umbrella.
