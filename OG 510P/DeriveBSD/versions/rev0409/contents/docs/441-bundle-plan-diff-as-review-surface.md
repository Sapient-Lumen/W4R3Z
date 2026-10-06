# Bundle plan diff as a review surface

**Tier:** B (Base)
**Profiles:** A, B, C, D
**Pillars:** reproducibility, supply-chain, operability
**Patterns:** Plan→Receipt, Registry→Diff→Gate, Bundles

DeriveBSD already treats incident/support bundles as first-class evidence:
- selection + transforms are explicit as a typed `bundle.plan`
- produced bytes are bound to that plan via `bundle.build.receipt`

The remaining operator pain point is review ergonomics:
**when bundle plans drift**, reviewers need a compact, stable “what changed?” surface that is gateable by policy.

This doc defines `bundle.plan.diff` as that surface.

## The artifact

- Schema: `spec/bundle.plan.diff.schema.json`
- Example: `spec/examples/bundle.plan.diff.json`

A `bundle.plan.diff` compares two `bundle.plan` objects (by digest) and summarizes:
- window drift (`since/until/max_bytes`)
- include knob drift (shared shape with `incident.bundle` include knobs)
- transform/policy binding drift (redaction + export policy digests)
- output format drift

The diff is deterministic-by-default: the only inputs are the two plan objects (plus optional policy metadata).

## Where it shows up

### Drift bundles (review funnel)

If a host/profile changes the default bundle-plan template (or rotates redaction/export policy bindings), attach:
- the new `bundle.plan` digest
- the old `bundle.plan` digest
- a `bundle.plan.diff` (preferred)

This keeps the review surface stable and makes it easy to gate promotion on high-leverage export posture drift.

### Export receipts

An export flow prefers to cite:
- `bundle.build.receipt` (binds plan → bytes)
- and (optionally) `bundle.plan.diff` when a plan change is the reason for a new export

This makes “why did we export more / different data?” answerable without spelunking logs.

## Typical gates

Bundle plan diffs are posture drift surfaces. Typical gates:
- enabling dangerous include knobs requires explicit approval
- expanding scope (larger window / max bytes) requires review
- changing redaction/export bindings requires at least approval (and two-person integrity in strict profiles)

Policy should treat bundle changes as **killable**: if an adapter lane requires unsafe includes, it must be optional and removable.

## Risk flags

`bundle.plan.diff` may emit canonical `risk_flags` (reason codes for UI + policy). Starter set:

- `bundle-scope-expanded`
- `coredumps-enabled`
- `trace-capsules-enabled`
- `redaction-transform-changed`
- `export-policy-changed`

Gate posture is profile-aware. Defaults commonly treat `coredumps-enabled` and `trace-capsules-enabled` as high-risk (often two-person or block in strict profiles), treat `bundle-scope-expanded` and `redaction-transform-changed` as reviewable drift (often at least approve), and treat `export-policy-changed` as high-leverage egress drift (often two-person in strict profiles).

Last updated: 2026-02-28r161
