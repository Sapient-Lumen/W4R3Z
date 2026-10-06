# Overlay transforms: Nix overlays, but as deterministic data patches

Nix pros rely on overlays to **surgically change a package set** without forking the universe.
DeriveBSD should offer the same power while keeping the authoritative IR (Spec/Lock/Plan) **diffable, canonical, and signable**.

## Core idea

An **overlay transform** is an ordered, deterministic patch applied to:
- `Spec` (authoring-time changes), and/or
- `Lock` (resolution overrides), and/or
- `Plan` (policy-visible parameter tweaks)

The transform itself is **data**, not executable code.

## Properties

- ordered (later overlays see earlier results)
- deterministic (no IO, no time, no randomness)
- schema-validated
- hashed and bound into the Plan digest (so “what we permitted” includes “what we overrode”)

## Formats

v0 should support **one** patch format to stay small.
Recommended:
- JSON Merge Patch (RFC 7396) for human authoring
- optional JSON Patch (RFC 6902) for tools

Either way, `derive diff --json` should be able to explain:
- which overlay introduced a change
- the exact fields changed
- the downstream consequences (closure / blast radius)

## Common use-cases

- pin a dependency to a different source revision
- apply a patch or flag to one package variant
- replace one package implementation with a local fork
- temporarily disable a feature behind a policy gate

## Relationship to other mechanisms

- **Emergency grafts** (`docs/102-emergency-grafts.md`) are “break glass” transforms.
  Overlays are the normal, reviewable, reusable path.
- **Patchsets** (`spec/patchset.manifest.schema.json`) can package code changes as artifacts.
  Overlays decide *where* a patchset is applied.
- **Policy decision records** must see overlay digests as inputs (authorization binds to the override).

## Non-goals (v0)

- a general-purpose evaluation language inside Derive core
- hidden “impure overlay” hooks

Last updated: 2026-02-23
