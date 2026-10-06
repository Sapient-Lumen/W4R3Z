# DevShells: “nix-shell / nix develop” parity without mutating the host

DeriveBSD fails as a day-to-day computing environment if it cannot produce **fast, reproducible, project-local dev environments**.

This document defines **DevShells** as a first-class Derive artifact type.

## Goal

- one-command entry into a pinned toolchain + dependency closure
- no host pollution
- explainable and diffable (Spec→Lock→Plan)
- sandboxed by default (hostile code posture)
- optional “Qubes-y” isolation mode for higher assurance

## DevShell as a derived object

A DevShell is not a special case; it is a normal identity chain:

- `devshell.spec` (intent)
- `devshell.lock` (pinned inputs)
- `devshell.plan` (closure + policy + mounts + env)
- `devshell.activation` (ephemeral runtime instance)

**Identity rule:** the Plan digest binds policy decisions, the computed closure, and the sandbox profile the same way other artifacts do.

## Execution modes

### Mode A (default): jail-backed devshell (fast path)
- enter is near-instant if the closure is cached
- closure/store is mounted **read-only**
- project workspace is mounted **writable** (tmpfs or ZFS clone)
- network is **off by default** (policy must grant)
- no secrets by default (credential broker only)

### Mode B (optional): microVM-backed devshell (high isolation)
- same DevShellPlan, different executor
- microVM is disposable; workspace is a disposable disk layer
- file channels are policy-gated (read-only, non-secret)
- useful for untrusted repos, supply-chain-sensitive work, and “run random build scripts” scenarios

## CLI surface (muscle memory)

- `derive develop` — enter the project’s default devshell
- `derive shell <spec|pkgs…>` — ad-hoc devshell
- `derive run <tool> -- <args…>` — run a tool inside the devshell without interactive entry

Optional ergonomics: generate a `direnv`-style hook so projects can auto-enter a DevShell on `cd` without re-evaluating arbitrary code (the hook should call `derive develop` and consume only verified Plan outputs).

Support commands (LLM-friendly):
- `derive devshell plan --json`
- `derive devshell explain --json`
- `derive devshell diff --json`

## Policy defaults

- **deny network** unless explicitly granted
- **deny secrets** unless the DevShell is permitted to call the credential broker for specific operations
- **resource budgets** derived from policy (rctl/racct/cpuset)
- **store view minimization** applies (the devshell only sees its closure)

## Evidence objects

A DevShell activation should emit (at minimum):
- `devshell.plan.json` (digest-bound)
- `devshell.env.json` (the exported environment map)
- `devshell.mounts.json` (read-only store mounts + writable overlays)
- `devshell.sandbox.json` (jail profile / microVM profile)

These allow `derive explain` to answer:
- why is this tool present?
- where did it come from?
- what authority does this devshell have?
- what changed since last time?

## Non-goals (v0)

- “perfectly emulate every Nix feature”
- evaluation-time metaprogramming in the core (frontends may compile to Spec)
- long-lived mutable dev environments

See also: `docs/83-evaluator-minimalism.md`, `docs/79-derive-spec-frontends.md`, `docs/152-store-view-minimization.md`.

Last updated: 2026-02-23
