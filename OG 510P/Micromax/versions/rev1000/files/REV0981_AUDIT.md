# Rev0981 audit — a timeout that begins after start is not a start timeout

## Highest-risk finding

Rev0980's stopped-forkserver reproducer proved that every framed one-shot worker
could still freeze the caller before its advertised result deadline:
`Context.Process(...)` and `Process.start()` ran synchronously on the editor
thread. Filesystem, save, plugin-package, docs, project, and compatibility-regex
owners all inherited that gap.

## Substantive correction

- `create_one_shot_worker()` now returns a deferred process plan; both the real
  Process constructor and `start()` run in one deadline-owned starter.
- Gate waiting, starter handoff, construction, and start share one monotonic
  deadline rather than serial full-duration waits.
- At most one unresolved process start exists. Later calls remain finite and do
  not accumulate blocked launcher threads.
- When a deadline wins, ownership transfers to the starter. A late child is
  terminated/reaped, purpose-specific abnormal cleanup runs once, all endpoints
  close, and the gate releases.
- A starter completion timestamp closes the boundary race where `Event.wait()`
  expires just before a late completion becomes visible.
- Positive-timeout workers no longer fall back to `fork`; the helper thread
  makes that route unsafe by construction. Non-importable entrypoints retain the
  explicit direct path when their worker timeout is disabled.

## Adjacent audit/refactor

Fork-inherited monkeypatch tests were split into foreground TOCTOU tests and
worker-boundary mapping tests rather than preserving an unsafe implementation
merely for test injection. Shared real-spawn regressions still cover complete
frames, partial frames, crash, timeout, oversize, lingering workers, and handle
cleanup. The compatibility export's misplaced module docstring was corrected.
The repository structural audit now fails if deferred construction, the single
absolute startup deadline, completion-time witness, one-pending handoff, or
fork rejection disappears; this is a regression guard around the code path, not
an added runtime registry.

## Measured evidence

The updated fault injector observed raw `Process.start()` blocked for the full
0.35-second observation. The bounded call returned at 0.100173 seconds for a
0.10-second startup deadline, later cleanup completed after `SIGCONT`, and a
subsequent worker succeeded. A five-sample normal spawn benchmark was noisy
(rev0980 median 0.980162 s; rev0981 median 1.131326 s), while a representative
project-picker command was effectively unchanged in wall time (6.63 s versus
6.45 s). This revision fixes availability; it does not claim spawn acceleration.

## Residual risk

The tiny starter thread's own OS creation is not independently preemptible. A
platform start that never returns leaves one daemon starter and blocks future
starts only within their finite deadlines; resource reclamation cannot finish.
Late abnormal cleanup can also delay gate release. Spawn cost, child-side pickle
allocation, Windows/frozen execution, native crashes, syscalls, total memory,
and hostile code remain outside the claim. See
`docs/938-worker-start-deadline-single-pending-handoff.md`.
