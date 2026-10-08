# Compile iteration edit-scope boundaries — 2026-03-23

**P-0537** now needs an explicit boundary note so future revisions do not flatten edit class, patch eligibility, restart ceiling, and state continuity into one fake result.

## Distinct from patch eligibility

`patch-eligibility.report` answers **what strongest route is currently honest**.

`edit-scope.receipt` answers **what the edit actually touched**.

A workflow can know that an edit touched a dependency crate or a struct layout even before it knows whether the strongest current route is hotpatch, relink, restart, or manual review.

## Distinct from reload surface

`reload-surface.report` answers **what the user actually saw update**.

`fast-path-barrier.report` answers **why a stronger claim was blocked**.

A browser page can visibly change while the stronger Rust-logic fast path is still unavailable.

## Distinct from state continuity

`state-continuity.contract` answers **what state survives or resets when a route succeeds**.

`fast-path-barrier.report` answers **why the route narrowed or failed in the first place**.

A route can fail because the edit touched struct layout, and separately succeed later only with full state reinstancing.

## Distinct from linker-route receipts

`linker-route.receipt` answers **how the binary was linked or relinked**.

`fast-path-barrier.report` answers **whether the edit class could benefit from relink only, hotpatch, or neither**.

A faster linker can shrink latency without widening patch eligibility.

## Boundary guardrail

Future passes should reject summaries like:
- “this framework supports hot reload,”
- “the edit was small,”
- “the browser changed instantly,”
- “the linker is faster now,”
- or “state was preserved.”

Those statements can all be true while edit scope, barrier class, and strongest honest fast path remain unresolved.
