# Gap: runtime capabilities and least-privilege contracts

## What is missing
Rust now has enough real least-privilege ingredients that the missing contribution is no longer “invent a capability model.”
The missing contribution is a **portable runtime-capability continuity contract**.

Today the ecosystem still lacks a standard way to describe, exchange, diff, and review:
- what runtime authorities a library, app, service, plugin host, or embedded runtime actually expects,
- which powers are declared by maintainers versus inferred by analyzers,
- which scopes or selectors constrain those powers,
- which framework or platform enforcement layers are only candidate outputs versus actually enacted,
- which ambient fallbacks still exist,
- and what evidence exists that deployed posture still matches the declared least-privilege story.

That missing layer matters because Rust already has real capability-oriented building blocks:
- `cap-std` models filesystem and network authority as passed values via `Dir` and `Pool`;
- `ambient-authority` forces APIs that intentionally use ambient authority to take an explicit token;
- Wasmtime documents WASI filesystem access as capability-based;
- Tauri v2 ships capabilities, permissions, and scopes tied to windows/webviews and commands;
- `cargo-capslock` now exists as an experimental Rust capability analyzer;
- `cargo-caps` exists as a second, narrower inference lane based on linked symbols rather than whole-product policy;
- and FOSDEM 2026 material already connects Rust capability analysis to generated seccomp profiles for services.

So the ecosystem no longer lacks ideas about least privilege.
What it lacks is the **review layer above declaration, inference, generation, and enactment**.

Sources:
- https://docs.rs/cap-std/latest/cap_std/
- https://docs.rs/ambient-authority/latest/src/ambient_authority/lib.rs.html
- https://docs.wasmtime.dev/security.html
- https://v2.tauri.app/security/capabilities/
- https://v2.tauri.app/security/permissions/
- https://github.com/rustfoundation/cargo-capslock
- https://github.com/emilk/cargo-caps
- https://fosdem.org/2026/schedule/event/QGCFDA-using_capslock_analysis_to_develop_seccomp_filters_for_rust_and_other_services/
- https://rustfoundation.org/media/strengthening-rust-security-with-alpha-omega-a-progress-update/
- https://blog.rust-lang.org/inside-rust/2026/02/09/project-director-update/

## The current seam is awkward
Rust capability truth is currently split across several non-equivalent lanes:
- **declaration lanes** in APIs and framework configs (`cap-std`, `ambient-authority`, Tauri capabilities, WASI host config),
- **inference lanes** (`cargo-capslock`, `cargo-caps`, future static or dynamic analyzers),
- **generation lanes** (seccomp drafts, container-policy drafts, permission drafts),
- **enactment lanes** (the policy actually attached to the shipped service/app/runtime),
- and **evidence lanes** (deny-path tests, container receipts, logs, CI attachments, support archaeology).

Those lanes are materially useful, but they do not line up automatically.
A service can generate a seccomp policy without proving that Kubernetes used it.
A Tauri app can ship capability files without a portable review artifact that compares them to maintainer claims.
A library can use `Dir` and `Pool` correctly while still exposing ambient helper paths elsewhere.
A dependency analyzer can infer linked capability hints without proving end-to-end runtime authority for the final product.

The result is not that Rust lacks capability-oriented software.
The result is that it still lacks a portable way to say:
- “these authorities are claimed,”
- “these authorities were inferred,”
- “these candidate enforcement artifacts were generated,”
- “this exact enforcement posture was actually enacted,”
- and “these denial / drift checks were exercised.”

## Why this matters
This is bigger than “better sandbox docs.”
It affects:
1. **blast-radius reduction** — a malicious or compromised dependency does less damage when runtime authority is genuinely constrained;
2. **security review** — teams need to know whether code can touch arbitrary files, networks, env vars, processes, host interfaces, or frontend command bridges;
3. **honest product claims** — “sandboxed” often hides whether posture is declared, inferred, candidate-only, or actually enforced;
4. **cross-stack composition** — Policy, Dependency Review, Client App, Extension Productization, Service Productization, and Wasm/host runtimes all want to import runtime-authority truth without re-owning it;
5. **maintainer continuity** — runtime powers are subtle operational truth and easy to lose during maintainer turnover;
6. **incident forensics** — when runtime blast radius changes, teams need durable diffable artifacts rather than memory.

There is also an honesty constraint: a CLI, service, Wasm host, desktop app, plugin host, and embedded runtime do not share one universal permissions model.
A worthy contribution must preserve declared scope and non-goals rather than pretending Rust can standardize “permissions” in one sweep.

## What “good” looks like
A worthy contribution here is **not** another sandbox, permission DSL, seccomp generator, or framework-specific ACL helper.

It is a shared runtime-capability boundary built around:
- `runtime-capability-surface/v0` for subject identity and declared least-privilege intent,
- `authority-profile/v0` for required / optional / delegated / denied / ambient authority classes,
- `scope-profile/v0` for directories, pools, commands, windows/webviews, interfaces, or tenant selectors,
- `delegation-map/v0` for where authority enters, propagates, narrows, widens, or falls back to ambient behavior,
- optional `sandbox-profile/v0` for framework/platform enforcement descriptions,
- optional `cap-inference-report/v0` for analyzer-derived findings,
- optional `sandbox-generation-report/v0` for generated candidate policies,
- optional `cap-enactment-report/v0` for the exact deployed or shipped enforcement posture,
- `cap-check-plan/v0` and `cap-check-report/v0` for allow/deny/drift checks,
- optional `cap-diff-report/v0` for widened powers or enforcement drift,
- and `cap-pack/v0` for CI, security review, release review, and later archaeology.

That would let Rust teams review runtime least-privilege posture as a real product surface instead of a scattered pile of configs, analyzer output, generated drafts, container manifests, and issue-thread memory.
