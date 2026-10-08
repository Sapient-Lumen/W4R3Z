# rev0077 — replay bundle inspect diagnostics

rev0076 made replay artifacts trustworthy as a bundle, but the first failure mode was still too opaque: callers got a broad error string and a few hashes. That is not enough when a replay bundle has crossed a process, filesystem, or agent boundary.

rev0077 adds a small diagnostic layer without creating a new registry:

- `ReplayArtifactFailureKind` classifies the trust boundary that failed.
- `ReplayArtifactVerifyResult` carries expected and actual values for checkpoint state hash, checkpoint journal hash, checkpoint journal entries, action count, and final StateCore hash.
- `mtgsim_cli --inspect-replay-bundle` prints a compact, parse-first report for the snapshot, trace, manifest, and verification result.
- `mtgsim_cli --artifact-bundle-inspect-roundtrip` keeps the inspection path executable in CTest.

The important distinction is that inspection is not replay doctrine. It is a practical failure-localization tool:

1. Exact snapshot/trace text hashes catch byte-level tampering before parsing.
2. Checkpoint metadata mismatch catches a valid manifest paired with the wrong replay root before mutation.
3. action-count mismatch catches a manifest/trace disagreement before replay attempts an action.
4. Trace replay mismatch still reports the underlying `ActionReplayFailureKind` and first mismatch index.
5. Final StateCore mismatch catches a self-consistent trace that does not reach the manifest's promised final state.

The diagnostic path is intentionally compact. It reuses `StateCoreSnapshot.v1`, `ActionTrace.v1`, and `ReplayArtifactManifest.v1`; it does not serialize journal evidence or introduce another object registry.
