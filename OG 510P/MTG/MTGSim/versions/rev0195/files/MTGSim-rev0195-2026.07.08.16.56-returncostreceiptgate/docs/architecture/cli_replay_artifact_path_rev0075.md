# rev0075 — CLI replay artifact path

The riskiest gap after `StateCoreSnapshot.v1` and `ActionTrace.v1` was practical: replay was durable in library tests, but not exposed as an executable artifact workflow. A user or harness could not ask the shipped binary to write snapshot/trace files and then verify those files from disk.

rev0075 adds that narrow path without creating another registry:

```bash
mtgsim_cli --write-demo-replay SNAPSHOT TRACE
mtgsim_cli --verify-replay SNAPSHOT TRACE
mtgsim_cli --artifact-roundtrip SNAPSHOT TRACE
```

`--write-demo-replay` creates a deterministic checkpoint, serializes it as `MTGSim.StateCoreSnapshot.v1`, applies a small `apply_action(...)` trace, and serializes the resulting `MTGSim.ActionTrace.v1` action stream. `--verify-replay` parses both files, reconstructs StateCore from the snapshot, applies the parsed trace via `replay_action_trace(...)`, and reports first-divergence fields on failure.

This is still intentionally modest. It does not yet serialize forensic journal rows, hidden-information observations, or arbitrary fixture construction. The value is that the replay root and action trace now cross the process/file boundary through an executable CLI command and a CMake smoke test: `mtgsim_cli_replay_artifact_roundtrip`.
