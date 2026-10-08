# mxtest resume environment gate (rev756)

Rev755 made host evidence visible by embedding `micromax.mxtest.environment.v1` in mxtest plan/run manifests and adding no-run current-environment verification. Rev756 closes the enforcement gap: `--run-chunks --resume` now requires the previous aggregate manifest's `environment_digest` to match the current run before any passed chunk can be skipped.

## Why this matters

Source digests answer whether the files being tested changed. They do not answer whether the earlier pass came from the same Python executable, Python version, pytest version, platform, or plugin-autoload setting. A source-identical but host-different manifest can still be useful evidence, but it should not silently suppress work in a resumed validation run.

## Resume gates

A previous chunk is skipped only when all of these are true:

1. the previous chunk status is `passed`
2. the previous and current top-level `source_digest` match
3. the previous and current top-level `environment_digest` match
4. the chunk index and total match
5. `selected`, `strategy`, `first`, `last`, and ordered `nodeids_digest` match

When source or environment evidence is missing or changed, mxtest prints a rerun notice and executes the previously passed chunk again.

## Skip reason

Resumed records now use a more explicit skip reason:

```json
{
  "resumed": true,
  "skipped": true,
  "skip_reason": "previous-passed-matching-source-environment-and-chunk"
}
```

The wording is intentionally long. A handoff reader should not have to infer whether a skip was guarded only by node ids, by source content, or by both source and host evidence.

## Boundary

This is still local evidence, not signed provenance. The environment digest is intentionally lightweight and may invalidate resume skips for benign host drift such as a different Python executable path. That is acceptable for the default trust posture: resuming should be conservative, and users can still compare or inspect old manifests with `--diff-manifests`, `--verify-current-source`, and `--verify-current-environment` before deciding how much to trust them.
