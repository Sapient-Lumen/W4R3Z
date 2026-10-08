# Design: Runtime Capability Kit (`cargo capability`, `cap-pack/v0`)

## Goal
Define a portable contract for declaring, inferring, validating, diffing, and reviewing a Rust library or application’s **runtime authority posture**: what external powers it needs, how those powers are scoped or delegated, which analyzers inferred additional powers, which candidate enforcement artifacts were generated, which enforcement posture was actually enacted, and what evidence exists that the least-privilege story still matches reality.

This should **not** replace `cap-std`, `ambient-authority`, Wasmtime/WASI, Tauri capabilities, seccomp tooling, container policies, or OS permission systems.
It should make them compose better and make their posture reviewable.

## References (signals)
- `cap-std` explicitly models external-resource access as passed values, with `Dir` and `Pool` as standout authority-bearing types.
  https://docs.rs/cap-std/latest/cap_std/
- `ambient-authority` explicitly recommends that APIs using ambient authority require an `AmbientAuthority` argument.
  https://docs.rs/ambient-authority/latest/src/ambient_authority/lib.rs.html
- Wasmtime explicitly documents a capability-based filesystem security model for WASI.
  https://docs.wasmtime.dev/security.html
- Tauri v2 explicitly models capabilities, permissions, scopes, and window/webview binding rules.
  https://v2.tauri.app/security/capabilities/
  https://v2.tauri.app/security/permissions/
- The Rust Foundation’s 2025 security update says Alpha-Omega funding is supporting a Rust-focused implementation of Capslock.
  https://rustfoundation.org/media/strengthening-rust-security-with-alpha-omega-a-progress-update/
- The January 2026 Project Director update says the Capslock capability analyzer has a functioning prototype.
  https://blog.rust-lang.org/inside-rust/2026/02/09/project-director-update/
- `cargo-capslock` describes itself as an in-development experimental tool to analyse Rust projects and ascertain which Capslock capabilities they require.
  https://github.com/rustfoundation/cargo-capslock
- `cargo-caps` describes itself as auditing crate capabilities by analyzing emitted linker symbols.
  https://github.com/emilk/cargo-caps
- FOSDEM 2026 material explicitly connects Rust capability analysis to generated seccomp profiles for services.
  https://fosdem.org/2026/schedule/event/QGCFDA-using_capslock_analysis_to_develop_seccomp_filters_for_rust_and_other_services/

## Design principles
1. **Declare powers, not vibes.** “Sandboxed” or “minimal permissions” is not enough.
2. **Separate authority classes from scope selectors.** Filesystem access is different from “only these directories”.
3. **Make delegation visible.** Passed handles/tokens, host grants, and window/webview bindings are part of the contract.
4. **Record ambient escape hatches honestly.** Global cwd, unrestricted process spawn, inherited env, or default network access remain security-relevant.
5. **Separate declaration from inference.** Maintainer claims and analyzer output are related but not interchangeable.
6. **Separate generation from enactment.** A generated seccomp or permission draft is not proof that production used it.
7. **Preserve raw framework truth.** Tauri files, WASI host config, container policy, and broker/sandbox config should remain attachable source artifacts.
8. **Keep examples separate from evidence.** Example configs are not deployment or deny-path proof.
9. **Compose across domains.** The kit must work for libraries, services, desktop apps, plugin hosts, Wasm hosts, and tool/agent runtimes without pretending they share one model.

## Artifact set
### 1. `runtime-capability-surface/v0`
Declares:
- subject identity (crate/app/service/plugin host/runtime)
- authority domains in scope
- high-level least-privilege intent
- security posture summary
- non-goals / intentionally unsupported authority classes

### 2. `authority-profile/v0`
Describes authority classes such as:
- filesystem read/write/create/delete
- network connect/listen/accept
- process spawn / shell / open-with-default-app
- environment read/write
- clock / timer / sleep
- randomness / entropy
- IPC / local sockets / shared memory
- host-interface calls / component worlds / plugin APIs
- device classes or platform permissions where relevant

Each authority should support statuses like:
- required
- optional
- denied by default
- delegated-only
- ambient fallback

### 3. `scope-profile/v0`
Records selectors and limits such as:
- directory roots / glob patterns / preopened bindings
- allowed network pools, hosts, or ports
- allowed process commands / argv constraints
- windows/webviews or frontend bindings
- tenant/plugin namespaces
- WASI worlds or host-interface selectors
- platform-specific permission notes

### 4. `delegation-map/v0`
Shows where authority enters and how it propagates:
- user-granted
- config-provided
- runtime host-provided
- explicitly passed handle/token
- widened / narrowed / transformed
- converted back into ambient behavior
- inherited by child tasks/processes/plugins

### 5. `sandbox-profile/v0` (optional)
Captures the declared or attached enforcement model:
- Tauri capabilities / permissions / scopes
- WASI host config
- OS/container/sandbox policy
- seccomp or brokered syscalls
- framework/plugin-host permission schemes
- org-specific policy engines

### 6. `cap-inference-report/v0` (optional)
Records analyzer-derived capability findings.

Should record:
- analyzer family and version (`cargo-capslock`, `cargo-caps`, future static or dynamic analyzers, manual review)
- capture lane (`callgraph`, `symbol`, `runtime-trace`, `hybrid`, `manual`)
- completeness posture and known blind spots
- authority findings and confidence/reason codes
- disagreements with declared capability posture
- raw attachments or source pointers

