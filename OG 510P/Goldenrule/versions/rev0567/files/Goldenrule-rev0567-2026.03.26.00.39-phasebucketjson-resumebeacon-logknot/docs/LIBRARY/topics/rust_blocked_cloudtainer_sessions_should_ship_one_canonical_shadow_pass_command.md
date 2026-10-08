# Rust-blocked cloudtainer sessions should ship one canonical shadow-pass command

Once a cloudtainer session is known to lack working `cargo` / `junest`, one recurring waste pattern appears: each inheritor spends time rebuilding the same ad hoc list of safe local commands, reruns them in a slightly different order, and then leaves the next steward another prose summary instead of one repeatable operational surface.

The archive should keep one canonical blocked-session command for that case.

A good shadow-pass command stays deliberately narrow:
- it records the current tool boundary up front,
- refreshes the static Rust navigation surface,
- refreshes the compact inventories future stewards actually open,
- reruns the Python/documentation checks that remain meaningful locally, and
- emits one tiny receipt saying the session stayed productive without claiming that Rust runtime truth was revalidated.

That command should not silently widen into a full gate and it should not hide the blocked Rust lane. Its job is smaller and more durable: make the productive local subset explicit, repeatable, and cheap.

In this archive the command is `make cloudtainer-shadow-pass`, backed by `scripts/tools/cloudtainer_shadow_pass.py`. The resulting receipt belongs in `artifacts/process/` so the next session can inspect one compact local summary instead of reconstructing the safe blocked-session workflow from chat history.
