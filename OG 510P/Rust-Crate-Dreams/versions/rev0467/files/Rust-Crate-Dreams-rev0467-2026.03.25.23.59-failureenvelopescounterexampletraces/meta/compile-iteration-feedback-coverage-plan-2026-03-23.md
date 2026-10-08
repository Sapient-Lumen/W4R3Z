# Compile Iteration Feedback coverage plan (2026-03-23)

## Main judgment

The next implementation-ready slice for **P-0537 Compile Iteration Feedback Kit** is a compact artifact layer for **coverage scope** and **coverage claim ceilings**.

The archive already knows how to say:

- what changed,
- what fast path was theoretically available,
- what surface updated,
- when fresh code became reachable,
- what old code might still survive,
- what generation a route seems to run,
- whether older work has drained,
- and what happened after a live-update attempt.

It still needs an honest answer to a different question:

> what exact routes, libraries, functions, systems, or crates were even under the live-update regime in the first place?

## Why the seam is real now

Current substrate is specific enough to support these artifacts without inventing a new patch engine:

- Dioxus explicitly separates RSX, asset, and Rust hot-patching surfaces and still keeps Rust hotpatch tip-crate-only.
- `subsecond` explicitly limits patching to the tip crate and route-local `call` / `HotFn` participation.
- Chaud explicitly updates `#[chaud::hot]` functions and says its macros are effectively no-ops unless the relevant feature is enabled.
- `hot-lib-reloader` explicitly requires a wrapped dylib interface and documents exported-function limitations such as no generics.
- `bevy_simple_subsecond_system` explicitly limits hotpatching to annotated / preexisting routes and notes common unsupported project shapes.

That means the missing crate can stay receiver-facing and artifact-first.

## Proposed artifacts

### `coverage-scope.receipt.json`

Purpose: describe what live-update support actually covered for one profile or session.

Minimum fields:
- subject
- coverage_classes
- covered_surfaces
- route_basis
- activation_prerequisites
- confidence
- caveats
- manual_review_required

Suggested coverage classes:
- `markup_only`
- `asset_only`
- `tip_crate_only`
- `annotated_functions_only`
- `wrapped_exports_only`
- `preexisting_routes_only`
- `mixed_framework_specific`
- `manual_review_required`

### `coverage-ceiling.report.json`

Purpose: describe what support claims are explicitly out of bounds.

Minimum fields:
- subject
- ceiling_class
- unsupported_claims
- trigger_basis
- fallback_truth
- confidence
- manual_review_required

Suggested ceiling classes:
- `workspace_gap`
- `annotation_gap`
- `wrapper_gap`
- `launch_time_gap`
- `feature_disabled_gap`
- `target_or_runtime_gap`
- `generic_api_gap`
- `manual_review_required`

## What this should provide other people

A worthy crate should give another engineer:

1. one honest answer to what was actually under live-update coverage;
2. one explicit statement of where support claims stop;
3. one separation between “a route updated” and “the whole project is covered”;
4. one separation between framework-specific convenience and portable support truth;
5. one compact bundle that can be attached to issues, framework docs, internal DX guides, or benchmark notes.

## Good first proving grounds

1. **Dioxus three-surface split** — RSX / asset / Rust hotpatch coverage should remain separate.
2. **Subsecond tip-crate + `call` anchor limits** — live-update coverage can be narrower than project structure suggests.
3. **Chaud feature-flag + annotation scope** — macros present in source do not imply active coverage.
4. **hot-lib-reloader wrapped dylib exports** — wrapper surface defines real coverage, not “all code in the repo.”
5. **Bevy simple subsecond route limits** — preexisting annotated systems and unsupported workspace shapes define a clear claim ceiling.

## Non-goals

- Not a replacement for framework-specific hot-reload engines.
- Not a universal source-code instrumentation system.
- Not proof that covered routes are semantically correct after reload.
- Not an excuse to flatten coverage scope into activation, generation, or drain truth.
