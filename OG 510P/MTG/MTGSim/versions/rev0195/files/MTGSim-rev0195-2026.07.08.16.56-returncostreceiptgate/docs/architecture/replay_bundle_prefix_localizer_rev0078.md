# rev0078 replay bundle prefix localizer

The risky gap after rev0077 was operational: manifest-bound replay failures were typed and inspectable, but there was still no artifact-production path that reduced a large failing trace to the smallest useful unit. A user still had to manually bisect `ActionTrace.v1` when a replay-step divergence occurred.

rev0078 adds `ReplayArtifactPrefixResult` and `make_replay_artifact_prefix_bundle(...)`. The function verifies the source bundle, keeps only replay-localizable failures, and emits a new `ActionTrace.v1` plus a fresh `ReplayArtifactManifest.v1` rooted at the original snapshot.

For `TraceReplayFailed`, the emitted trace is the **longest known-good prefix**: every action before the first divergent step. The result records `next_bad_step`, so the failing action remains explicit without forcing the reduced bundle itself to fail verification. For `FinalStateHashMismatch`, replay succeeded and the mismatch is isolated to the manifest expectation, so the whole trace is retained and the new manifest is normalized to the replayed final StateCore hash.

The CLI exposes this through:

```bash
mtgsim_cli --write-replay-prefix SNAPSHOT TRACE MANIFEST PREFIX_TRACE PREFIX_MANIFEST
mtgsim_cli --artifact-bundle-prefix-roundtrip SNAPSHOT TRACE MANIFEST PREFIX_TRACE PREFIX_MANIFEST
```

This is intentionally not another registry. It is a small refactor around the replay artifact boundary: parse once, verify, reduce to the longest known-good prefix, re-manifest the prefix, and keep the original snapshot as the stable replay root.
