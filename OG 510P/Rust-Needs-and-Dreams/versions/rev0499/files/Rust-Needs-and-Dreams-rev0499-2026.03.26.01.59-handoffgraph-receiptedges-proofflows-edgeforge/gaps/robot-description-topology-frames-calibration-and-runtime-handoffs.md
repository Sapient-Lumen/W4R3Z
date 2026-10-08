# Gap: robot description, frame topology, limits/calibration posture, and runtime/replay handoffs

## The missing thing
Rust robotics now has real ingredients for **robot models**, **ROS 2 runtime integration**, **alternate transport/runtime lanes**, **replay/inspection**, and **visualization**. What it still lacks is a thin, reviewable boundary for the robot description itself: one honest answer to questions like:
- what robot subject is being described;
- what frames and joints exist;
- what geometry/assets are referenced;
- what limits, mimic rules, and calibration-like assumptions matter;
- and what runtime/replay evidence actually attached to that description later.

Today, those truths are scattered across URDF files, builder code, kinematics libraries, ROS packages, runtime topic graphs, MCAP logs, and visualization-specific assumptions.

## Why this now looks real rather than speculative
- ROS 2 now officially lists Rust client-library work, and FOSDEM 2026 material around `rclrs` says Rust support is part of the rolling release trajectory rather than only a side project.
- The runtime lanes are already plural: `rclrs`, `r2r`, Zenoh-backed ROS 2 middleware, and pure-Rust-over-Zenoh approaches are all real but not equivalent.
- Rerun now makes **physical-world frames**, URDF examples, MCAP import, and ROS 2 reflection/visualization a serious inspection lane rather than a toy viewer.
- The model-side ingredients are also real: `urdf-rs`, `robot-description-builder`, `k`, `urdf-viz`, OpenRR-adjacent motion/control tooling, and `rosbags-rs` all cover different slices of robot description truth.

That is exactly the pattern where another framework or parser would miss the real need. The ecosystem needs a **portable description contract** above the ingredients.

## What a worthy contribution would do
A worthy contribution would not try to replace URDF, ROS 2, kinematics libraries, planners, or viewers. It would define a thin layer such as `cargo robotdesc` / `robot-description-pack/v0` that can:
1. identify the robot subject and source materials under review;
2. export a stable frame/joint/topology map from authored descriptions or builder code;
3. attach geometry/mesh/material references without pretending assets and structure are the same thing;
4. record limits/mimic/calibration-like posture explicitly;
5. attach runtime/replay/import evidence later without mutating the authored description;
6. produce diffs that humans and tools can review.

## Ownership boundary
- **Robot Description Surface** should own authored structure, frames, joints, geometry references, and declared limits.
- **Runtime/ROS/transport layers** should own node/topic/service/graph activation and transport-specific posture.
- **Replay/visualization layers** should own imported logs, traces, and renderable runtime evidence.
- **Support/docs/product layers** should own what is promised downstream.

## Anti-goals
- not another robotics framework;
- not another URDF parser alone;
- not a hidden simulator schema that quietly replaces existing formats;
- not one fake score for “robotics readiness”.

## Candidate output artifacts
- `robot-description-subject/v0`
- `robot-structure-map/v0`
- `frame-topology-map/v0`
- `geometry-asset-manifest/v0`
- `limits-calibration-profile/v0`
- `robot-description-diff/v0`
- `robot-description-check-report/v0`
