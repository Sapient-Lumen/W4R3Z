# Epic proposal: Runtime Capability Kit

## Thesis
Rust’s ecosystem now has enough real capability-oriented pieces that the higher-leverage missing contribution is no longer “invent another sandbox.”
The missing piece is a **portable runtime-authority continuity contract** that lets teams declare, infer, generate, enact, diff, validate, and ship what their software can actually do at runtime.

In other words: Rust needs a boring, attachable `cap-pack/v0` more than it needs another bespoke permissions language.

## Why now
The ecosystem signals line up:
- `cap-std` already provides explicit filesystem and network authority via `Dir` and `Pool`.
- `ambient-authority` already gives Rust an explicit token for intentional ambient access.
- Wasmtime/WASI already uses a capability-based filesystem security model.
- Tauri v2 already ships explicit capabilities, permissions, scopes, and window/webview binding rules.
- The Rust Foundation’s 2025 security update says Alpha-Omega funding is supporting a Rust-focused implementation of Capslock.
- The January 2026 Project Director update says that capability analyzer has a functioning prototype.
- `cargo-capslock` already exists as an experimental Rust capability-analysis tool.
- `cargo-caps` already exists as a second analysis lane based on emitted linker symbols.
- FOSDEM 2026 material explicitly connects Rust capability analysis to generated seccomp profiles for services.

That means the missing substrate is not raw capability theory.
It is the **reviewable boundary above declaration, inference, generation, and enactment**.

Sources:
- https://docs.rs/cap-std/latest/cap_std/
- https://docs.rs/ambient-authority/latest/src/ambient_authority/lib.rs.html
- https://docs.wasmtime.dev/security.html
- https://v2.tauri.app/security/capabilities/
- https://v2.tauri.app/security/permissions/
- https://rustfoundation.org/media/strengthening-rust-security-with-alpha-omega-a-progress-update/
- https://blog.rust-lang.org/inside-rust/2026/02/09/project-director-update/
- https://github.com/rustfoundation/cargo-capslock
- https://github.com/emilk/cargo-caps
- https://fosdem.org/2026/schedule/event/QGCFDA-using_capslock_analysis_to_develop_seccomp_filters_for_rust_and_other_services/

## What should be built
A first credible version should ship:
1. `runtime-capability-surface/v0`, `authority-profile/v0`, `scope-profile/v0`, `delegation-map/v0`, optional `sandbox-profile/v0`, optional `cap-inference-report/v0`, optional `sandbox-generation-report/v0`, optional `cap-enactment-report/v0`, `cap-check-plan/v0`, `cap-check-report/v0`, optional `cap-diff-report/v0`, and `cap-pack/v0`
2. adapters for common Rust authority models (`cap-std`, `ambient-authority`, Wasmtime/WASI host config, Tauri capabilities/permissions/scopes)
3. analyzer adapters for at least `cargo-capslock` and `cargo-caps`, with explicit completeness and blind-spot reporting
4. docs/reference generation for declared authority classes, scopes, delegation paths, inference posture, candidate enforcement, and enacted posture
5. validation/reporting support for authority drift: new powers, widened scope, new ambient paths, changed analyzer findings, changed generated-policy output, or changed enactment receipts
6. bounded generation support for candidate enforcement artifacts like seccomp or host-policy drafts, with explicit separation between generated and enacted truth
7. release/CI examples showing capability packs attached to services, desktop apps, plugin hosts, Wasm hosts, and internal tool runtimes
8. a ranked pilot program so service and framework lanes prove real consumer value before the ecosystem widens the claim

The winning version is boring, adapter-heavy, and explicit about what it does **not** own.
It should make today’s pieces legible together rather than replacing them.

## Initial pilots
- one service-binary inference pilot centered on `cargo-capslock`
- one declaration-versus-inference pilot comparing maintainer claims to analyzer output
- one generated-enforcement pilot proving seccomp or comparable drafts can be attached without being mistaken for deployment truth
- one enactment-continuity pilot proving deployed/package-level receipts can be attached without claiming universal posture
- one framework-attachment pilot spanning Tauri, Wasmtime/WASI, or a plugin host
- one policy/release integration pilot showing capability artifacts feeding downstream decisions without flattening raw source truth

Treat [`design/runtime-capability-pilot-program.md`](../design/runtime-capability-pilot-program.md) as the ranked execution anchor so runtime-capability work does not jump from abstract schemas straight to overclaimed security promises.

## Success metrics
- Teams can review runtime authority changes as explicit artifacts instead of reading scattered config and code.
- Least-privilege claims remain documented without erasing analyzer disagreement.
- Generated seccomp or permission drafts stop being mistaken for deployment truth.
- Enacted policy receipts stop being confused with abstract framework posture.
- Newly added powers or widened scopes become easier to notice before release.
- Capability posture survives beyond one maintainer or CI setup.
- Rust supply-chain work gains a blast-radius-reduction companion rather than only more registry metadata.

## Archive fit
This proposal fills a real gap between several existing concise-archive kits:
- Compile-Time Capabilities Kit covers build-time execution authority,
- Policy Kit covers decisions,
- Dependency Review covers intake review above imported capability facts,
- Plugin Surface Kit covers extension-point contracts,
- Client App Surface Kit covers broader platform/app behavior,
- Wasm Component Kit covers WIT/package/composition boundaries,
- and Service / Event / Protocol kits cover external interfaces.

None of those is the portable contract for the **runtime authority boundary itself**.
Runtime Capability Kit is the missing substrate that keeps least-privilege posture explicit across libraries, app frameworks, Wasm hosts, plugins, generated enforcement, enacted policy, and security review without absorbing everything into one mega-format.
