---
id: P-0363
title: OMA LwM2M 1.2 + OMNA Object Registry Conformance & Evidence Kit — object/version locks, bootstrap replay, and device-management bug bundles
status: idea
domains: [iot, embedded, device-management, standards, interoperability, validation, tooling]
last_reviewed: 2026-03-06
evidence:
  - https://www.openmobilealliance.org/specifications/lwm2m/introduction/
  - https://www.openmobilealliance.org/release/LightweightM2M/V1_2_1-20221209-A/HTML-Version/OMA-TS-LightweightM2M_Transport-V1_2_1-20221209-A.html
  - https://www.openmobilealliance.org/specifications/registries/objects/
  - https://github.com/OpenMobileAlliance/lwm2m-registry
  - https://docs.rs/lwm2m-registry
  - https://www.openmobilealliance.org/release/LightweightM2M/ETS/OMA-ETS-LightweightM2M_INT-V1_2-20231003-A.pdf
---

# Problem

Rust has enough LwM2M-adjacent substrate to work with object registries and device-facing integrations, but real interoperability failures still happen at the seam between:

- LwM2M core versus transport-binding assumptions,
- object/version selection from the OMNA registry,
- bootstrap and registration flows,
- server/client expectations about security mode, resource encoding, and reporting behavior,
- and field bug reports that arrive as “device won’t register” or “object mismatch” with no portable evidence bundle.

The missing Rust contribution is not another full client/server stack. It is a **profile-and-evidence workbench** that makes LwM2M failures reproducible, comparable, and small enough to debug.

# What it provides

- `device-lock` — lockfiles pinning LwM2M version, transport bindings, security mode, object versions, resource expectations, and bootstrap assumptions.
- `registry-bridge` — a normalized layer over OMNA object definitions and local overrides.
- `flow-replay` — capture and replay for bootstrap, registration, observe/notify, and selected device-management interactions.
- `lwm2m-diff` — semantic diffs such as “same object ID, different versioned resource contract” or “server accepted registration but rejected later reads due to capability mismatch”.
- `cargo lwm2m-evidence` — emits `*.lwm2mbundle.zip` with profiles, object manifests, normalized traces, and redaction-aware notes.

# What the crate should provide other people

1. **A boring default artifact for LwM2M interoperability bugs**.
2. **Pinned object/version expectations** that survive firmware and server upgrades.
3. **Registry-aware diagnostics** instead of raw path/value dumps.
4. **Replayable bootstrap and registration failures** for CI, vendors, and support engineers.
5. **A bridge from object registries and packet/trace adapters to evidence-grade workflows**.

# Persona / who it’s for

- IoT device and gateway teams using LwM2M for fleet management
- Managed-device platform operators
- Firmware teams debugging bootstrap, registration, and object-model drift
- Test-lab and certification-adjacent teams

# Users & user stories

- **Firmware engineer**: “Tell me whether this breakage is object-version drift, bootstrap policy, or transport/security mismatch.”
- **Platform operator**: “Replay the failing registration against a simulated server profile and compare it with the passing device.”
- **Integrator**: “Pin which OMNA object versions this product line actually supports.”
- **Support engineer**: “Ship a redacted bundle to a vendor without leaking full customer telemetry.”

# Prior art (and why it’s insufficient)

- OMA publishes LwM2M 1.2.x core/transport surfaces, an authoritative object registry, and interoperability test material.
- Rust has useful substrate in `lwm2m-registry` and related object-definition tooling.
- But there is still no boring-default Rust crate for **object/version lockfiles + bootstrap/registration replay + semantic diffs + portable evidence bundles**.

# Design goals

1. **Object-first** — model device capabilities in terms maintainers actually debug.
2. **Version-aware** — object and resource versions must be first-class.
3. **Flow-aware** — bootstrap and registration should be replayable rather than reduced to isolated packets.
4. **Redaction-first** — make shareable bundles safe for production incidents.
5. **Transport-conscious** — record core/transport assumptions explicitly.

# MVP surface

- Minimal types: `DeviceLock`, `ObjectManifest`, `Lwm2mBundle`, `FlowFinding`, `ObjectDiffFinding`
- Minimal functions:
  - `load_registry_object()`
  - `pin_device_profile()`
  - `replay_registration()`
  - `diff_object_contracts()`
  - `write_bundle()`
