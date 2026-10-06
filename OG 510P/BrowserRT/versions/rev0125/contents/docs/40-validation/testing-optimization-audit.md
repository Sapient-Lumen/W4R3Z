# Testing optimization audit

Revision: rev0028.

BrowserRT is being built in short cloudtainer windows. The testing facility must therefore optimize for selective confidence, not brute-force confidence.

## Current posture that should stay

- Broad release stays browser-light.
- Browser/CDP slices are explicit ids, `browser` tier, or `full` tier only.
- Package-time release tests run serially by default.
- Test tasks have estimated time and timeout budgets.
- Expensive proofs get their own manifest ids.
- Timing reports and slowest-task analysis are artifacts, not console-only memories.
- One-shot fixtures own setup, teardown, and policy restoration.

## What rev0028 fixed

Affected selection had a runner-only regression: `--only-affected --changed tools/run_tests.mjs` could produce an empty plan even though the impact map named impacted tasks. Rev0022 fixes the runner and adds a release-tier dry-run artifact:

```txt
facility:affected-runner-dry-run
artifacts/validation/REV0044-AFFECTED-RUNNER-DRYRUN.json
```

This is important because future refactoring will rely heavily on affected runs. A silent empty affected run is worse than a slow full run.

## What future sessions should watch

When adding or changing tests, check:

1. Does the test have a manifest id?
2. Is its tier honest?
3. Is its lane honest?
4. Is its estimated time realistic?
5. Is its timeout bounded?
6. Does it write a proof artifact when it claims a proof?
7. Does the impact map select it when its code changes?
8. Does the surface inventory explain why the surface exists?
9. Does the validation doc state non-claims?
10. Does broad release remain browser-light unless intentionally changed?

## Parallelism stance

Parallelism is useful for cheap Node slices. It is dangerous for browser/CDP slices in short cloudtainer windows. The runner respects `parallelGroup`; browser tasks use `browser-process` so they do not launch multiple Chromium fixtures concurrently when selected together.

The release gate uses `--jobs 1` because predictable completion is currently more valuable than theoretical speed.

## Long-run desiderata

The facility should eventually gain:

- generated current-revision artifact paths;
- a command to scaffold new test slices;
- historical timing trend compression;
- release budget enforcement by tier;
- changed-file fixture tests for every impact-map family;
- quarantine aging policy;
- optional stress tier that never runs in package release.
