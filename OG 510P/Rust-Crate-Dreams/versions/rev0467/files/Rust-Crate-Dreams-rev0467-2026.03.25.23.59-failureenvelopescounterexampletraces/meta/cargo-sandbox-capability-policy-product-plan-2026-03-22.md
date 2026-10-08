# Cargo Sandbox & Capability Policy Kit — product plan (2026-03-22)

## Product thesis

`cargo sandbox-policy` should give maintainers, CI owners, and reviewers one **portable support bundle** for compile-time sandbox policy.
Its job is not to replace Cargo, and not to replace sandbox runtimes.
Its job is to make build-time policy explainable, comparable, and reviewable.

## Who it is for

- maintainers publishing policy for build scripts and proc macros,
- CI and platform teams enforcing no-network / limited-host builds,
- distro and packaging teams using restricted environments,
- editor/tooling authors running compile-time-only workflows,
- release reviewers comparing old and new build-time trust posture.

## Core user promises

1. **I can see which policy source was authoritative.**
2. **I can see which actor got which powers.**
3. **I can tell whether the result came from observe, audit, or enforce mode.**
4. **I can see every break-glass exception and who owns it.**
5. **I can compare two bundles and know what materially changed.**

## 0.1 deliverables

### Library

- policy resolution and normalization,
- typed receipts for policy authority, actor capability scope, enforcement mode, and exceptions,
- import adapters for current practical backends,
- bundle assembly and diffing.

### Cargo subcommand

- `snapshot`
- `doctor`
- `diff`
- `pack`

### Bundle contents

- declared policy,
- normalized effective policy,
- policy-authority receipt,
- actor-capability matrix,
- enforcement-mode receipt,
- exception records,
- imported observation reports,
- policy drift diff,
- human summary.

## First implementation order

1. **Policy authority resolution** from crate/workspace/CI overlays.
2. **Actor-capability capture** for build scripts and proc-macro lanes.
3. **Enforcement-mode capture** with backend granularity honesty.
4. **Exception ownership capture** for break-glass grants.
5. **Diff + pack** once the vocabulary stops moving.

## Success criteria

A user should be able to answer all of these from one bundle without re-running the build:

- which actor actually received filesystem or network access?
- did a workspace or CI overlay outrank the crate’s own manifest?
- was the green result only observe-mode?
- are proc macros isolated individually or only through a shared rustc lane?
- did this release broaden power or only preserve existing policy?

## Anti-goals

- rewriting Cargo,
- inventing a new kernel sandbox,
- promising perfect isolation,
- or auto-solving every build.rs compatibility problem.

## Why this is likely shippable

The crate can deliver value now because the artifact layer does not require Cargo-native sandboxing to be finished.
It can ingest today’s practical tools, document their limits honestly, and serve as a proving ground for the vocabulary that upstream work will still need.
