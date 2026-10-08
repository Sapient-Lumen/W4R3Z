# 655. Release-gate failure locality, fail-fast default, and manifest-write quarantine

**Track:** Shared / Release engineering

This document records the v782 audit/reconstruction pass for release-gate control flow. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

The v781 timeout pass made each child check bounded, but the top-level runner still had two smaller release-control seams.

First, `docs/654-release-gate-subprocess-timeouts-and-ambient-environment-fail-closed-discipline.md` carried a stale internal anchor to a nonexistent release-gate checklist filename. The archive's backtick-reference checker caught it, which is good; the failure also shows why release hygiene docs must be treated as ordinary checked content rather than trusted commentary.

Second, `scripts/release_gate.py` kept running after a failed step. That behavior is useful for a diagnostic sweep, but it is a poor default for a release gate: the first actionable error can be delayed behind later checks, timeout symptoms can obscure the original cause, and a `--write-manifest` run could reach the manifest step after an earlier check had already proven the release invalid.

## Reconstruction rule

The release gate is now fail-fast by default.

- The first failed check returns a release-gate failure immediately.
- `--keep-going` is an explicit diagnostic mode for maintainers who want the larger failure set.
- The manifest step is quarantined from partial-failure runs: if any non-manifest check fails, the runner skips manifest write/check even under `--keep-going`.
- `--write-manifest` means "write the manifest after all other checks pass," not "repair the manifest despite failed checks."
- `ELECTION_STACK_RELEASE_STEP_TIMEOUT` must parse as a positive integer. Invalid timeout configuration is a release failure, not an ambient crash or silent default.

This makes the release gate a verdict path rather than a best-effort batch script.

## Reference-closure repair

The stale anchor in `docs/654-release-gate-subprocess-timeouts-and-ambient-environment-fail-closed-discipline.md` was repaired to point at the actual release-gate control doc: `docs/162-release-and-ci-evidence-pipeline.md`.

Maintainer rule: when a process doc backticks a numbered markdown file, it must use the exact canonical filename unless it intentionally names a range or family. Release engineering documents do not get to bypass the same link/reference controls they describe.

## Manifest quarantine policy

The manifest is evidence of a coherent archive state. It should not be regenerated around a known-bad tree.

For routine releases:

1. run `scripts/release_gate.py --quiet` or the equivalent CI job;
2. fix the first reported failure;
3. rerun until the non-manifest checks pass;
4. run `scripts/release_gate.py --write-manifest --quiet` only after the tree is coherent;
5. run the ordinary gate again if the release process needs an explicit manifest-check transcript.

For diagnostics, `--keep-going` may collect multiple failures, but its output is not a release verdict unless it exits cleanly.

## Compression posture

This revision adds one compact control document and a small runner patch. It does not add external sources, downloaded artifacts, schemas, or a new voter-facing surface. The useful invariant is centralized here: release-gate failure locality and manifest write quarantine should be enforced in the harness, not repeated as a bespoke warning in each checker.

## Future maintainer test

A release-gate change is suspicious if it makes any of these statements false:

- the first ordinary failure is visible without waiting for unrelated later checks;
- a timeout is a hard failure with the timed-out command visible;
- manifest writing is impossible after a prior check failure in the same run;
- invalid timeout configuration fails closed;
- process docs remain subject to doc-link and backtick-reference closure.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/163-artifact-reference-conventions.md`
- `docs/653-source-reference-parser-lockfile-closure-and-xref-reconstruction.md`
- `docs/654-release-gate-subprocess-timeouts-and-ambient-environment-fail-closed-discipline.md`
- `scripts/check_doc_backtick_refs.py`
- `scripts/release_gate.py`
