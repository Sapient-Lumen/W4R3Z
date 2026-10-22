# View objects (Plan 9-inspired, capability-mediated)

Goal: import the low-hanging fruit from Plan 9 namespaces **without** ambient authority.

## Concept
A **view** is an explicit object that maps *names* to *capabilities*.
- Views are created/modified only via explicit capability-authorized operations.
- Name resolution is a *pure* operation: `resolve(view, name) -> cap | none`.

This replaces implicit global namespaces with explicit, auditable objects.

## Minimal semantics (v0)
- `view.create(parent_view?) -> view_cap`
- `view.bind(view, name, cap)` (requires write authority to the view)
- `view.mount(view, prefix, other_view)` (composition; optional)
- `view.resolve(view, name) -> cap | none` (no fallback to ambient state)

## Invariants
- **I-VIEW-1 (No ambient resolution):** any name→cap mapping used by privileged code must be obtained via an explicit view object.
- **I-VIEW-2 (No implicit amplification):** binding/mounting cannot create authority beyond the capabilities provided (paired with PO-VIEW-NOAMP).

## Why it is worth it
- shrinks "policy toggles" into explicit objects (supports I-IF-1)
- makes observation/export scoping cheaper (IF-OBS can export a redacted view summary)
- treats name-binding as a protection boundary (name resolution mistakes are protection mistakes)

Refs: REF-BISBEY78.

Evidence hooks
- E1: property tests for resolve purity + no fallback
- E2: model-check small view graphs for "no amplification" and "no unintended aliasing" properties


## Extended semantics (v1 draft) — namespaces that scale

Plan 9’s “per-process namespace” and **union mounts** are a usability superpower: they let you *compose* the world you want to see without turning “the filesystem” into a single shared policy surface. The same idea fits our capability discipline if (and only if) all mutations are explicit and authorized.

### Per-process, copy-on-write namespaces
- Each component starts with a **root view** capability (its “Pgrp” analogue).
- Spawning a child process passes a view cap explicitly; the default is “inherit”.
- `view.clone(view) -> view'` creates a copy-on-write fork of the mapping table.
  - Why: cheap customization + easy “sealed steady-state” (D-SEAL).
  - Audit: mutations to a view SHOULD be transcripted as explicit actions (CH-LOG), so “what names existed when?” is answerable in postmortems.

Suggested additional invariant: make resolution deterministic given the view graph + mutation log (so replay isn’t derailed by “it depends on mount order”).

### Union mounts / overlays (explicit search order)
Allow a **name/prefix** to map to an ordered list of targets (overlay stack):
- `view.bind_union(view, name, [cap1, cap2, ...])`
- `view.mount_union(view, prefix, [viewA, viewB, ...])`

Resolution rule (sketch):
1. Try earlier entries first (left-to-right).
2. Optional: for directory-like objects, expose an explicit “union directory view” that enumerates children in a stable order with shadowing.

Why this matters:
- “overlay policy” lives in the view, not in privileged global configuration.
- It supports “layered composition” patterns (base system + app overlay + ephemeral debug overlay) without needing separate filesystems.

### Service trees as a tooling convention (optional)
Borrow the Plan 9/Inferno lesson that “hierarchical interfaces are easy to inspect and script”:
- A service MAY export a **tree** of capability-bearing nodes (not necessarily byte files).
- Human tooling can adapt the tree into a file-like UI (read/write) **in user space**.
- Optional: a user-space bridge MAY speak a 9P-like protocol to make trees mountable over the network for debugging/operations, but *the protocol endpoint remains just another capability*.

The key discipline: “tree mount” is just `view.bind/mount` under explicit authority; no hidden global mounts.

Reality check: QNX’s “resource manager” model is the same shape (user-space servers attached into a pathname space), and its docs treat name attachment as an explicit, capability-like *ability* (pathspace registration). That’s a useful reminder that “mount/attach” is not just convenience — it’s an authorization surface we should keep explicit, transcripted, and sealable.


## Evidence hooks (incremental)
- Model-check small view graphs for determinism and no-amplification under union semantics.
- Differential tests: compare resolve results across implementations for the same view mutation transcript.
- Performance microbench: resolve overhead with union depth N; define a budget to keep tooling features from leaking into critical paths.
