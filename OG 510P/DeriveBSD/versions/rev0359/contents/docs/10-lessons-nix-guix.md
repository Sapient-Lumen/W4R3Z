# Lessons from Nix and Guix

This document is a **design input**, not a manifesto. It captures where Nix/Guix succeeded, where they hurt, and the actionable responses for DeriveBSD.

## The big successes worth preserving

### 1) The immutable store + explicit graphs
- Coexistence of versions, no global overwrite hazards
- Reliable dependency closure computation
- “What you built is what you run” (when inputs are explicit)

**DeriveBSD response:** Store + closure semantics are non-negotiable. Make them *boring, stable, and inspectable*.

### 2) Binary caches as a first-class accelerator
- Substituters enable speed at scale
- Reuse across machines/CI is transformative

**DeriveBSD response:** caches + signatures + policy are first-class; “trust” must be explicit.

### 3) Atomic system composition / whole-system declarative config
- The “system is a build artifact” idea is enormous
- Rollbacks become normal, not scary

**DeriveBSD response:** one unified story: packages + system closures + generations.

### 4) Powerful introspection
- why-depends, dependency graphs, closure size, etc.

**DeriveBSD response:** ship `explain/why-depends/bisect` early, not later.

## Recurring failure modes (the monster-making patterns)

### A) Multiple overlapping user surfaces
**DeriveBSD response:** enforce the “single workflow” rule:
Spec → Lock → Plan → Build → Install/Activate, everywhere.

### B) “Config is code” complexity explosions
**DeriveBSD response:** default surface is typed data with stable merge semantics.
Allow escape hatches, but keep them explicit, constrained, and linted.

### C) Impurity handling by folklore
**DeriveBSD response:** impurity is *policy*:
- network/time/cpu features are explicit fields in Plan
- recorded in metadata
- included in artifact identity where appropriate

### D) Debuggability gaps
**DeriveBSD response:** every failure emits a reproduction capsule:
- exact Lock + Plan excerpt + sandbox policy + jail recipe (on BSD)

### E) Governance & ecosystem consistency
**DeriveBSD response:** a small set of blessed packaging patterns + lints + continuous migration tooling.

## Additional lessons worth stealing (non-Nix)

### OSTree / rpm-ostree: “deployments are commits”

- treat upgrades as atomic transitions between bootable deployments
- make `status` and `rollback` the *happy path*

**DeriveBSD response:** unify host generations and workload revisions as deployment objects (see `docs/100-deployments-are-commits.md`).

### Bazel / BuildStream: Action Cache + CAS clarity

- action keys derived from inputs/metadata
- action results reference CAS digests

**DeriveBSD response:** push “CAS everywhere” so verification and caching are uniform (see `docs/101-cas-everywhere.md`).

### Spack: pragmatic, signed binary caches for “from-source” ecosystems

**DeriveBSD response:** make caches a replication layer over verifiable objects; keep signing ergonomic (see `docs/109-repo-signing-ux.md`).

### Foreign binaries friction: build a first-class compat story

Nix users often rely on shims/chroots to run prebuilt binaries.

**DeriveBSD response:** provide a policy-governed compat view built from closures, using BSD-native linker mapping (see `docs/105-compat-view-foreign-binaries.md`).


Last updated: 2026-02-23
