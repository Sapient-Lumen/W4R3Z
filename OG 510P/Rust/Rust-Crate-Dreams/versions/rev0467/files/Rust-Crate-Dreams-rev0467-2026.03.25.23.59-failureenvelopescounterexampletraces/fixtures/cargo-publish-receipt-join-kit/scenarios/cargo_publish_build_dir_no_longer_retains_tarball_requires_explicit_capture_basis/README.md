# Scenario — cargo publish with `build.build-dir` no longer leaves a final tarball artifact

This scenario exists so **P-0477 Cargo Publish Receipt Join Kit** does not assume that a post-publish receipt can always point at a still-present `.crate` file from the publish run.

Current Rust release notes say that `cargo publish` no longer keeps `.crate` tarballs as final build artifacts when `build.build-dir` is set, and recommend `cargo package` when a final tarball artifact is needed.

The receipt should therefore say explicitly whether the authoritative local artifact came from:

- `cargo package`,
- a retained dry-run artifact,
- an imported CI artifact,
- or a later registry re-download.
