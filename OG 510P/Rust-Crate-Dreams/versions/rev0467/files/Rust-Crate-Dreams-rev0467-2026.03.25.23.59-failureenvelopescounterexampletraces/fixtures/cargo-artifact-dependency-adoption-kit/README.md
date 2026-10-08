# Cargo Artifact Dependency Adoption Kit fixtures

These fixtures are for **P-0495 Cargo Artifact Dependency Adoption Kit**.

The point is to freeze the target-matrix / env-binding / fallback layer around artifact dependencies, including the newer bridge posture for reusable build helpers.

These fixtures should stay distinct from:

- final artifact handoff bundles,
- sidecar attachment contracts,
- delegated build-script unit plans,
- and host/target scope diagnosis.

Scenario families in this pass:
- `renamed_multi_target_delegate_bridge/`
- `stable_workspace_helper_fallback/`
