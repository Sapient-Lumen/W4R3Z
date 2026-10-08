# Robot Description Surface pilot program

## Goal
Prove that a thin `robot-description-pack/v0` layer can unify authored description truth across parser, builder, kinematics, runtime, replay, and visualization lanes **without replacing them**.

## Ranked pilot slices

### 1. Static model round-trip
Use `urdf-rs` and `robot-description-builder` to export the same robot subject into:
- `robot-description-subject/v0`
- `robot-structure-map/v0`
- `frame-topology-map/v0`
- `geometry-asset-manifest/v0`
- `limits-calibration-profile/v0`

Success condition: a human can review the exported structure without reading raw XML or Rust builder code.

### 2. Kinematics + visualization agreement
Import `k` and either `urdf-viz` or Rerun-side structure checks.

Success condition: the pack can record whether the exported frame/joint graph is compatible with kinematics and visualization consumers, while preserving where those lanes disagree.

### 3. ROS runtime attachment
Attach runtime evidence from `rclrs` or `r2r` examples.

Success condition: runtime node/topic/frame usage can be linked to the description pack as imported evidence, without pretending runtime activation is authored description truth.

### 4. Alternate transport / middleware posture
Attach Zenoh-based posture via ROS 2 Zenoh middleware or pure-Rust-over-Zenoh experiments such as `oxidros-zenoh`.

Success condition: transport/runtime differences are visible as imported runtime posture, not baked into the robot-description contract itself.

### 5. Replay / archaeology
Attach `rosbags-rs` or MCAP/Rerun replay evidence.

Success condition: a replay can point back to the robot-description subject and frame topology it was interpreted against, while preserving uncertainty when the match is partial or approximate.

## What this would prove
If the pilot works, the archive can argue for a real **Robot Description Surface Kit** contribution rather than another parser, DSL, or robotics mega-framework.
