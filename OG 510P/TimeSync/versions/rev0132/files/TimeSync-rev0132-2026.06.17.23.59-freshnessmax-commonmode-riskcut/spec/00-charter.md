# 00 — Charter

## Purpose

TimeSync is a design for describing trustworthy time state across heterogeneous timing systems.

It is not a replacement for every time protocol. It is a compact semantic layer that can bridge current mechanisms and future systems by making time uncertainty, operating condition, trust posture, and downstream applicability explicit.

## Primary design constraints

1. Keep the invariant core small.
2. Put sector-specific density into profiles.
3. Add extension hooks only when pressure recurs across more than one demanding boundary.
4. Keep wire claims thinner than local assessed state.
5. Treat profile conformance as scoped local/export metadata, not as a universal compliance label.
6. Avoid global registries, manifests, bundles, or policy lattices until a concrete boundary earns them.

## Reconstruction rule

The rev0060 archive is preserved as research history. The files in `spec/`, `schema/`, `profiles/`, `tests/`, and `examples/` are the reconstructed current answer.

## Review rule

A future change should identify which layer it changes:

```text
core TimeState
extension hook
profile obligation
wire claim
local assessed state
request/result surface
boundary context
profile assessment
profile reference
lifecycle/current-policy overlay
```

Changes that widen the invariant core need stronger evidence than changes that add profile-local obligations or examples.
