# Policy module diff as a drift surface (review policy-code changes)

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** supply-chain, operability, reproducibility
**Patterns:** Registry→Diff→Gate, Bundles

DeriveBSD supports an optional extensibility lane where rich org policy compiles to a **sandboxable Wasm artifact**:
`policy-module` evidence objects bind policy evaluation code to a digest and signature (see `docs/186-policy-modules-wasm.md`).

Policy modules are **high leverage**:
- a module decides admits/denies, approvals, and which evidence is “enough”
- hostcalls are a trust boundary (every hostcall is ambient authority unless brokered)

What was missing was a stable review surface for **policy-code drift**:

> “Did the policy evaluator’s authority surface expand between generations?”

This doc introduces a single, typed diff artifact that makes policy-module changes **bundle-friendly** and **gateable**.

## The artifact: `policy.module.diff`

`policy.module.diff` compares two signed `policy-module` evidence objects (baseline → next) and emits a compact, deterministic summary:

- module digest drift (bytes changed)
- declared entrypoints added/removed
- declared hostcalls added/removed (authority surface)
- declared resource-limit drift (fuel/memory)
- optional canonical `risk_flags` suitable for policy gates

### The artifacts

Schema: `spec/policy.module.diff.schema.json`
Example: `spec/examples/policy.module.diff.json`

### Noise rule (keep this surface stable)

`policy.module.diff` is a **summary** surface.

- It should not embed Wasm bytes.
- It should not embed full source policy.
- Deep inspection belongs in a separate, policy-controlled export (e.g., an offline review bundle) keyed by module digest.

This keeps drift bundles safe and stable while still making “authority drift” visible.

## Where it plugs in

### 1) Drift bundles

When a unit’s active policy module digest changes between generations, attach `policy.module.diff` next to other posture diffs.

See: `docs/395-drift-bundles-and-review-summaries.md` and the canonical registry `docs/430-diff-surface-registry.md`.

### 2) Evidence spine

Policy decisions should be explainable as:

- which policy module digest (and signature) was used
- which inputs were evaluated
- what decision was emitted
- what changed when behavior changes

See: `docs/229-evidence-spine-overview.md`.

### 3) Gates (profile/policy controlled)

Profiles can gate on the summary and/or risk flags:

- hostcalls expanded → require two-person integrity in strict profiles
- limits relaxed → require explicit approval
- entrypoints changed → require a decision-log replay check (optional lane)

Start conservative: treat policy-module changes as reviewable drift by default.

## Risk flags (minimal starter set)

Diff generators should emit conservative flags:

- `policy-module-changed`
- `policy-module-hostcalls-expanded`
- `policy-module-limits-relaxed`

Risk flags are canonical ids from `risk.flag.registry` (`spec/examples/risk.flag.registry.json`).

## References

- Policy modules as Wasm lane: `docs/186-policy-modules-wasm.md`
- Policy engine options + traces: `docs/85-policy-engine-options-and-traces.md`

Last updated: 2026-02-28r173
