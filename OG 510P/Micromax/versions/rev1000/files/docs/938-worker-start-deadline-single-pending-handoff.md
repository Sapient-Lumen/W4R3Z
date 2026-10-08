# Finite worker start ownership without a process pool (rev0981)

Rev0980 proved a concrete freeze outside Micromax's otherwise bounded one-shot
worker lifecycle: a stopped private forkserver leaves
`multiprocessing.Process.start()` blocked before the framed-result deadline can
begin. Rev0981 owns that exact phase. It does not add a pool, broker process,
worker registry, or speculative execution service.

## Why this was the highest-risk unfinished boundary

Filesystem reads and writes, save planning, plugin package capture, documentation
catalogs, project scans, and the compatibility regex adapter all used one-shot
processes. Their result frames already had finite byte ceilings, incremental
reads, timeouts, and forced teardown, but all of that began only after
`Process.start()` returned. A launcher stall could therefore freeze the editor
thread indefinitely even when the operation advertised a timeout.

The rev0980 fault injector warmed a private forkserver, stopped the server with
`SIGSTOP`, and called `Process.start()` in another thread. The call remained
blocked for the full 0.35-second observation and resumed only after `SIGCONT`.
That is a supported-library control-path stall, not a hypothetical hostile
worker.

## The narrow owner

### Process construction is deferred

`create_one_shot_worker()` now creates the private bounded result channel and a
small immutable process plan. The context's `Process(...)` constructor and the
real `Process.start()` both execute inside the start owner rather than on the
editor thread. Construction failures therefore use the same taxonomy and
cleanup path as start failures.

### One absolute startup deadline

The start owner uses one monotonic deadline across:

1. waiting for an earlier unresolved start to clear;
2. creating and launching the one small starter thread; and
3. the process constructor plus `Process.start()`.

Gate waiting does not receive one timeout and process start another. The
starter records its own completion timestamp, so a result published just after
`Event.wait()` reaches the boundary cannot be accepted as on-time through a
scheduler race.

The result-frame deadline remains separate and begins only after an on-time
start. Startup delay therefore cannot silently consume the request's framed
receive budget, and a fast start does not enlarge the result budget.

### At most one unresolved starter

A module-local lock covers only process construction/start. It is released as
soon as an on-time start completes; workers may execute and return results
concurrently after that point. If a platform start call remains stuck, later
bounded operations wait only within their own startup deadline and do not
create another starter thread. This is a one-pending circuit breaker, not a
long-lived worker or authority registry.

### Deadline loss transfers cleanup ownership

The caller and starter never race the same process/channel after a timeout.
When the deadline wins before start completes, the caller marks the attempt
abandoned and returns `WorkerResultStartTimeoutError`, which is both a start
error and a timeout error for existing caller mappings. The starter remains the
sole owner. If the platform call later returns, it:

- records the child PID when available;
- closes the parent's inherited sender endpoint;
- terminates and reaps any late live child;
- runs the existing operation-specific abnormal cleanup exactly once;
- closes channel and process handles; and
- releases the one-pending gate.

If start completed after the deadline but before the caller observed the event,
the completion timestamp still classifies it as late; the caller retains sole
cleanup ownership in that already-complete race.

## Fork is deliberately rejected

The starter itself makes the parent process multithreaded. Initiating POSIX
`fork` from that helper would revive the lock-inheritance hazard this subsystem
exists to avoid. Deadline-owned workers therefore require `spawn` or
`forkserver`. A non-importable `python -c`, stdin, or REPL entrypoint fails
closed for positive-timeout work and can still select the existing explicit
nonpositive direct path. Embeddings may provide a compatible spawn-style
context; an explicit fork context is rejected before mutation.

## Fault-injection evidence

The revised `tools/reproduce_process_start_stall.py` performs raw and bounded
passes against the same private stopped forkserver. One Linux cloudtainer run
observed:

- raw `Process.start()` still blocked throughout **0.35 s** and completed in
  **0.364652 s** only after `SIGCONT`;
