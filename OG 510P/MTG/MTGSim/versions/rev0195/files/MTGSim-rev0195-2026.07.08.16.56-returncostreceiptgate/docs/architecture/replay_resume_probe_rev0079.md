# Replay resume probe — rev0079

`ReplayArtifactResumeResult` is the new result carrier for this seam. rev0079 turns the rev0078 prefix localizer into an actionable resume artifact. A prefix artifact says “the longest known-good prefix has N actions.” A resume probe goes one step further: it actually replays that prefix, serializes a new `StateCoreSnapshot.v1` at the resulting StateCore boundary, and writes the remaining suffix as a new `ActionTrace.v1` plus `ReplayArtifactManifest.v1`.

## Why this matters

A full replay bundle can be large enough that a failure report still leaves debugging work scattered across many earlier transitions. The resume probe makes the failing transition small and local:

- original bundle: `snapshot + full trace + manifest`
- prefix localizer: `prefix trace + prefix manifest + next_bad_step`
- resume probe: `resume snapshot + suffix trace + suffix manifest`

For a `TraceReplayFailed` source, the first divergent original action is rebased to suffix step one. This means the next investigation can run a tiny manifest-bound bundle rooted exactly at the last known-good StateCore hash.

## Boundaries

`make_replay_artifact_resume_probe(...)` only operates after the bundle reaches a localizable boundary:

- accepted: verified bundle, action-count mismatch, trace replay failure, final-StateCore mismatch;
- rejected: unsupported formats, manifest bundle-hash mismatch, snapshot/trace text hash tampering, snapshot parse failure, checkpoint seal mismatch, and trace parse failure.

That split is intentional. Resume probes should not normalize evidence that failed basic trust checks.

## Behaviors

For replay-step failures:

1. verify the original manifest-bound bundle;
2. parse the original snapshot and trace;
3. derive the longest known-good prefix from the first mismatch index;
4. replay that prefix into a working `GameState`;
5. branch/trim the journal at that state;
6. serialize a fresh `StateCoreSnapshot.v1`;
7. serialize the remaining suffix trace;
8. manifest-bind the suffix bundle using the original expected final StateCore hash.

For already verified bundles, the full trace is the prefix and the suffix is empty. The resume snapshot is the final StateCore snapshot and the empty suffix verifies immediately.

For final-StateCore mismatches, the trace replay itself is good, so the full trace is the prefix. The suffix is empty and its manifest retains the original expected final hash, making the mismatch explicit at the new boundary.

## CLI

```bash
mtgsim_cli --write-replay-resume-probe SNAPSHOT TRACE MANIFEST RESUME_SNAPSHOT SUFFIX_TRACE SUFFIX_MANIFEST
mtgsim_cli --artifact-bundle-resume-roundtrip SNAPSHOT TRACE MANIFEST RESUME_SNAPSHOT SUFFIX_TRACE SUFFIX_MANIFEST
```

The roundtrip CTest keeps the path executable so future replay changes cannot silently break file-level resume artifacts.

## Remaining risks

This is still a deterministic text-artifact pipeline, not a semantic minimizer. It does not yet attempt delta-debugging inside a single suspect transition, action-choice normalization, or snapshot slicing by object dependency. Those should come after the choice/event transaction boundary is stronger.
