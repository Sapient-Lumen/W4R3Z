# mixed_msrv_workspace_compromise

Goal: freeze the case where one workspace member's lower MSRV drags a shared dependency version downward, while another member could have used a newer version.

Why it matters:
- resolver docs explicitly describe heuristic "good enough" behavior for mixed-Rust-version workspaces,
- lockfile generation and compile-time feature passes are not the same thing,
- and a worthy explanation crate must distinguish hard requirement, heuristic compromise, and lockfile carry-forward.
