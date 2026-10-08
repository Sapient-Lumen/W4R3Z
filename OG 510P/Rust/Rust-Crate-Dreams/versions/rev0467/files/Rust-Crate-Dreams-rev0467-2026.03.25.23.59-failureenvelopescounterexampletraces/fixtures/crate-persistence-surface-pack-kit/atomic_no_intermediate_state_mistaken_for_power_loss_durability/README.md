# Atomic no-intermediate-state claim mistaken for power-loss durability

Simulates a crate that advertises “atomic writes” because it uses an overwrite helper or temp-file replacement path, but does not prove the stronger claim that the final directory entry is durably published after sudden power loss.

Why this matters:
- `atomic-write-file` documents **no intermediate state**, which is valuable, but that is not the same thing as “durable after restart”.
- `tempfile::NamedTempFile::persist` also warns that neither the file contents nor the containing directory are synchronized when `persist` returns.
- `std::fs::rename` replaces the destination on the same mount point, but does not itself settle whether the result is durably published.

What this scenario should force:
- an `atomicity-scope.report` that can stop at `no_intermediate_state_only` or `destination_replace_same_mount`
- a separate durability-boundary statement instead of one blurred “atomic save” badge
- a doctor warning such as `atomic_no_intermediate_state_presented_as_durable`