- the Micromax caller returned in **0.100173 s** against a **0.10 s** startup
  deadline;
- the late starter finished cleanup after the server resumed; and
- a subsequent one-shot worker completed, proving the gate was released.

Deterministic tests separately cover blocked constructor, blocked start, retry
circuit breaking, late child termination, exact abnormal cleanup, one absolute
deadline across gate and start, and rejection of a completion timestamp after
the deadline.

## Latency audit

This change targets availability, not spawn acceleration. Five fresh
spawn-worker samples on this host measured a rev0980 median of **0.980162 s**
and a rev0981 median of **1.131326 s**. The individual samples overlapped and
are too few for a throughput claim. A real project-picker journey measured
**3.68 s** test-call time in the rev0980 tree and **4.06 s** in rev0981; complete
command wall time was **6.63 s** versus **6.45 s**. The honest conclusion is
that the extra thread/lock handoff is small relative to fresh-interpreter cost,
not that startup became faster.

Repeated spawn-heavy modules remain unusually slow in this instrumented
cloudtainer and can exceed a coarse aggregate test timeout even while isolated
families pass. Rev0981 does not hide that cost behind a resident process.

## Audit/refactor consequences

- All one-shot worker families retain one shared construction/start/result/
  teardown owner rather than implementing purpose-specific starter threads.
- The legacy single-threaded `fork` fallback and native-task counter are removed;
  once start is delegated, that fallback is internally contradictory.
- Tests that previously inherited monkeypatches through `fork` now separate
  foreground TOCTOU behavior from worker-boundary error projection. Real spawn
  tests still exercise frame transport, timeout, crash, oversize, and forced
  teardown.
- The compatibility editor export now has a real module docstring and exposes
  the startup timeout constant and start-timeout taxonomy.
- `mxaudit` now treats deferred construction, one absolute startup deadline,
  completion timing, late ownership transfer, and fork rejection as one
  executable structural boundary, preventing a future refactor from restoring
  the pre-result freeze while its focused unit tests are omitted.

## Primary sources checked 2026-07-19

- Python 3.14.6 multiprocessing contexts, start methods, `Process.start()`, and
  library context guidance:
  https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods
- Python 3.14.6 thread join/daemon lifecycle:
  https://docs.python.org/3/library/threading.html#thread-objects
- CPython 3.14.0 `BaseProcess.start()`, which calls the platform `_Popen` path
  without a timeout parameter:
  https://github.com/python/cpython/blob/v3.14.0/Lib/multiprocessing/process.py
- CPython 3.14.0 POSIX spawn launcher:
  https://github.com/python/cpython/blob/v3.14.0/Lib/multiprocessing/popen_spawn_posix.py
- CPython 3.14.0 forkserver launcher and server connection path:
  https://github.com/python/cpython/blob/v3.14.0/Lib/multiprocessing/popen_forkserver.py

## Deliberately narrow claims

- Python/OS creation of the small starter thread itself has no independently
  preemptible API. Rev0981 owns the reproduced process constructor/start stall
  after that handoff; it does not claim arbitrary kernel thread creation is
  bounded.
- A permanently stuck platform start leaves one daemon starter and the gate
  occupied. The editor call and later retries remain finite, but reclamation
  waits for the platform call to return. Python documents daemon threads as
  abruptly stopped at interpreter shutdown, so late cleanup is not a crash- or
  power-loss transaction.
- Operation-specific abnormal cleanup still runs synchronously in the late
  owner. A defective cleanup callback can delay gate release, although callers
  and retries retain finite startup waits.
- The start gate briefly serializes process starts. It does not cap running
  workers after start, provide fairness, or improve fresh-interpreter latency.
- No Windows execution, Job Object tree ownership, frozen-executable support,
  total-memory cap, child-serialization cap, syscall filter, native-crash
  container, hostile-worker pickle boundary, or complete-suite claim is added.
