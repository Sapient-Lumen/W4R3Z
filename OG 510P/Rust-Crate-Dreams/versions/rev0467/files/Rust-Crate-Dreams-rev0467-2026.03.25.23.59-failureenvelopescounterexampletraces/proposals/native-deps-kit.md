---
id: P-0058
title: native-deps-kit — declarative system dependency management across pkg-config/vcpkg/vendoring
status: idea
domains: [cargo, ffi, build-scripts, packaging]
last_reviewed: 2026-03-08
evidence:
  - https://docs.rs/system-deps/latest/system_deps/
  - https://github.com/gdesmott/system-deps/issues/97
  - https://docs.rs/vcpkg/latest/vcpkg/
  - https://docs.rs/system-deps/latest/system_deps/struct.Config.html
  - https://doc.rust-lang.org/cargo/reference/build-scripts.html
  - https://doc.rust-lang.org/cargo/reference/config.html
  - https://doc.rust-lang.org/cargo/reference/external-tools.html
  - https://rust-lang.github.io/rust-project-goals/2024h2/sandboxed-build-script.html
needs:
  - Make native/system dependencies reproducible and cross-platform without copy-pasted build.rs logic.
  - Provide a single “doctor” UX for developers and CI to diagnose missing libs and misconfiguration.
risks:
  - Competing ecosystems and expectations (vendored vs system vs vcpkg) could fragment adoption.
  - Cross-compilation and distro differences can explode scope without strict MVP boundaries.
---

## Problem

Rust’s `*-sys` / FFI crates frequently rely on imperative `build.rs` scripts that probe for native libraries. Those scripts are commonly copied across crates, rarely tested, and behave differently across platforms. A declarative crate like `system-deps` exists, and `vcpkg` tooling exists, but there isn’t a unified, high-quality “golden path” that:

- standardizes the manifest of native requirements,
- supports multiple discovery backends (pkg-config, vcpkg, vendored),
- produces *explainable* diagnostics,
- makes **system vs vendored vs override** choice explicit instead of hidden in feature unification and env vars, and
- is testable in CI.

## Users & user stories

- **Library maintainers** of `foo-sys`: “I want to declare native deps once and stop maintaining bespoke build.rs boilerplate.”
- **Application teams**: “I need a reliable way to build on Linux/macOS/Windows CI without custom per-platform scripts.”
- **Enterprise/offline users**: “I need a deterministic report of what native deps are required and how to satisfy them.”

## Prior art (and why it’s insufficient)

- `system-deps` provides declarative `pkg-config` integration, but (today) doesn’t solve the full cross-platform ecosystem story (e.g., vcpkg-first Windows/MSVC workflows, vendoring conventions, richer diagnostics, test fixtures).  
  https://crates.io/crates/system-deps  
- `vcpkg` crate + `cargo vcpkg` can build a vcpkg installation from Cargo manifests, but it doesn’t unify with other discovery mechanisms and doesn’t become a standard interface for `*-sys` crates.  
  https://docs.rs/vcpkg  
- Many crates use `pkg-config` build dependency directly; the resulting scripts vary widely.  
  https://crates.io/crates/pkg-config

## Design goals / non-goals

### Goals
- **Declarative inputs**: a consistent manifest schema describing the *native contract* (names, versions, features, link mode).
- **Multiple backends**: `pkg-config` (Unix), `vcpkg` (Windows), and “vendored build” as a first-class option.
- **Great diagnostics**: `doctor` mode that explains what it tried, what it found, and how to fix it.
- **Mode governance**: freeze whether the user or CI requested system-only, vendored-only, auto fallback, or override mode, and explain when feature unification or defaults changed that outcome.
- **Testability**: fixture-based tests for sys crates (simulate pkg-config/vcpkg outputs deterministically).

### Non-goals
- Replace system package managers; the kit should *integrate* and produce actionable instructions, not become a distro tool.
- Promise one universal cross-platform package-discovery story for every OS/package-manager pair.
- Solve every native build toolchain (CMake/Meson/etc.) in v0.1.

## Architecture & API sketch

