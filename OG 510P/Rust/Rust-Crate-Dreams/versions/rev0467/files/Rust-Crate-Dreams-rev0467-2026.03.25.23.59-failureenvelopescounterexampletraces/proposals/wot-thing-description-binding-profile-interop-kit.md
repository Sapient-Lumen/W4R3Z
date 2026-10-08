---
id: P-0394
title: WoT Thing Description, Binding & Profile Interop Kit — TD locks, affordance replay, and profile-aware evidence bundles
status: idea
domains: [iot, web-standards, interoperability, validation, semantics, edge]
last_reviewed: 2026-03-06
evidence:
  - https://www.w3.org/TR/wot-thing-description-2.0/
  - https://www.w3.org/TR/wot-binding-registry/
  - https://www.w3.org/groups/wg/wot/publications/
  - https://github.com/wot-rust/wot
  - https://github.com/WebThingsIO/webthing-rust
---

# Problem

W3C Web of Things now has a serious standards surface: Thing Description 1.1 is a Recommendation, Thing Description 2.0 is underway, binding guidance exists, and profile/discovery work continues. Rust also has meaningful substrate in `wot`, `wot-td`, and the WebThings server implementation.

But the persistent failures are still concentrated at the seam between:

- **what a Thing Description says an affordance means and what an implementation actually exposes on the wire**,
- **JSON-LD / semantic model correctness and protocol-binding correctness**,
- **profile/core assumptions and vendor- or deployment-specific binding details**,
- **migration from TD 1.1-era expectations toward TD 2.0/profile work**,
- and **bugs that currently sound like “works with this dashboard but not that gateway” with no portable replay artifact**.

The missing Rust contribution is not another device SDK or gateway. It is a **TD/binding/profile interop kit** that makes affordance correctness, profile locks, and cross-stack evidence portable.

# What it provides

- `wot.lock` — pins TD version, context/profile assumptions, binding-registry snapshot, security-scheme expectations, and redaction policy.
- `td-ir` — normalized representation of Things, Thing Models, affordances, forms, operations, schemas, and security metadata.
- `affordance-replay` — a tiny replay format for read/write/invoke/observe interactions tied back to TD expectations.
- `binding-diff` — explains mismatches between declared forms/bindings and observed behavior.
- `cargo wot-evidence` — emits `*.wotbundle.zip` with lockfile, normalized TD/TM documents, replay traces, diffs, and notes.

# What the crate should provide other people

1. **A boring artifact for WoT interoperability bugs**.
2. **Version- and profile-pinned TD evidence**.
3. **Binding-aware diffs** that show where implementations diverge from declarations.
4. **A small replay corpus** for gateways, digital twins, and device adapters.
5. **A coordination layer above existing Rust WoT crates**, not a replacement.

# Persona / who it’s for

- Rust maintainers building WoT gateways, twins, device bridges, or validators
- Teams integrating heterogeneous devices through WoT metadata
- Implementers migrating across TD/profile revisions
- Test engineers who need reproducible affordance-level evidence

# Users & user stories

- **Gateway author**: “Show whether this bug is in the TD, the binding metadata, or the device behavior.”
- **Validator maintainer**: “Pin the exact profile and binding-registry assumptions used for conformance.”
- **Device integrator**: “Compare the declared affordance model with what the HTTP/MQTT/CoAP endpoint actually does.”
- **Standards contributor**: “Capture a migration issue without requiring the original device network to stay online.”

# Prior art (and why it’s insufficient)

- W3C publishes the normative TD surface and the WoT publication stream now includes profile and binding work.
- Rust crates can already parse/serve WoT descriptions and expose Web Thing servers.

What Rust still lacks is a **shared evidence format** for TD locks, binding-registry assumptions, affordance replay, and profile-aware diffs.

# Design goals

1. **Semantics plus wire behavior** — not just schema validation.
2. **Version-aware** — make TD 1.1/2.0 and profile assumptions explicit.
3. **Binding-aware** — observed operations must be connected back to declared forms.
4. **Privacy-preserving** — device identities and payloads may need redaction.
5. **Adapter-first** — integrate with existing Rust crates and gateways.

# MVP surface