- Feature flags:
  - `registry`
  - `bootstrap`
  - `observe`
  - `redaction`

# Compatibility story

- MVP should target LwM2M 1.2.x style profiles and clearly document downgrade behavior for older assumptions.
- The crate should complement existing embedded/network stacks rather than replace them.
- Capture/replay adapters can remain optional while the lockfile and report schemas stay neutral.
- Object-definition parsing must be deterministic across local and registry-fed sources.

# Conformance & fixtures

- Tiny object manifests for common objects such as Device, Server, Security, and Firmware Update.
- Cases for object-version drift, missing mandatory resources, unexpected resource types, and bootstrap/security mismatches.
- Goldens for “same path, different object version semantics” and “registration succeeds but later reads fail”.
- Scenario bundles for observe/notify timing and content-format differences.

# Path to boring stability

- Stabilize the lockfile, object-manifest, and bundle schemas before growing the replay matrix.
- Start with object/version validation plus registration replay rather than every interface.
- Keep diagnostics phrased in registry/object terms, not transport internals alone.
- Build a public corpus from small object manifests and synthetic traces.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 3/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 24/30**

# Minimum lovable MVP

A library and CLI that pin the object/version profile for a device, replay a bootstrap or registration trace, and emit a compact `*.lwm2mbundle.zip` with normalized failures and object-aware diffs.

# De-risk plan

1. Start with object/profile validation and registration replay before full observe/write workflows.
2. Treat OMNA object-version handling as the hardest early design problem.
3. Keep synthetic traces and tiny manifests in the initial public corpus.
4. Add richer transport/security adapters only after the lockfile and report model stabilize.

# Non-goals

- Not a new end-to-end LwM2M client/server implementation.
- Not a generic IoT cloud platform.
- Not a replacement for OMA interoperability events or full certification programs.
- Not a device-provisioning control plane.

# Architecture & API sketch

```rust
pub struct DeviceLock {
    pub lwm2m_version: String,
    pub object_versions: Vec<ObjectVersionPin>,
    pub security_mode: SecurityMode,
}

pub fn pin_device_profile(objects: &[RegistryObject]) -> Result<DeviceLock>;
pub fn replay_registration(lock: &DeviceLock, trace: &[u8]) -> Result<Lwm2mReport>;
```

Bundle draft: `profile.toml`, `objects.json`, `bootstrap.trace`, `registration.trace`, `report.json`, `diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Treat traces and registry objects as untrusted input.
- Support redaction of endpoint identifiers, credentials, resource values, and customer metadata.
- Record exact registry/object versions and transport/security assumptions.
- Keep bundle artifacts deterministic enough for support and regression review.

# Maintenance & governance plan

- Keep the core centered on lockfiles, registry-object normalization, findings, and bundle format.
- Version replay adapters separately when necessary.
- Publish a small, public fixture corpus organized around common object/version seams.
- Avoid tying the crate to one vendor cloud or one client/server implementation.

# Milestones

## 0.1
- object manifest loader
- device/profile lockfile
- registration replay report

## 0.2
- bootstrap scenarios
- semantic object diffs
- redaction support

## 1.0
- stable `*.lwm2mbundle.zip`
- public object/version fixture corpus
- documented compatibility policy for supported LwM2M 1.2.x surfaces

# Open questions

- What minimum object corpus is enough to make the bundle format useful in practice?
- How much transport detail belongs in the stable report schema versus optional adapters?
- Which redaction defaults preserve enough evidence without leaking production secrets?

# Sources

- OMA LwM2M introduction: https://www.openmobilealliance.org/specifications/lwm2m/introduction/
- LwM2M 1.2.1 transport bindings: https://www.openmobilealliance.org/release/LightweightM2M/V1_2_1-20221209-A/HTML-Version/OMA-TS-LightweightM2M_Transport-V1_2_1-20221209-A.html
- OMNA object registry: https://www.openmobilealliance.org/specifications/registries/objects/
- OMA LwM2M registry repository: https://github.com/OpenMobileAlliance/lwm2m-registry
- `lwm2m-registry`: https://docs.rs/lwm2m-registry
- OMA LwM2M interoperability test specification: https://www.openmobilealliance.org/release/LightweightM2M/ETS/OMA-ETS-LightweightM2M_INT-V1_2-20231003-A.pdf
