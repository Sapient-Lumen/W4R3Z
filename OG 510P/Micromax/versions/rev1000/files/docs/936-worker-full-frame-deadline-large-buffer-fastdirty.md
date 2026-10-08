# Full-frame worker deadlines and large-buffer dirty cost (rev0979)

Rev0979 finishes the concrete worker-IPC hole left explicit by rev0978 and
removes a large-buffer per-keystroke tax. It does not add a worker registry,
process pool, rope, background service, or generic sandbox.

## Measured false deadline

Rev0978 corrected join-before-receive: a worker producing a large
`multiprocessing.Queue` result could wait for its feeder thread while the parent
waited for process exit. Receiving first fixed that ordering, but it did not make
the receive itself deadline-safe.

The adversarial baseline wrote a valid Queue/Connection length prefix declaring a
1 MiB payload, wrote one payload byte, and then stopped making progress.
`Queue.get(timeout=0.2)` remained blocked beyond an independent three-second
supervisor. The timeout had already done its only readiness poll. CPython's
`Queue.get()` then entered `_recv_bytes()`, whose `_recv(size)` loop performs
blocking reads until the declared body is complete. A parent-held writer can also
suppress EOF after the child exits. A timeout on message availability is not a
timeout on full-frame consumption.

This is not merely malformed-test traffic. Python documents that terminating a
process while it uses a Queue or Pipe can corrupt message boundaries. Worker
crash, cancellation, memory failure, or forced teardown can therefore leave the
same incomplete frame on an ordinary error path.

## One-shot framed result owner

Every affected Micromax one-result worker now uses one shared private channel:

1. `socket.socketpair()` creates connected parent and child endpoints without a
   Queue feeder thread;
2. the child serializes exactly one trusted result, checks a caller-selected
   byte ceiling, then sends `MXW1`, an unsigned 64-bit payload length, and the
   payload;
3. after `Process.start()` transfers the child endpoint, the parent closes its
   own writer copy so crash EOF remains observable;
4. the parent keeps the receiver nonblocking and reads header and body in bounded
   chunks, recomputing one absolute monotonic deadline before every `select()`;
5. the declared length is rejected before payload allocation when it exceeds the
   channel budget;
6. exactly one pickle must consume the declared frame; invalid or trailing
   serialized data is a protocol failure; and
7. one collector owns start failure, receive timeout, protocol failure,
   terminate/kill, optional clean-exit postcondition, abnormal cleanup, endpoint
   closure, and `Process.close()`.

The private one-shot channel matters. Forced teardown cannot corrupt a transport
that another operation will reuse, and there is no background feeder thread whose
lifetime must be separately cancelled or joined.

The migration covers contained stat, access, batched stat, read, and directory
listing; parent creation, freshness checks, atomic-write planning, residue
cleanup, and writes; plugin fingerprint and package snapshot capture; docs and
project scans; and the injected-context regex compatibility path. Read-only
filesystem and regex callers may accept a complete terminal result before a
short producer reap; save, plugin, docs, and project owners require a clean
terminal process. Existing operation-specific error taxonomies and containment
checks remain at their public seams.

Result ceilings are finite and purpose-sized. Metadata and save-control rows use
1 MiB, directory results use 8 MiB, docs/project scans derive finite limits from
their row/byte policies, bounded file reads add only transport overhead to their
public byte limit, and the intentionally unbounded direct read mode is still
capped by the shared 64 MiB one-result transport ceiling.

## Large-buffer dirty-tracking audit

Micromax's accurate dirty mode hashes the full logical document after each
mutation so undoing back to the saved bytes can clear `dirty`. That is useful for
ordinary files, but it is pure repeated work on a large buffer. In this Linux
cloudtainer, a many-short-line benchmark measured the rev0978 exact path at a
median **2.22 ms per mutation at 1 MiB** and **8.90 ms at 4 MiB**, before syntax,
selection projection, rendering, or terminal output.

