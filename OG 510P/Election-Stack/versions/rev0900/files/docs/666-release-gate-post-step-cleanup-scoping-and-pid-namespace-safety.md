# 666 — Release-gate post-step cleanup scoping and PID-namespace safety

**Track:** Shared / Release engineering

This document records a v791 release-gate hardening pass. It is a maintainer-control document, not a new voter-facing evidence surface.

## Audit finding

The v788 release moved child-step output capture to files and added POSIX process-group cleanup so diagnostic slices would not hang on daemonized grandchildren. That cleanup used `killpg(pgid, 0)` after the named child had already exited to decide whether anything in the child process group remained.

That is too broad for post-step cleanup. In PID namespaces, supervised containers, or busy diagnostic environments, a process-group id can be projected or reused in ways that make a post-exit group probe less trustworthy than the original live child process handle. A release-gate diagnostic should clean up descendants of its own child step, not signal an unrelated process group after the child is gone.

## Reconstruction rule

Timeout handling still signals the live child process group while the named child process is known to exist.

Post-completion cleanup is narrower:

1. enumerate live Linux `/proc/<pid>/stat` entries;
2. parse each process's process group and session id;
3. keep only processes whose process group equals the child pid and whose session id equals the child pid;
4. signal those specific pids, first with `SIGTERM`, then with `SIGKILL` only for survivors.

On non-Linux POSIX platforms where `/proc` is unavailable, the post-completion sweep is skipped instead of using an unsafe broad group probe. This preserves the bounded-timeout behavior for live children while making the daemonization firewall conservative after the child has exited.

## Operator effect

The operator CLI is unchanged:

```bash
python3 scripts/release_gate.py --from-step 1 --to-step 20 --progress --profile --skip-manifest
```

A diagnostic slice should no longer terminate the runner or unrelated local processes merely because a process-group id is still observable after a child step exits.

## Compression posture

This revision changes the release-gate runner and adds this compact maintainer-control document. It does not add schemas, registries, downloaded external bodies, public-answer surfaces, or a new release-gate child step.

## Internal anchors

- `docs/162-release-and-ci-evidence-pipeline.md`
- `docs/657-release-gate-resumability-profiled-diagnostics-and-process-group-timeouts.md`
- `docs/661-release-gate-file-backed-child-capture-and-daemonization-firewall.md`
- `scripts/release_gate.py`
