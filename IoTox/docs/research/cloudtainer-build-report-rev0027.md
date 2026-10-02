# IoTox cloudtainer build report — rev0027

**Date:** 2026-08-18 America/New_York
**Version:** 0.27.0
**Revision:** rev0027
**Codename:** Process-Pinned Bounded Fair Local IPC Citadel
**Linked outer revision:** rev0014
**Qualified source commit:** `c4c4e70518dde3051d5aaee68215040a74d862fa`

## Outcome

rev0027 removes the two remaining serial same-UID local-admission waits identified after rev0026 and
pins three connection-lifetime decisions to the exact connecting process where Linux exposes
`SO_PEERPIDFD`.

The administrative `control.sock` worker is now one bounded readiness multiplexer over its listener,
stop event, pending request sockets, and optional connection pidfds. Silent peers retain independent
complete-record leases and can no longer serialize ready requests behind one accepted descriptor.
Global and exact-credential-tuple per-process quotas, accept-refill limits, and handler-work limits
bound descriptor ownership and work per cycle.

The terminal server now maintains a bounded nonblocking contender set while an active stream is live.
Silent contenders expire independently without pausing active input, outbound draining, owner-pidfd
handling, or wake processing. Contenders may be decoded only far enough to correlate a busy response;
they never enter the controller state machine.

On supporting kernels, the control server pins every accepted request peer, the control client pins the
exact accepting server process, and the terminal server pins the active connection before its first
`OPEN`. A descriptor inherited or transferred to another process therefore cannot preserve these
pre-record waits after the exact connector exits. rev0026's mandatory message-bound credentials,
optional sender pidfds, ancillary-rights rejection, and post-`OPEN` terminal controller fence remain
in force.

The direct owned registry grows from 313 to **322** checks. The qualified matrix passes GCC Debug,
Clang Debug, GCC Release, Clang ASan+UBSan, GCC ThreadSanitizer, and three Clang static-analyzer lanes.

## Online primary-source review

The implementation and final review rechecked these primary or first-party Linux references online on
2026-08-18:

- Linux UAPI socket constants:
  <https://github.com/torvalds/linux/blob/master/include/uapi/asm-generic/socket.h>
- Linux generic socket option implementation, including `SO_PEERPIDFD` and no-peer `ENODATA`:
  <https://github.com/torvalds/linux/blob/master/net/core/sock.c>
- Linux Unix-domain socket implementation:
  <https://github.com/torvalds/linux/blob/master/net/unix/af_unix.c>
- Linux pid object and pidfd implementation:
  <https://github.com/torvalds/linux/blob/master/kernel/pid.c>
- Linux `pidfd_open(2)`:
  <https://man7.org/linux/man-pages/man2/pidfd_open.2.html>
- Linux `poll(2)`:
  <https://man7.org/linux/man-pages/man2/poll.2.html>
- Linux networking maintainer's 2023 interface summary:
  <https://people.kernel.org/kuba/netdev-in-2023>

The bounded findings are that `SO_PEERPIDFD` yields a process handle associated with an attached socket
peer; the generic socket implementation returns `ENODATA` when no peer process is attached; pidfds are
pollable lifetime objects; and one poll cycle can report socket data, hangup, and pidfd exit together.
IoTox therefore makes record-versus-exit ordering an explicit protocol decision rather than relying on
poll-array order.

For one-shot administrative requests and responses, a complete readable seqpacket record wins over a
simultaneous peer-exit notification and must still pass the complete rev0026 sender-evidence contract.
For terminal command dispatch, the bound controller process must remain live immediately before the
handler is invoked. Unsupported-option results retain the finite credential-and-lease compatibility
path; `ENODATA`, `ESRCH`, malformed lengths, negative descriptors, and unexpected errors do not become
silent success.

These references define kernel interfaces. They do not audit IoTox, prove every scheduling interleaving,
or establish a complete hostile-user or production boundary. Applied reasoning is retained in ADRs
0077 and 0078 and the two rev0027 research notes.

## Constructed local IPC boundary

### Multiplexed administrative admission

`ControlServer::Config` now validates and bounds:

```text
request timeout                         default 5000 ms, finite
maximum pending clients                 default 32
maximum pending clients per process     default 4
maximum accepts per refill interval     default 8
maximum handled requests per cycle      default 8
admission refill interval               default 1 ms
```

