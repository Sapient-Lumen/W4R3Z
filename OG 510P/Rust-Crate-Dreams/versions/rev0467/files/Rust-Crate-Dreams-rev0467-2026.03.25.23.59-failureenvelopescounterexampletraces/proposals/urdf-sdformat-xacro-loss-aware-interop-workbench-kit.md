---
id: P-0423
title: URDF + SDFormat + xacro Loss-Aware Interop Workbench Kit — robot-description locks, expansion receipts, and simulator-aware diffs
status: idea
domains: [robotics, simulation, cad, xml, portability, evidence]
last_reviewed: 2026-03-06
evidence:
  - https://sdformat.org/
  - https://gazebosim.org/libs/sdformat/
  - https://docs.ros.org/en/rolling/p/xacro/
  - https://docs.rs/urdf-rs
  - https://docs.rs/sdformat
  - https://index.ros.org/p/sdformat_urdf/
---

# Problem

Robot-description work is still messy at the exact point where teams most need boring reliability:

- authors write **xacro** because hand-maintaining raw robot XML is painful,
- much downstream tooling still expects **URDF**,
- simulators and richer scene descriptions want **SDFormat**,
- and conversions silently lose or reinterpret semantics around frames, sensors, materials, plugins, dynamics, and simulator-specific behavior.

Rust already has URDF and SDFormat substrate. The missing contribution is not “one more parser.” It is a **loss-aware interop workbench** that can say exactly what survived xacro expansion, URDF interpretation, and URDF↔SDF conversion — and what did not.

# What it provides

- `robotdesc.lock` — pins xacro version/expansion assumptions, URDF interpretation rules, SDFormat target version, and simulator profile.
- `expansion.receipt.json` — records macro expansion, include provenance, and parameter values.
- `transform.loss.json` — explains what was preserved, normalized, dropped, or synthesized during URDF↔SDF conversion.
- `frame-joint.diff.json` — compares kinematic trees, inertial data, visuals, collisions, and plugin payloads.
- `fixture-pack/` — tiny robot models designed to expose conversion edge cases.
- `cargo robotdesc-evidence` — emits `*.robotbundle.zip` with expanded source, normalized model, diff reports, and simulator notes.

# What the crate should provide other people

1. **A boring, reviewable handoff artifact for robot descriptions**.
2. **Loss accounting** for xacro expansion and URDF↔SDF transforms.
3. **Simulator-profile receipts** instead of “it looked fine in Gazebo on my machine.”
4. **A reusable Rust comparison core** for robot-tooling pipelines, CI, and asset review.
5. **A safer migration path** between authoring and simulation representations.

# Persona / who it’s for

- robotics platform teams
- simulation and digital-twin tool builders
- robot-description maintainers in ROS ecosystems
- CI/tooling owners validating robot assets before release

# Users & user stories

- **Robotics maintainer**: “Show me which links, sensors, or inertial fields changed when this xacro-expanded URDF was converted to SDFormat.”
- **Simulator integrator**: “Package the exact model, expansion inputs, and target-profile assumptions that reproduced a bad simulation.”
- **Tool builder**: “Depend on one lock/diff schema rather than implement URDF/SDF comparison logic from scratch.”
- **Reviewer**: “Approve a robot-description migration based on an explicit loss report, not screenshots.”

# Prior art (and why it’s insufficient)

- SDFormat is a real specification and conversion ecosystem.
- xacro is widely used as a macro language for robot XML authoring.
- Rust has `urdf-rs`, `sdformat`, and visualization/robotics crates.

What Rust still lacks is an **artifact layer** that makes authoring expansions, conversion loss, and simulator-profile assumptions visible and portable.

# Design goals

1. **Loss-honest** — make conversion and normalization losses explicit.
2. **Authoring-aware** — xacro expansion is first-class provenance, not prehistory to discard.
3. **Profile-explicit** — target simulator/version assumptions must be pinned.
4. **Tree-centric** — kinematics, frames, inertia, and sensor placement deserve dedicated diffs.
5. **Asset-pipeline friendly** — usable in CI and preflight checks, not just interactive debugging.

# MVP surface

- Minimal types: `RobotDescLock`, `ExpansionReceipt`, `NormalizedRobot`, `LossReport`, `KinematicDiff`, `RobotBundle`
- Minimal functions:
  - `expand_xacro_receipted()`
  - `parse_urdf()`
  - `parse_sdf()`
  - `convert_with_loss_report()`
  - `diff_robot_models()`
  - `write_bundle()`
