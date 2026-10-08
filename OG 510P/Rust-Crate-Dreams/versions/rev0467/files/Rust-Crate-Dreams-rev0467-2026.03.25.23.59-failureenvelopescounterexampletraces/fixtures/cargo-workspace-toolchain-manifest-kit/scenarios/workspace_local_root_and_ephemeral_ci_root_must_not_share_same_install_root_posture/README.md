# workspace_local_root_and_ephemeral_ci_root_must_not_share_same_install_root_posture

A persistent workspace-local root and an ephemeral CI-only root can both support reproducible tool use, but they do not make the same claim about persistence, path visibility, or cleanup responsibility.

This fixture keeps **install-root posture** separate from the abstract fact that “the workspace has pinned tools”.