### Library: `native-deps`
- `NativeDepsManifest`: parsed from `[package.metadata.native-deps]` or `NativeDeps.toml`.
- `ProbeBackend`: trait implemented by `PkgConfigBackend`, `VcpkgBackend`, and `VendoredBackend`.
- `ResolutionModeLock`: compact artifact describing requested mode inputs (features, env, overrides, policy), final allowed mode, and exact/manual-review boundaries.
- `probe(manifest, ctx) -> Result<ResolvedNativeDeps, ProbeError>`:
  - `ResolvedNativeDeps` includes include paths, link search paths, libs, cfg flags, and “explain data”.
  - The result also carries whether resolution happened through system probing, internal build, or override handoff.

### Build-script helper
- `native_deps::emit_cargo_instructions(resolved)` emits:
  - `cargo:rustc-link-lib`, `cargo:rustc-link-search`, `cargo:include=...`, and standardized `cargo:metadata=` keys.

### CLI: `cargo native-deps`
- `cargo native-deps doctor`:
  - prints a structured report (JSON + human) of resolved deps and failures.
- `cargo native-deps explain <crate>`:
  - show the resolution path and the **mode decision** for a specific dependency.
- `cargo native-deps ci`:
  - “fail fast” checks that native requirements are satisfied (with clear failure modes).
- `cargo native-deps freeze-mode`:
  - emits a small `resolution-mode.lock.json` that another human or CI step can review.

## Security / safety model

- Treat external outputs (`pkg-config`, `vcpkg`) as untrusted input: sanitize paths, enforce bounds, and produce reproducible logs.
- Support an “offline mode” where no network fetches are allowed (important for enterprise/air-gapped CI).

## Maintenance & governance

- Ship as a small core crate plus optional backend crates to reduce dependency sprawl.
- Maintain a conformance fixture suite (golden pkg-config outputs; example vcpkg manifests) so behavior is stable across releases.

## MVP milestones

- **0.1**: schema + `pkg-config` backend + `doctor` UX + test fixtures runner.
- **0.2**: `vcpkg` backend + Windows/MSVC docs + “vendored backend” conventions.
- **0.3**: cross-compilation profiles + more ergonomic cargo metadata integration.


## What this crate should provide other people

This crate should provide the missing **native contract** that today is usually buried inside handwritten `build.rs` logic.

Other people should get:

- `native-contract.toml` — declared library names, version expectations, features, preferred backends, link mode, and offline policy.
- `resolution-mode.lock.json` — requested mode inputs (features, env, overrides, policy), final mode, and whether that answer is exact or manual-review-required.
- `vendoring-policy.report.json` — whether vendoring or system-only resolution was allowed, blocked, or forced, and why.
- `native-resolution.report.json` — what backend was attempted, what was found, what was inferred, and what action is suggested.
- `backend-attempts.receipt.json` — ordered probe attempts (`pkg-config`, `vcpkg`, vendored, override) plus observed env/config inputs.
- `consumer-doctor.txt` — short actionable install/help text for developers and CI.

That means downstream users get something much more useful than “build script failed”: they get a reviewable declaration of what native support was promised and how the probe actually behaved.

## 0.1 boundaries

A good 0.1 should:

- start with a manifest layer plus `pkg-config` backend and a strong doctor UX,
- freeze one **mode lock** before or during probing,
- record backend attempts and observed inputs conservatively,
- integrate with existing `links` / metadata conventions rather than replacing them,
- and keep networked or vendored builds opt-in.

A bad 0.1 would try to standardize every native toolchain, subsume system package managers, hide feature-driven vendoring behind “magic defaults”, or promise perfect source-build portability across all platforms.
## Recommended 0.1 crate split

Keep the first release layered:

- `native-contract-core` — manifest schema, normalization, and report types
- `native-contract-mode` — mode lock + vendoring policy evaluation
- `native-contract-pkg-config` — first backend
- later `native-contract-vcpkg` and optional vendored helper crates
- `cargo-native-deps` — doctor / explain / CI-facing interface

This keeps the value centered on the **declared native contract and doctor receipt**, not on becoming a package manager.

## Upstream fit

This crate should prefer low-friction manifest/config integration and treat existing Cargo override/handoff flows as first-class support cases.

That means:

- prefer `package.metadata`-style declaration when possible,
- model `target.<triple>.<links>` override success honestly,
- treat `system-deps` environment controls (`*_BUILD_INTERNAL`, `*_NO_PKG_CONFIG`, `*_LINK`) as substrate rather than as the final support artifact,
- and add value through **mode locks, policy reports, resolution receipts, doctor UX, and backend-attempt truth**, not by replacing Cargo or the OS package manager.
