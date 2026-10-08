# Robot Description Surface Kit

## Intent
`cargo robotdesc` should define a **portable, reviewable robot-description boundary** above URDF files, builder APIs, and downstream runtime/replay lanes.

The point is not to declare a new canonical robot-description format. The point is to make existing descriptions exportable as stable evidence that other tools can inspect, diff, attach, and import honestly.

## Why this belongs in Rust
Rust already has credible ingredients across:
- description parsing (`urdf-rs`);
- typed/builder authoring (`robot-description-builder`);
- kinematics (`k`);
- runtime integration (`rclrs`, `r2r`, Zenoh-backed ROS lanes);
- visualization (`urdf-viz`, Rerun);
- replay/import (`rosbags-rs`, MCAP-oriented tooling).

Those ingredients are strong enough that the missing seam is now the **surface contract**, not another parser.

## Proposed command + pack
- Command: `cargo robotdesc`
- Pack: `robot-description-pack/v0`

### Candidate sub-artifacts
#### 1. `robot-description-subject/v0`
What exact robot description subject is under review?
- package/crate/workspace subject
- source files or builder modules used
- primary authored format(s)
- optional provenance hints

#### 2. `robot-structure-map/v0`
Declared structural elements.
- links
- joints
- mimic relationships
- transmissions/attachments if available
- named groups if available

#### 3. `frame-topology-map/v0`
Portable frame graph.
- parent/child frame edges
- fixed vs movable relationships
- transform declarations where statically available
- unresolved or imported-only edges called out explicitly

#### 4. `geometry-asset-manifest/v0`
Geometry/material/mesh references.
- primitive geometry declarations
- mesh URIs/paths
- optional materials/textures
- missing assets or unresolved references

#### 5. `limits-calibration-profile/v0`
Mechanical and calibration-like posture.
- joint limits
- mimic/scaling/offset rules
- defaults and named profiles if exposed
- “unknown/unmodeled here” explicitly preserved

#### 6. `robot-description-check-report/v0`
Checked integrity results.
- parse/build success
- frame-tree sanity checks
- missing asset checks
- kinematics compatibility checks
- visualization/export/import comparison notes

#### 7. `robot-description-diff/v0`
Human-reviewable structural diff.
- added/removed/changed links and joints
- frame graph changes
- geometry reference changes
- limit/profile changes
- unresolved changes called out, not hidden

#### 8. `robot-description-pack/v0`
Bundle tying the above together with versioning and tool metadata.

## Ownership rules
- This kit owns **authored model truth**.
- It may import builder-generated or parsed structure.
- It may attach runtime/replay evidence later, but runtime evidence must remain clearly imported, not silently merged into the authored model.
- It must preserve partiality honestly; many descriptions will be incomplete, asset-light, or environment-dependent.

## Rollout
### Slice 1 — static structure export
Support URDF + builder-based export to subject/structure/frame/geometry/limits artifacts.

### Slice 2 — diff + integrity checks
Add missing-asset/frame-tree/joint-limit sanity checks and reviewable diffs.

### Slice 3 — kinematics and visualization imports
Import `k` and visualization comparison outputs without making them the owner of structure truth.

### Slice 4 — runtime/replay attachments
Attach ROS topic/frame usage or MCAP-derived evidence as imported runtime posture.

### Slice 5 — downstream consumers
Let docs/support/release/robotics-product consumers import the pack.

## Anti-goals
- not a simulator;
- not a planner;
- not a middleware winner;
- not a replacement for URDF/SDF/etc.;
- not a hidden schema empire.
