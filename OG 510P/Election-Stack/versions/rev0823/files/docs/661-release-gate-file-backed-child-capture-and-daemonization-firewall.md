# 661 — Release-gate file-backed child capture and daemonization firewall

**Track:** Shared / Release engineering

This document records a v788 release-gate hardening pass discovered while running long diagnostic slices. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

`docs/657` added process-group timeouts and resumable release-gate slices, but the runner still captured child stdout/stderr through pipes. Pipes are convenient, but they have an avoidable failure mode: if a child process exits after leaving a descendant with the inherited pipe open, the parent can wait for pipe EOF even though the named child has already ended. That makes a diagnostic slice look like a stuck release check and can hide the actual step boundary.

Release-gate children should not daemonize, and the gate should not depend on pipe EOF from descendants to finish a step.

## Reconstruction rule

`scripts/release_gate.py` now uses file-backed child output capture for each step:

1. child stdin is `DEVNULL`;
2. child stdout/stderr are temporary files, not pipes;
3. each child runs with `cwd` pinned to the repository root;
4. timeout handling still terminates the child process group;
5. after a normally completed POSIX child, the gate also performs best-effort process-group cleanup for descendants that outlived the named step.

The public CLI contract is unchanged: `--quiet`, `--profile`, `--progress`, `--only`, `--from-step`, `--to-step`, `--skip-manifest`, `--keep-going`, and `--write-manifest` keep the same meaning.

## Operator effect

The release gate now treats background descendants as a local hygiene fault to clean up, not as a reason for the parent runner to block on inherited output pipes. This improves the diagnostic value of range runs such as:

```bash
python3 scripts/release_gate.py --from-step 71 --to-step 85 --skip-manifest --profile --progress
```

The full-gate rule remains unchanged: only an unsliced run may perform the final manifest check or write.

## Compression posture

This revision changes one stdlib runner and adds one compact maintainer-control document. It does not add schemas, registries, downloaded bodies, or a new public-answer surface.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/657-release-gate-resumability-profiled-diagnostics-and-process-group-timeouts.md`
- `scripts/release_gate.py`

## v791 post-step cleanup note

`docs/666-release-gate-post-step-cleanup-scoping-and-pid-namespace-safety.md` narrows post-completion daemonization cleanup. Timeout handling may still signal a live child process group, but after a child exits the runner enumerates matching process-group/session members and signals those pids directly instead of probing a broad `killpg` target.