Design rule: **inference is an input, not the whole truth.**

### 7. `sandbox-generation-report/v0` (optional)
Records generated **candidate** enforcement artifacts.

Should record:
- generator family and version
- target enforcement kind (`seccomp`, `container-policy`, `tauri-permission-draft`, `wasi-host-config`, etc.)
- assumptions and platform limits used during generation
- lossy conversions or unsupported capability classes
- pointers to generated files
- whether the artifact was only proposed or locally exercised

Design rule: **generated policy is still candidate truth.**

### 8. `cap-enactment-report/v0` (optional)
Records the **actually enacted** enforcement posture.

Should record:
- deployment subject identity (image, chart, bundle, desktop package, runtime host, launcher)
- exact enforcement artifact or config attached
- environment / platform / orchestrator tuple
- how attachment was verified
- known divergence from declared or generated policy
- expiry/freshness posture for the enactment evidence
- raw receipt pointers (manifest snippets, config digests, deployment metadata, packaging receipts)

Design rule: **enactment is separate from both generated candidates and abstract framework posture.**

### 9. `cap-check-plan/v0`
Defines what will be exercised:
- allow-path checks
- deny-path checks
- scope-boundary checks
- authority attenuation/delegation checks
- declared-vs-inferred reconciliation checks
- generated-policy smoke checks where relevant
- enacted-policy verification checks where relevant

### 10. `cap-check-report/v0`
Records:
- which authority claims were checked
- which inference/generation/enactment layers participated
- failures, skips, and unsupported cases
- drift between declared, inferred, generated, enacted, and observed posture
- raw attachments to config, logs, host settings, generated policies, and tests

### 11. `cap-diff-report/v0` (optional)
Summarizes additive or breaking changes:
- newly required authority classes
- widened scopes
- new ambient fallbacks
- changed analyzer findings
- changed generated-policy outputs
- changed enacted policy or verification posture

### 12. `cap-pack/v0`
Bundle for CI artifacts, release review, security review, and long-term archaeology.

## Candidate CLI shape
- `cargo capability init`
- `cargo capability infer`
- `cargo capability generate`
- `cargo capability enact`
- `cargo capability plan`
- `cargo capability run`
- `cargo capability diff`
- `cargo capability pack`

## How it would work in practice
### Capability-oriented library
A library using `cap-std` could:
- declare filesystem and network authority as delegated-only,
- record that `Dir` and `Pool` bound access,
- mark any ambient helper APIs explicitly,
- attach analyzer findings as advisory inference,
- and ship denial-path evidence for traversal or out-of-pool connection attempts.

### Service binary with analyzer + seccomp continuity
A service could:
- declare filesystem/network/process/env posture,
- run `cargo-capslock` and optionally `cargo-caps` as complementary inference lanes,
- generate a candidate seccomp profile in `sandbox-generation-report`,
- attach the actually deployed orchestration or container policy in `cap-enactment-report`,
- and ship evidence showing whether denied syscalls or widened powers were caught before release.

### Wasm host / component runtime
A Wasmtime-based embedding could:
- declare which WASI worlds or host interfaces are enabled,
- record preopened directories and runtime host grants,
- attach host config in `sandbox-profile`,
- and use `cap-enactment-report` only when there is real packaged/deployed host configuration rather than a local example.

### Tauri desktop app
A Tauri app could:
- declare frontend-exposed commands,
- attach permission identifiers and scopes,
- record which windows/webviews receive which capabilities,
- compare declared posture against analyzer or manual review findings,
- and attach the packaged capability/permission bundle that actually shipped.

## Adapters worth building first
- `cap-std`
- `ambient-authority`
- `cargo-capslock`
- `cargo-caps`
- Wasmtime/WASI host configs
- Tauri capability and permission files
- seccomp/container-policy generation hooks for service binaries
- raw attachment readers for container manifests, app bundles, and broker/sandbox configs

## Non-goals
This kit should **not**:
- replace existing sandboxes or permission systems;
- define one universal enforcement engine;
- pretend all authority can be inferred automatically from code;
- treat generated seccomp or permission drafts as proof of deployment;
- own compile-time build-script/proc-macro sandboxing;
- flatten OS, browser, desktop, Wasm, and embedded authority models into one fake ACL.

## Overlap boundaries
- **Compile-Time Capabilities Kit** owns build-time execution authority.
- **Policy Kit** owns policy decisions consuming capability artifacts.
- **Dependency Review Stack** owns dependency-intake review above imported capability facts.
- **Plugin Surface Kit** owns extension-point contracts above runtime authority.
- **Client App Surface Kit** owns broader platform/app behavior beyond permissions.
- **Wasm Component Kit** owns WIT/package/composition boundaries; Runtime Capability Kit can attach host/runtime authority posture.
- **Service / Protocol / Event Surface Kits** own externally visible interfaces, not local authority over files, processes, env vars, or host resources.

## Why this could be high leverage
A good runtime-capability kit would:
- make least-privilege claims explicit and reviewable,
- keep declaration, inference, generated candidates, enacted posture, and checked behavior visibly distinct,
- reduce accidental widening of authority over time,
- give security and platform reviewers one place to inspect power boundaries,
- complement registry and supply-chain work with blast-radius reduction,
- and let Rust’s capability-oriented islands converge without forcing one implementation model.
