# Native Deps Kit — ABI and provenance plan (2026-03-23)

This note sharpens **P-0058 Native Deps Kit** around the part most likely to drift into hand-waving:

> When a native dependency resolves, what should the crate say about ABI assumptions, package-manager provenance, vendoring mode, and override handoff?

## Product thesis

The crate should not just say “found library X”.
It should export enough context that another person can review:

- which native contract was declared,
- which backend was tried in what order,
- whether the result came from system packages, vendored source build, vcpkg, or an explicit override,
- and what ABI/linkage assumptions were active.

## Why this is worth doing

### Existing substrate is real, but fragmented

`system-deps` already gives declarative metadata in `Cargo.toml`, and `vcpkg` already gives a configurable discovery path with environment-variable controls and metadata emission. That is enough substrate to build on.

### Silent vendoring is a real design smell

The current `system-deps` standardization discussion calls out additive feature unification around `vendored` as hard to detect, difficult to revert, dangerous in air-gapped or sandboxed environments, and risky from a security and patch-management perspective.

### The ecosystem bar is higher now

Safety-critical and mixed-language adopters need interop surfaces that stay reviewable for years. A native resolution result that does not preserve provenance, mode choice, and ABI hints is not good enough for that audience.

## What the crate should provide other people

### `native-contract.toml`
Declares:
- logical library name,
- version expectation,
- optional feature gating,
- preferred backend order,
- vendoring policy,
- offline/network policy,
- expected link mode if constrained.

### `backend-attempts.receipt.json`
Records:
- backend order attempted,
- relevant env/config observations,
- early exits or disabled backends,
- exact/manual-review-required state.

### `native-resolution.report.json`
Records:
- final selected backend,
- discovered include/lib paths,
- declared vs observed version info when available,
- target and host context,
- next actions when unresolved.

### `abi-provenance.report.json`
Records, conservatively:
- static vs dynamic preference/selection,
- package-manager or source-build origin class,
- explicit override handoff,
- triplet/target flavor when provided by the backend,
- uncertainty fields when the crate cannot actually prove ABI compatibility.

### `resolution-mode.lock.json`
Freezes:
- requested system/vendored/auto/override posture,
- which inputs influenced the result,
- whether the current answer is portable or local-only.

### `consumer-doctor.txt`
A short human guide answering:
- what the crate expected,
- what it tried,
- what this environment appears to be missing,
- and which supported remediation path is most likely.

## Suggested 0.1 command surface

- `cargo native-deps doctor`
- `cargo native-deps explain <crate-or-lib>`
- `cargo native-deps freeze-mode`
- `cargo native-deps check --offline`

## Theory of the crate in practice

### Inputs
- manifest metadata,
- selected Cargo features,
- environment variables,
- host/target information,
- backend-specific probe outputs.

### Processing
- normalize requested mode,
- evaluate backend eligibility,
- probe in declared order,
- record attempts and stop reasons,
- emit resolution and provenance receipts.

### Outputs
- machine-readable receipts for CI and review,
- human-readable doctor guidance,
- stable vocabulary shared with the buildscript stack.

## Guardrails

### Refuse false ABI certainty

If the backend only proves that a library was found, the crate should say that.
It must not claim full ABI compatibility or runtime safety unless it actually has evidence.

### Keep package-manager provenance coarse but honest

The crate can usually classify a result as one of:
- system package / pkg-config route,
- vcpkg route,
- vendored/source build route,
- explicit override route.

That is useful even when it cannot prove deeper distro or supply-chain details.

### Keep override handoff explicit

Cargo override and `links` handoff flows should be recorded as first-class successful routes, not treated as weird exceptions.

## Good first scenarios

- `pkg_config_then_vendored`
- `links_override_handoff`
- `build_internal_env_forces_vendored_mode`
- `feature_unification_forces_vendoring_blocked_by_policy`
- Windows/MSVC vcpkg triplet selection with static vs dynamic mode differences

## Relationship to nearby crates

- **P-0046** explains the build-script run.
- **P-0059** tests build-script behavior under fixtures.
- **P-0058** explains native contract resolution and provenance.

Do not merge them into one blurred “native tooling” crate.

## Sources

- system-deps docs — https://docs.rs/system-deps/latest/system_deps/
- `system-deps` standardization discussion — https://github.com/gdesmott/system-deps/issues/97
- vcpkg docs — https://docs.rs/vcpkg/latest/vcpkg/
- Cargo build scripts reference — https://doc.rust-lang.org/cargo/reference/build-scripts.html
- Call for Testing: Build Dir Layout v2 — https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- docs.rs builds — https://docs.rs/about/builds
- What does it take to ship Rust in safety-critical? — https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