- Feature flags:
  - `xacro`
  - `urdf`
  - `sdf`
  - `plugins`
  - `gazebo-profiles`

# Compatibility story

- Treats SDFormat version and simulator profile as explicit bundle state.
- Treats xacro as a de-facto authoring layer whose expansion provenance matters.
- Supports comparing authoring-form, expanded-form, and normalized-form models side by side.
- Keeps rendering, physics engines, and simulator runtimes out of the core.

# Conformance & fixtures

- Tiny corpora for fixed-joint collapsing, frame drift, sensor pose changes, inertial normalization, and plugin passthrough.
- Goldens for xacro include/macro expansion receipts.
- Explicit examples where URDF has no faithful SDFormat equivalent and vice versa.
- Fixtures for simulator-profile-specific warnings.

# Path to boring stability

- Stabilize `robotdesc.lock`, `expansion.receipt.json`, and `transform.loss.json` first.
- Start with offline analysis of already-expanded models.
- Keep simulator adapters optional and profile-driven.
- Resist drift into becoming a full simulator or model editor.

# Scorecard

- Impact: 4/5
- Neglectedness: 4/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 4/5
- Differentiation: 5/5
- **Total: 25/30**

# Minimum lovable MVP

A Rust library and CLI that expand one xacro file, normalize one URDF and one SDFormat model, produce a kinematic/loss diff, and package the results as a compact review bundle.

# De-risk plan

1. Start with small fixture robots, not full industrial cells.
2. Treat plugins and simulator extensions as opaque-but-receipted payloads at first.
3. Keep conversion-loss reporting more important than one-shot “auto-fix” features.
4. Validate on CI-safe corpora before chasing every ROS edge case.

# Non-goals

- Not a full simulator.
- Not a CAD or mesh editor.
- Not a URDF/SDF authoring GUI.
- Not a ROS runtime replacement.

# Architecture & API sketch

```rust
pub struct RobotDescLock {
    pub xacro_version: Option<String>,
    pub urdf_profile: String,
    pub sdf_version: String,
    pub simulator_profile: Option<String>,
}

pub fn expand_xacro_receipted(path: &std::path::Path) -> Result<ExpansionReceipt>;
pub fn convert_with_loss_report(model: &NormalizedRobot, target: TargetFormat) -> Result<LossReport>;
pub fn diff_robot_models(a: &NormalizedRobot, b: &NormalizedRobot) -> KinematicDiff;
pub fn write_bundle(bundle: &RobotBundle, out: &std::path::Path) -> Result<()>;
```

Bundle draft: `robotdesc.lock`, `source/`, `expanded/`, `normalized/`, `frame-joint.diff.json`, `transform.loss.json`, `simulator-notes.md`.

# Security / safety model

- Support redaction of proprietary meshes, package paths, and vendor plugin blobs.
- Keep plugin payloads hashable even when they cannot be interpreted.
- Distinguish physical-safety-impacting differences (inertia, collisions, joint limits) from cosmetic differences.
- Preserve enough provenance to reproduce a simulator mismatch without shipping all source assets.

# Maintenance & governance plan

- Track SDFormat versions explicitly.
- Keep simulator-specific semantics in profile packs.
- Publish a small public fixture suite focused on high-confusion transformations.
- Avoid binding the core schema to one simulator vendor.

# Milestones

## 0.1
- `robotdesc.lock`
- xacro expansion receipt
- URDF/SDF normalization and tree diff

## 0.2
- conversion loss reports
- simulator profile packs
- redacted fixture corpus

## 1.0
- stable `*.robotbundle.zip`
- CI-friendly migration gates
- reusable corpus for tool vendors

# Open questions

- What is the smallest normalized robot model that still supports useful loss reporting?
- How should simulator plugins be represented when only partial semantic understanding is available?
- Which URDF↔SDF mismatches deserve hard errors versus advisory findings?

# Sources

- SDFormat specification home: https://sdformat.org/
- Gazebo SDFormat documentation: https://gazebosim.org/libs/sdformat/
- xacro documentation: https://docs.ros.org/en/rolling/p/xacro/
- `urdf-rs` docs: https://docs.rs/urdf-rs
- `sdformat` docs: https://docs.rs/sdformat
- `sdformat_urdf` overview: https://index.ros.org/p/sdformat_urdf/
