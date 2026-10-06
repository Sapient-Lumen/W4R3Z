# Flake-style input graphs and registries (Nix lessons)

One of the most successful ergonomic improvements in modern Nix is **flakes**:
a standard project boundary (`flake.nix`) plus a lockfile (`flake.lock`) that pins the full input graph.

Flakes also popularised **URL-like input references** (e.g. `github:org/repo`) and a registry of symbolic identifiers.

DeriveBSD already wants Spec/Lock to be explicit — this is about making *composition* and *discovery* boring.

## DeriveBSD target

### 1) An input graph format that is:
- easy to compose (“imports” without implicit evaluation)
- cache-friendly (inputs are addressable)
- policy-friendly (trust roots and transport restrictions apply uniformly)

### 2) A lock file that:
- pins *every* transitive input by cryptographic identity
- records transport (git, tarball, OCI, etc.) and mirrors
- supports “update one input” without rewriting the world

### 3) A registry mechanism that:
- maps short names to *namespaced* references (not global magic)
- is scoped (project, org, site)
- is mediated by trust policy (no silent redirections)

## Proposed shape

- `derive.spec.json` (typed intent)
- `derive.lock.json` (resolved input graph)
- `derive.registry.json` (optional; site/project mapping)

### Input reference canonical form

A reference is a tuple:
- `scheme` (e.g. `git`, `https`, `oci`, `file`)
- `locator` (URL-ish)
- `identity` (digest / commit / tag+digest)
- `mirrors` (optional list)

The lock file stores the canonicalised reference, plus:
- fetcher identity (versioned)
- normalisation rules applied (e.g., strip VCS metadata)
- content digest of fetched material

## Policy hook points

Trust policy can constrain:
- allowed schemes (no `ssh://` in production)
- allowed registries and name mappings
- required mirror redundancy (availability)
- allowed update windows (anti-freeze)

## Why this belongs in the archive now

Input graph shape is a “compounding decision”:
- tooling, docs, and ecosystem conventions build around it
- changing it later breaks everyone

Bake in the boring pieces early:
- deterministic lock updates
- explicit registries
- clear error modes (“input moved”, “hash mismatch”, “untrusted mapping”)

## References
- nix.dev — Flakes concepts: https://nix.dev/concepts/flakes.html
- Nix reference manual — `nix flake lock`: https://nix.dev/manual/nix/2.18/command-ref/new-cli/nix3-flake-lock
- NixOS Wiki — Flakes overview (URL-like refs, registries): https://wiki.nixos.org/wiki/Flakes

Last updated: 2026-02-25
