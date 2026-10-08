---
id: P-0143
title: ROS2 Workcell Kit — cargo-native scaffolding, bag replay, and conformance for robotics apps
status: idea
domains: [robotics, ros2, integration, testing, tooling]
last_reviewed: 2026-03-05
evidence:
  - https://docs.rs/rclrs
  - https://github.com/ros2-rust/ros2_rust
  - https://crates.io/crates/rclrs
  - https://foxglove.dev/blog/first-steps-using-rust-with-ros2
needs:
  - Make “Rust + ROS 2” feel first-class: project scaffolding, message/interface generation, and runtime ergonomics.
  - Make integration testing reproducible: bag playback, deterministic fixtures, and CI-friendly failure artifacts.
  - Reduce newcomer friction: environment/setup, workspace layout, and dependency pinning across ROS distributions.
---

## What this crate should provide (to other people)

A **batteries-included toolkit** for building and testing ROS 2 robotics applications in Rust that feels like the “golden path”:
- `cargo ros2 new` scaffolds a node/package with recommended workspace layout (colcon + Cargo coexistence), launch stubs, and CI templates.
- `cargo ros2 interfaces` generates Rust bindings from `.msg/.srv/.action` with pinned, reproducible build inputs.
- `cargo ros2 bag {record,play,replay}` to turn ROS bag data into deterministic test fixtures.
- A stable, shareable **`*.rosbundle.zip`** artifact format for bug reports (manifest, bag subset, QoS profile, logs, platform fingerprint).

## Scope and non-goals

**In-scope**
- “Workflow + artifacts” layer above `rclrs`: scaffolding, repeatability, and test harnesses.
- Conformance harnesses for common ROS patterns: QoS, timers, subscriptions, services, actions.

**Out of scope**
- Replacing `rclrs` or deciding ROS 2 Rust API surface.
- Full simulator/physics engine integration (leave to Gazebo/Isaac/etc).

## Design sketch

### Components
1. **Workspace scaffold**
   - Templates for `rclrs` nodes with `tracing` defaults and structured logging.
   - Docker/devcontainer recipes for reproducible ROS toolchain setup.

2. **Interface generation pipeline**
   - Deterministic binding generation (record generator version + inputs).
   - Cacheable output + CI checks to ensure generated code is committed/consistent.

3. **Bag → fixture pipeline**
   - “Fixture extraction” (subset topics/time ranges) for small, shareable corpora.
   - A replay harness that asserts on message streams (with tolerance windows).

4. **Conformance + failure artifacts**
   - Conformance scenarios as code (“workcell scenarios”), producing stable summaries.
   - Failure bundle captures: QoS negotiation results, timing drift, message counts, platform details.

### Artifact format: `rosbundle.zip`
Minimum contents:
- `manifest.toml` (scenario, versions, ROS distro, OS, CPU)
- `inputs/` (bag snippet or synthetic events)
- `outputs/` (logs, summary metrics, optional traces)
- `qos/` (declared QoS + negotiated QoS)

## MVP → v1 plan

**MVP**
- `cargo ros2 new`
- `cargo ros2 bag replay` + `rosbundle.zip`
- One canonical conformance scenario (pub/sub timing + QoS)

**v1**
- Interfaces pipeline (`cargo ros2 interfaces`)
- Scenario library (actions/services)
- CI integrations: GitHub Actions templates + report upload

## Adoption strategy

- Start as **workflow tooling** that works with existing `rclrs` projects.
- Publish “known-good templates” for common robot stacks (sensor → filter → planner → actuator).
- Provide a “doctor” command that checks environment drift (ROS distro mismatch, missing dependencies).
