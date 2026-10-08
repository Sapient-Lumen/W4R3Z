# 657 — Release-gate resumability, profiled diagnostics, and process-group timeouts

**Track:** Shared / Release engineering

This document records the v785 reconstruction pass for release-gate operability in constrained, offline, or long-running environments. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

The v781–v784 release-gate repairs made child checks bounded, fail-fast, documented, and less subprocess-heavy inside the largest example-packet lanes. The remaining seams were the top-level diagnostic path itself and one operator-tools smoke lane that still spawned many short-lived Python interpreters for repository-local card CLIs.

The authoritative gate now contains more than one hundred child steps. Many are intentionally small, but they repeatedly load the same archive tree, registries, and markdown files. In a slow filesystem, a remote shell, or a short execution window, an ordinary full run can become hard to inspect even when no individual check is wrong. The operator sees either no output under `--quiet`, or only completed-step output after each child exits. That makes a stalled or merely slow run difficult to localize.

A second seam was timeout cleanup. The prior runner used a per-step timeout, but a timed-out child that spawned helper processes could leave descendants alive long enough to keep pipes open or contaminate the next diagnostic. That is an operability hazard: a release-gate timeout must be a hard local verdict for that step, not a partial parent-process kill.

A third seam was manifest discipline during partial diagnostics. Maintainers need to run a contiguous slice or a single named step while repairing a release. That must not create a path where a partial pass rewrites `MANIFEST.sha256` and looks like a release verdict.

## Reconstruction rule

`scripts/release_gate.py` remains the authoritative runner, and the full release gate remains the only release verdict. The runner has explicit diagnostic controls for locality:

- `--list` prints the numbered child-step inventory.
- `--from-step` and `--to-step` run a contiguous numbered or named slice.
- `--only` runs a comma-separated set of numbered or named child steps.
- `--skip-manifest` lets full diagnostic runs avoid the final manifest check/write.
- `--profile` prints elapsed time for completed child steps.
- `--progress` prints a child step before it starts, so the current hang location is visible.
- `--step-timeout` provides a one-invocation timeout override without mutating the ambient environment variable.

Partial runs are explicitly diagnostic. `--write-manifest` is rejected when `--only`, `--from-step`, or `--to-step` is present. A manifest rewrite remains valid only after the full non-manifest gate succeeds.

## Process-group timeout rule

Each child step now runs in its own process session on POSIX systems. If a timeout fires, the runner terminates the process group, escalates if needed, then reports the timed-out command and elapsed time. This closes the helper-process seam: a checker may use subprocesses internally, but it does not get to outlive a failed release-gate step.

The timeout rule is still fail-closed:

1. invalid timeout configuration is a release failure;
2. a timed-out step is a release failure;
3. timeout overrides are explicit, local, and positive integers;
4. operators should use longer timeouts only to inspect a slow known-good step, not to normalize a hang.

## Diagnostic transcript rule

A useful diagnostic transcript should answer three questions without rerunning the whole gate blindly:

- Which exact child step was running when the failure or stall occurred?
- How long did completed steps take on this machine?
- Was the manifest intentionally skipped because the run was only a slice?

The new controls answer those questions while preserving the full-gate invariant. For example, a maintainer may run a slow section with `--from-step 70 --to-step 90 --skip-manifest --profile --progress`, repair any reported issue, and then return to the full gate for the release verdict.

## Operator-tools smoke rule

`scripts/check_operator_tools_smoke.py` now invokes repository-local Python card CLIs through an isolated in-process argv/stdout/stderr frame. `tools/evidence_object_card.py` likewise dispatches specialized card renderers in-process instead of spawning another interpreter. The observable CLI contract remains the same, but the smoke lane no longer pays interpreter-startup cost for every card assertion and no longer leaks successful card output into the gate transcript.

## Local transcript packaging rule

Top-level `*.log` files are operator-local diagnostic transcripts, not normative release content. v785 removes the stale empty gate transcripts that had been sealed into the previous manifest and aligns manifest generation, deterministic ZIP construction, and cache-artifact checking so top-level logs do not silently become archive payload.

## Compression posture

This revision changes the release harness and records one compact control document. It does not add external sources, downloaded bodies, schemas, registries, or a new public-answer surface. The useful invariant is procedural: release-gate diagnostics should be local and bounded, while release authorization remains full-gate and manifest-quarantined.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/654-release-gate-subprocess-timeouts-and-ambient-environment-fail-closed-discipline.md`
- `docs/655-release-gate-failure-locality-failfast-and-manifest-write-quarantine.md`
- `docs/656-release-gate-inventory-doc-coverage-and-packaging-scope-firewall.md`
- `scripts/release_gate.py`
- `scripts/build_manifest.py`
- `scripts/build_release_zip.py`
- `scripts/check_no_cache_artifacts.py`
- `scripts/check_operator_tools_smoke.py`
- `tools/evidence_object_card.py`
