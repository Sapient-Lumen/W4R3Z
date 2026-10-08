# Compile iteration feedback — artifact completeness addendum (2026-03-23)

This note exists to make **P-0537** more buildable.

## Main judgment

The proposal already had the right shape, but the fixture pack was incomplete in exactly the places that make cross-framework comparison credible.

The next serious implementation slice should therefore freeze three more review objects:

1. `reload-surface.report.json`
2. `fallback-restart.plan.json`
3. `latency-budget.report.json`

## Why these three matter

### `reload-surface.report.json`

Without this, the lane keeps flattening:
- RSX reload,
- CSS asset refresh,
- frontend HMR,
- Rust logic hotpatch,
- and rebuild/restart

into one fake “live update” claim.

This artifact should answer:
- what changed,
- what route handled it,
- whether Rust recompilation was avoided,
- and what state-touch class is in play.

### `fallback-restart.plan.json`

Without this, the lane can over-celebrate frameworks that are pleasant most of the time while remaining vague about the sharp edges.

This artifact should answer:
- which edit classes force rebuild or restart,
- what reset scope is expected,
- what the operator or tool does next,
- and where manual review still blocks automation.

### `latency-budget.report.json`

Without this, measurements keep mixing together:
- instant visual updates,
- logic-ready hotpatches,
- and restarted-process readiness.

This artifact should answer:
- what the budget was,
- what readiness signal was measured,
- whether the budget passed,
- and whether the comparison basis was direct observation or imported expectation.

## Recommended implementation order

1. stabilize the three schema families;
2. add tiny scenario bundles for Dioxus, Tauri, and Trunk/cargo-leptos adjacent flows;
3. only then add richer adapters, dashboards, or orchestration.

## What the crate should provide other people after this pass

A useful v0.2 should let another engineer inspect one bundle and say:

1. **this was visual-only feedback,**
2. **this one changed Rust logic,**
3. **this edit still forces restart,**
4. **this budget was measured to the browser paint, not to process readiness,**
5. **and this other flow is fast but incomparable because the readiness signal differs.**

That is a much more valuable contribution than another local-only dev command.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2025/09/10/rust-compiler-performance-survey-2025-results/
- https://dioxuslabs.com/learn/0.7/essentials/ui/hotreload/
- https://v2.tauri.app/reference/cli/
- https://book.leptos.dev/interlude_styling.html