- Minimal types: `WotLock`, `ThingBundle`, `AffordanceReplay`, `BindingDiff`, `WotEvidence`
- Minimal functions:
  - `normalize_td()`
  - `capture_affordance_replay()`
  - `diff_bindings()`
  - `write_bundle()`
- Feature flags:
  - `td`
  - `thing-model`
  - `replay`
  - `bindings`
  - `redaction`

# Compatibility story

- Adapts `wot` / `wot-td` style metadata rather than replacing them.
- Works with live devices, simulators, or captured protocol traces.
- Keeps the semantic model and transport observations in the same bundle without flattening them into one layer.
- Supports partial bundles when only metadata or only replay traces are shareable.

# Conformance & fixtures

- Goldens for malformed forms, operation mismatches, security-scheme drift, profile violations, and observe-property/event quirks.
- Tiny fixtures for HTTP, CoAP, and MQTT-style affordance behavior.
- Public sample TD/TM corpus with replay traces and expected findings.
- Binding-registry snapshot tests so future revisions remain comparable.

# Path to boring stability

- Stabilize `wot.lock` and the affordance replay schema first.
- Keep the first release focused on TD normalization, replay, and binding diffs.
- Treat profile overlays and vendor quirks as explicit packs, not implicit defaults.
- Avoid building a full device-management platform.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 3/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 4/5
- **Total: 23/30**

# Minimum lovable MVP

A library and CLI that normalize a Thing Description, pin profile/binding assumptions, capture a handful of affordance interactions, compute binding diffs, and emit compact `*.wotbundle.zip` artifacts.

# De-risk plan

1. Start with TD normalization and read-only affordance replay.
2. Keep protocol adapters shallow and opt-in.
3. Snapshot binding assumptions explicitly instead of hard-coding them.
4. Delay broad discovery/profile automation until the evidence format is stable.

# Non-goals

- Not a full IoT gateway.
- Not a digital-twin platform.
- Not a replacement for device SDKs.
- Not a cloud control plane.

# Architecture & API sketch

```rust
pub struct WotLock {
    pub td_revision: String,
    pub profile_pack: String,
    pub binding_snapshot: String,
    pub security_profile: Vec<String>,
}

pub fn normalize_td(input: &str) -> Result<ThingBundle>;
pub fn capture_affordance_replay(input: ReplayInput) -> Result<AffordanceReplay>;
pub fn diff_bindings(td: &ThingBundle, replay: &AffordanceReplay) -> BindingDiff;
```

Bundle draft: `wot.lock`, `thing.json`, `thing-model.json`, `replay.json`, `binding-diff.json`, `redaction-map.json`, `notes.md`.

# Security / safety model

- Support payload truncation, hashing, and identity redaction for devices and endpoints.
- Treat externally supplied TD/TM documents as untrusted input.
- Record which profile and binding assumptions were applied by the tool.
- Keep replay traces bounded so bundles remain CI- and bug-report-friendly.

# Maintenance & governance plan

- Keep the core about locks, normalization, replay, and diffs.
- Version binding/profile packs independently.
- Publish a small public corpus tied to concrete W3C publications and snapshots.
- Resist pressure to absorb generic gateway/runtime concerns.

# Milestones

## 0.1
- TD normalization
- lockfile format
- binding diff prototype

## 0.2
- affordance replay
- profile overlays
- public fixtures

## 1.0
- stable `*.wotbundle.zip`
- documented compatibility policy across TD/profile evolution
- adapter maturity for multiple protocol bindings

# Open questions

- How should TD 1.1 versus 2.0 migration be represented in one stable lockfile?
- Which binding-registry details are essential to pin for reproducibility?
- How much observed wire data is needed before a replay trace stops being useful and starts being too sensitive?

# Sources

- WoT Thing Description 2.0 FPWD: https://www.w3.org/TR/wot-thing-description-2.0/
- WoT Binding Registry: https://www.w3.org/TR/wot-binding-registry/
- WoT Working Group publications: https://www.w3.org/groups/wg/wot/publications/
- `wot` Rust project: https://github.com/wot-rust/wot
- `webthing-rust`: https://github.com/WebThingsIO/webthing-rust
