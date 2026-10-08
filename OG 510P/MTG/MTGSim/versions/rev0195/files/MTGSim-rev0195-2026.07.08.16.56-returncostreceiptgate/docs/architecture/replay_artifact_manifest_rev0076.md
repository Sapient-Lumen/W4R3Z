# rev0076 replay artifact manifest

rev0075 made persisted replay executable by writing and verifying a `StateCoreSnapshot.v1` plus `ActionTrace.v1` pair through the CLI. The riskiest remaining gap was artifact trust: two separate files could be swapped, edited, or misreported without a single durable unit describing what replay is supposed to prove.

rev0076 adds `MTGSim.ReplayArtifactManifest.v1`. The manifest binds:

- exact snapshot text hash,
- exact trace text hash,
- source checkpoint StateCore hash, journal hash, and journal entry count,
- parsed action count,
- applied-only export policy,
- expected final StateCore hash,
- and a manifest `bundle_hash` over the manifest payload.

`parse_replay_artifact_manifest(...)` rejects malformed, duplicate, unknown, missing, or self-hash-mismatched fields before any replay. `verify_replay_artifact_bundle(...)` then rejects changed snapshot bytes, changed trace bytes, checkpoint metadata mismatches, action-count mismatches, replay divergence, and final StateCore hash mismatch.

This is deliberately not a new card registry and not a journal serializer. It is the smallest durable trust wrapper around the replay root and action trace already present in the cube.

The CLI exposes the seam through:

```bash
mtgsim_cli --write-demo-replay-bundle SNAPSHOT TRACE MANIFEST
mtgsim_cli --verify-replay-bundle SNAPSHOT TRACE MANIFEST
mtgsim_cli --artifact-bundle-roundtrip SNAPSHOT TRACE MANIFEST
```

CTest keeps the path executable with `mtgsim_cli_replay_bundle_roundtrip`.