At a saved baseline of 1 MiB or more, a newly opened buffer now receives an
ordinary visible buffer-local `fastdirty=true` option. Mutation becomes a sticky
boolean until save, avoiding the full-document hash in the typing path. The
choice is inspectable through the existing option model and reversible with
`setlocal fastdirty false`; buffers below the threshold retain exact
return-to-clean semantics. A user who globally enables `fastdirty` is not given a
redundant local override.

This follows a mature editor precedent rather than inventing hidden behavior:
micro documents `fastdirty` as the explicit accuracy/performance switch and
auto-enables it above 50 KB. Micromax uses a more conservative measured 1 MiB
threshold because its current Python exact path remains acceptable below that
point.

Clean-baseline and explicit exact-mode hashing still need exact logical bytes.
Large values now join the line vector in optimized native code, then encode and
hash in 64 KiB slices so no second full-document byte string is required. The
audit initially tried to stream every line in Python; that reduced one temporary
string too, but regressed exact mode to **21.9 ms at 1 MiB** and **149 ms at 4
MiB** on the same benchmark. That overengineered path was removed before
publication. The final exact path measured **2.23 ms** and **9.03 ms** respectively,
near rev0978 speed while retaining bounded UTF-8 byte chunks.

## Audit and deletion

- Replaced all one-shot `multiprocessing.Queue` result owners in the affected
  product modules with the shared framed collector.
- Removed the regex compatibility `Pipe.recv()` path because it had the same
  poll-then-block full-frame weakness.
- Centralized process construction so a failing `Process(...)` call closes both
  IPC endpoints.
- Removed duplicated filesystem result lifecycle and a repeated batched-stat
  status fragment.
- Added structural checks that fail if Queue/Pipe receives return to these
  owners, if size checks move after allocation, or if the large-buffer policy
  becomes hidden or loses its reversible exact mode.
- Added transport-level regressions for multi-megabyte success, incomplete frame
  timeout and EOF, oversize declarations, malformed/trailing pickle data,
  crash-without-result, non-exiting producers, and construction/start cleanup.

## Primary sources

- Python multiprocessing Queue implementation: the finite `get()` path polls
  once and then calls `_recv_bytes()`:
  https://github.com/python/cpython/blob/v3.13.5/Lib/multiprocessing/queues.py
- Python multiprocessing Connection framing: `_recv_bytes()` reads a declared
  length and `_recv()` loops until that body is complete:
  https://github.com/python/cpython/blob/v3.13.5/Lib/multiprocessing/connection.py
- Python multiprocessing guidance on Queue feeder threads, join ordering,
  corruption after termination, and trusted pickle transport:
  https://docs.python.org/3.13/library/multiprocessing.html#pipes-and-queues
- Python `socket.socketpair()` portability and endpoint semantics:
  https://docs.python.org/3.13/library/socket.html#socket.socketpair
- Python `select.select()` deadline behavior and Windows socket support:
  https://docs.python.org/3.13/library/select.html#select.select
- micro's documented `fastdirty` accuracy/performance policy and 50 KB automatic
  enablement:
  https://github.com/micro-editor/micro/blob/master/runtime/help/options.md
- micro's current buffer implementation applying `LargeFileThreshold` to
  `fastdirty`:
  https://github.com/micro-editor/micro/blob/master/internal/buffer/buffer.go

## Deliberately narrow claims

- Process construction and `Process.start()` still occur before the result
  deadline can preempt them.
- The child serializes a complete pickle before checking its serialized size; the
  byte ceiling bounds transport acceptance, not all child peak memory.
- Pickle is accepted only from a private Micromax-created worker endpoint. This
  is not safe against a compromised worker or interpreter.
- The default 64 MiB channel ceiling is finite but can still require multiple
  in-memory copies during serialization, receive, and decode.
- `socketpair()` plus `select()` is documented on Windows, but this revision's
  executable evidence is Linux-only.
- Automatic `fastdirty` deliberately trades exact undo-to-clean recognition for
  typing latency until the next save. The local option makes that trade visible
  and reversible.
- Exact dirty checks, initial line splitting, whole-buffer search, replacement
  plans, rendering, and many edit operations remain eager. This is not a rope,
  piece table, incremental hash tree, total-memory cap, syscall filter,
  native-crash boundary, or hostile-plugin sandbox.