The worker reserves its bounded client and poll storage before entering the service loop and contains
those reservations inside the worker's exception boundary. Each accepted client owns one nonblocking
seqpacket descriptor, exact connection PID/UID/GID, an optional connection pidfd, an independent
absolute deadline, and removal state. Listener acceptance, request handling, expiration, peer exit,
and stop wakeups are all performed through one bounded loop.

A best-effort overload response may decode an already queued record solely to preserve correlation. An
over-quota request never reaches the administrative handler. Admission accounting compares the full
connection credential tuple rather than PID alone. That is a fairness key, not a cryptographic
principal.

### Nonblocking terminal contenders

While a terminal stream is active, the server retains at most:

```text
maximum pending contenders              default 16
maximum contenders per process          default 4
maximum accepts per refill interval      default 4
maximum contender records per cycle      default 8
contender first-record lease             default 20 ms
```

The active stream, sender-process pidfd, listener, wake descriptor, and bounded contender descriptors
share the readiness cycle. Active stream work is serviced before contender acceptance/decoding.
Contender deadlines are independent; silent peers do not create a shared grace sleep. Complete
contender records are authenticated and decoded only to return a correlated busy result, then closed.
DETACH continues to suppress new acceptance during its bounded `OUTPUT_ACK` drain.

### Exact connection-process lifetime

The shared local security layer runtime-probes `SO_PEERPIDFD` and returns an RAII-owned close-on-exec
pidfd when supported. Three paths consume it:

1. **Pending control request:** peer exit without a readable request releases the slot immediately,
   even when another process retains the accepted socket.
2. **Control response wait:** exact accepting-server exit without a readable response returns
   unavailable promptly, even when another process retains the server endpoint.
3. **Pre-`OPEN` terminal connection:** connector exit releases the sole active slot before the full
   open lease, even when the descriptor survives elsewhere.

The first authenticated terminal record still binds the sender process through rev0026's delivered
`SCM_PIDFD` or checked `pidfd_open` fallback. Subsequent terminal records must match the connection and
bound sender credentials, and handler dispatch remains fenced by live-process evidence.

### Compatibility and error surface

Build headers or kernels without `SO_PEERPIDFD` retain mandatory `SO_PEERCRED` plus per-record
`SCM_CREDENTIALS`, optional sender-pidfd evidence, finite leases, quotas, and exact socket-inode
ownership. That compatibility path is explicitly weaker against retained pre-record descriptors but
remains bounded.

`ENOPROTOOPT`, `EINVAL`, and equivalent unsupported-option results mean the optional capability is
absent. An unattached peer (`ENODATA`) is unavailable identity; an already vanished peer (`ESRCH`) is
unavailable; malformed output length, negative descriptors, and all unexpected failures are rejected.
Every acquired descriptor is made close-on-exec and RAII-owned.

## Adversarial evidence added

Nine direct checks account for the registry increase from 313 to 322:

1. silent administrative peers do not serialize a ready request behind their leases;
2. one process cannot exceed its pending-control quota;
3. multiple admitted silent control leases expire independently;
4. the global pending-control ceiling rejects and later recovers;
5. connector exit releases a retained silent control socket through its connection pidfd;
6. the control client abandons a retained endpoint after exact server-process exit;
7. silent terminal contenders do not delay active-stream request/response work;
8. one process cannot exceed its terminal-contender quota; and
9. pre-`OPEN` connector exit releases an inherited terminal socket before its lease.

The existing rev0026 fork-inherited sender, response-forgery, descriptor-injection, terminal
post-`OPEN` pidfd, request-lease, socket-inode, and process-boundary cases remain green.

## Validation matrix

All compiler builds retain the project's warnings-as-errors surface. The qualified source commit is
`c4c4e70518dde3051d5aaee68215040a74d862fa`; the later evidence/report commit changes no product or
test source.

### Native and optimized builds

- **GCC 14.2.0 Debug:** configured tree complete; final Ninja no-work proof passed; all **14/14**
  default CTest routes passed.
- **Direct GCC Debug registry:** `tests=322 selected=322 shard=0/1 failures=0`; three independent
  full-registry processes each produced 322 PASS records and the same zero-failure summary.
- **Clang 17.0.0 Debug:** affected source rebuilt with warnings as errors; final Ninja no-work proof
  passed; all **14/14** default CTest routes passed.
- **GCC 14.2.0 Release:** affected source rebuilt and linked under optimization with warnings as
  errors; final Ninja no-work proof passed; all **14/14** default CTest routes passed.

