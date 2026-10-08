# Epic proposal: Robot Description Surface Kit

## Proposal
Build a thin `cargo robotdesc` / `robot-description-pack/v0` layer for Rust robotics.

## Why this is worthy
Rust robotics now has enough serious ingredients that the missing contribution is no longer “get one parser working.” The ecosystem has:
- official ROS 2 Rust motion (`rclrs` and rolling-release support signals);
- runtime-diverse client lanes (`rclrs`, `r2r`, Zenoh-backed ROS 2, pure-Rust-over-Zenoh experiments);
- model-side authoring/parsing/kinematics/viewing lanes (`urdf-rs`, `robot-description-builder`, `k`, `urdf-viz`);
- replay and visualization lanes (`rosbags-rs`, MCAP/Rerun, frame-aware visualization).

But it still lacks one **honest robot-description boundary** above those pieces.

## The contribution
The worthy move is not another robotics framework, simulator, or format crusade. It is a portable pack that keeps these truths separate:
- robot subject identity;
- structure and joint topology;
- frame topology;
- geometry/assets;
- limits and calibration-like assumptions;
- imported runtime/replay attachment evidence;
- downstream support or product claims.

## Suggested artifact family
- `robot-description-subject/v0`
- `robot-structure-map/v0`
- `frame-topology-map/v0`
- `geometry-asset-manifest/v0`
- `limits-calibration-profile/v0`
- `robot-description-check-report/v0`
- `robot-description-diff/v0`
- `robot-description-pack/v0`

## Who this helps
- robotics library authors who want reviewable model diffs;
- runtime/framework authors who need a stable description import boundary;
- visualization/replay tools that need to say what model/frame assumptions they used;
- support/release teams that need a product-facing robotics contract;
- future higher-level robotics-productization work.

## First execution path
Treat [`design/robot-description-surface-kit.md`](../design/robot-description-surface-kit.md) and [`design/robot-description-pilot-program.md`](../design/robot-description-pilot-program.md) as the immediate execution pair.

## Anti-goals
- not a winner-take-all robotics runtime;
- not a mandatory replacement for URDF;
- not an excuse to collapse structure truth, runtime truth, and replay truth into one story.
