# Scenario: cargo-fix source edits observed but manifest/docs follow-through still needs approval

This fixture freezes the distinction between **fix capability** and **fixup posture**.

The lane has real automation substrate:
- `cargo fix` can apply Rust-source edits,
- a maintainer codemod can touch manifests and docs,
- and the migration family includes config follow-through.

But that does **not** mean the lane is safe for unattended execution.
The pack should say whether the next action is manual-only, assisted, approval-required, or bounded-autonomous, and it should carry stop conditions for any multi-step path.