### Dynamic sanitizers

- **Clang ASan+UBSan:** complete configured build passed. Registry shards 1–13 and 14–16 passed in
  bounded invocations, followed by all 13 process/product routes: **29/29 unique routes**. No retained
  AddressSanitizer or UndefinedBehaviorSanitizer diagnostic signature was found.
- **GCC ThreadSanitizer:** a fresh `gcc-tsan` configuration was completed, then the final build was
  finished by one isolated builder and confirmed by a no-work Ninja proof. The complete configured
  suite passed: 16 owned-registry shards plus 13 process/product routes, **29/29 unique routes**. No
  retained ThreadSanitizer diagnostic signature was found.

The command harness imposes a finite per-invocation output window. Long compilation was therefore
resumed from Ninja's dependency graph, and the sanitizer registry was sharded by the project's own
configured test surface. Only completed commands with explicit zero exits are retained as positive
evidence. Interrupted diagnostic logs and evidence from the predecessor checkout are excluded.

### Static and auxiliary validation

- Clang static analyzer: no findings in `seqpacket_security.cpp`, `control_socket.cpp`, or
  `terminal_socket.cpp`.
- Python bytecode compilation: all `tools/*.py` passed.
- Ratox R7 analyzer self-test: passed in every default/product suite.
- Product identity: `IoTox 0.27.0 rev0027`.
- Runtime `SO_PEERPIDFD` probe: a connected seqpacket peer returned an `anon_inode:[pidfd]`
  descriptor with `FD_CLOEXEC`; it was not readable while the peer lived, became readable after the
  exact connector exited, and an unattached socket returned `ENODATA`.
- Source integrity: `git diff --check` passed, the tracked product worktree was clean before evidence
  addition, and all five configured build trees ended in `ninja: no work to do`.

## Qualification-host facts

```text
kernel: Linux 6.18.35 x86_64
CMake: 3.31.6
Ninja: 1.12.1
GCC: 14.2.0
Clang: 17.0.0
Python: 3.13.5
SO_PEERPIDFD: 77
runtime connected-peer pidfd: yes
runtime pidfd close-on-exec: yes
runtime unattached-peer result: ENODATA
```

This host proves that the direct connection-pidfd branch is available here. It does not qualify older
kernels, different build headers, every Unix-socket topology, or a target production fleet. The
qualification host's cgroup-v2 mount remains outside this revision's positive writable-delegation
claim; no synthetic positive was substituted.

## Evidence inventory

Revision-owned evidence is retained under `artifacts/rev0027/`, including:

- GCC Debug, Clang Debug, and GCC Release configure/build and grouped CTest logs;
- the complete direct 322-check registry transcript;
- Clang ASan+UBSan build and all 29 configured routes;
- isolated GCC TSan configure/build and all 29 configured routes;
- three Clang static-analyzer logs and exits;
- product identity, Python compilation, analyzer self-test, host facts, and the runtime
  `SO_PEERPIDFD`/`ENODATA` probe;
- online research source inventory, validation summary, source-integrity record, exit-code inventory,
  and SHA-256 manifest.

The qualified source commit precedes the evidence-only report commit. The repository datacube names
and verifies the final clean commit and includes complete reachable Git history, allowing the source
qualification boundary and evidence addition to be inspected separately.

## Nonclaims and remaining work

rev0027 does not claim:

- cryptographic authorization or isolation between processes intentionally sharing one UID;
- starvation freedom against an unlimited coalition of same-UID processes creating distinct process
  identities or continuously refilling accepted work;
- callback preemption after a handler has begun executing;
- a namespace, container, VM, LSM, complete syscall allowlist, or traffic-isolation boundary;
- PTY/controller continuity across daemon restart;
- crash-restart collection of every abandoned delegated-cgroup leaf;
- a positive delegated-cgroup lifecycle on this read-only qualification host;
- every target kernel, libc, service manager, filesystem, scheduler, or local socket topology;
- public-network or two-physical-host Ratox R7 qualification;
- independent security audit, production certification, or production readiness.

The next local-IPC work is an independent authority-bearing descriptor audit, callback execution-budget
or worker-isolation design, and target-kernel qualification of both the `SO_PEERPIDFD` and bounded
fallback paths. Public-network R7 and writable delegated-cgroup qualification remain separate physical
host exercises with raw attested evidence.
