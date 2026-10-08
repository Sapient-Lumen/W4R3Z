# Rev0979 audit — a deadline must own the entire frame

## Highest-risk finding

Rev0978 correctly received worker results before joining their producers, but
`multiprocessing.Queue.get(timeout=...)` was still not an end-to-end deadline.
CPython polls once, then performs a blocking length-framed receive. An incomplete
body caused by crash, kill, or corruption could therefore trap filesystem,
save, plugin, docs, project, or regex callers beyond their advertised timeout.
The adversarial baseline remained blocked past a three-second outer supervisor
although the Queue timeout was 0.2 seconds.

## Substantive correction

All affected one-result workers now publish one explicitly bounded frame over a
private socket pair. The parent incrementally reads header and body on a
nonblocking socket, recomputes one monotonic deadline before every wait, rejects
oversize declarations before growing the payload, decodes exactly one trusted
pickle, and owns every process/endpoint cleanup path. Closing the parent's writer
copy after start makes child crash visible as EOF. Save/plugin/docs/project
owners require a clean terminal producer; read-only filesystem and compatibility
regex callers may retain a complete result after bounded teardown.

## Adjacent audit/refactor

- removed duplicated Queue feeder cancellation/join code across product modules;
- centralized one-shot process construction and construction-failure endpoint
  cleanup;
- removed the regex `Pipe.recv()` bypass;
- deleted a duplicated stat-batch status fragment;
- added source audits preventing the old Queue/Pipe transports from re-entering;
- caught and removed this revision's own per-line exact-signature walker after a
  benchmark showed a 10–17× slowdown;
- stopped the generated code handoff from growing past 64 paths while retaining
  every current-revision surface; and
- shortened established decision prose back under its existing ceiling instead
  of expanding the registry budget.

## Waste corrected

Large opened buffers no longer hash every logical byte on every edit by default.
At 1 MiB and above the existing `fastdirty` option is installed locally and
visibly, turning dirty tracking into the intended sticky flag until save. The
user can restore exact behavior explicitly. Final exact hashing still avoids a
full encoded-byte allocation and remains near baseline speed.

The transport also removes Queue feeder threads, cancellation bookkeeping,
false retry after incomplete frames, and family-specific lifecycle variants.
This is less machinery at call sites and a stronger deadline, not a new registry.

## Residual risk

No claim is made for preemptible process construction/start, child-side
pre-serialization memory, hostile pickle senders, total process memory, syscalls,
native crashes, Windows execution evidence, arbitrary process trees, or hostile
plugin isolation. The 64 MiB default transport cap is finite but not small.
`fastdirty` trades undo-to-clean accuracy for latency until save, and other
whole-buffer operations remain eager. See
`docs/936-worker-full-frame-deadline-large-buffer-fastdirty.md`.
