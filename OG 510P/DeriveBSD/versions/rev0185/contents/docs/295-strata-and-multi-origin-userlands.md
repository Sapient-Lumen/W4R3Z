# Strata and multi-origin userlands (Bedrock lessons)

Greenfield OSes lose momentum when they require everyone to *port everything* before doing real work.
DeriveBSD already has an adoption bridge (ports/pkg adapters + compat views), but we can push further:

> Make “multiple origins” a **first-class, explainable composition**, not an accidental mess.

Bedrock Linux is a rare prior art example: it treats each coherent set of files as a **stratum**, and processes/files are associated with strata. The point is not “run multiple distros for fun”; the point is **explicit provenance + explicit composition**.

## DeriveBSD target

Introduce a DeriveBSD notion of **stratum** for userland ecosystems:
- a stratum is a signed, versioned, digest-bound *filesystem tree + ABI assumptions*
- strata are composed into a `mount.view` with explicit precedence rules
- the chosen stratum stack is recorded in evidence (so “where did this binary/library come from?” is answerable)

Strata can represent:
- DeriveBSD base sets (kernel/userland/toolchain as sets)
- FreeBSD pkg-derived trees (adapter output)
- ports-derived trees
- vendor runtimes (e.g., a pinned SDK/runtime)
- “foreign userlands” (e.g., Debian-ish tree inside a microVM)

## Composition rules (avoid chaos)

### 1) No silent mixing

A process must run with an explicit *stratum stack*.
If it tries to resolve a dependency outside the declared stack, it fails closed.

### 2) ABI boundaries are named

Each stratum declares:
- libc/rtld expectations
- kernel ABI expectations (or “must run in microVM with kernel X”)
- loader paths / default search paths

This prevents “it happened to work” from becoming a security hole.

### 3) Strata composition is a `mount.view` problem

DeriveBSD already wants a first-class view object (`docs/264-mount-namespaces-and-union-views.md`).
A stratum stack is just a specialized view:
- base root (read-only)
- optional extension strata (read-only)
- explicit writable layers (state datasets, scratch)

### 4) Provenance is not optional

Strata composition should cooperate with:
- origin labels + quarantine metadata (`docs/280-origin-labels-and-quarantine-attributes.md`)
- attribute-indexed metadata + live queries (`docs/293-attribute-indexed-metadata-and-live-queries.md`)

So the system can answer:
- “show me every executable sourced from stratum X”
- “which services are currently running with a foreign stratum stack?”

## Operator ergonomics

- A stratum stack should be selectable in one place:
  - devshells (`derive develop`)
  - compat views (`derive run --compat <stack>`)
  - service manifests (svcdb points at a stack)

- Diffs should show **stratum stack changes** explicitly (blast radius review).

## Why bake this in now

If we postpone this, we risk two failure modes:
1) ad-hoc chroots and hand-mounted trees become “the unofficial standard”
2) adapters silently leak host libraries and ambient authority

A first-class stratum concept forces:
- explicit stacks
- explicit precedence
- receipts tying runtime to policy

## References

- Bedrock Linux concepts (strata as a first-class notion): https://bedrocklinux.org/0.7/concepts-and-terminology.html

Related:
- Compat view for foreign binaries: `docs/105-compat-view-foreign-binaries.md`
- Ports/pkg adapter lane: `docs/108-ports-pkg-adapter-lane.md`
- Mount views as derived objects: `docs/264-mount-namespaces-and-union-views.md`

Last updated: 2026-02-26
