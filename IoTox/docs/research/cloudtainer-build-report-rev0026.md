# IoTox cloudtainer build report — rev0026

**Date:** 2026-08-18 America/New_York
**Version:** 0.26.0
**Revision:** rev0026
**Codename:** Message-Bound Local IPC Citadel
**Linked outer revision:** rev0013

## Outcome

rev0026 materially strengthens both owner-private Linux `AF_UNIX/SOCK_SEQPACKET` planes without
changing their payload encodings. The administrative control stream and the terminal controller
stream now authenticate the kernel-observed sender of every request and every response, reject all
ancillary capabilities, and bind long-lived terminal ownership to a process lifetime rather than to
an open file description.

The constructed boundary adds:

- one shared bounded `recvmsg(2)` ancillary parser;
- mandatory bidirectional `SO_PASSCRED`/`SCM_CREDENTIALS` evidence;
- runtime-probed `SO_PASSPIDFD`/`SCM_PIDFD` evidence when the host supports it;
- exact record-time PID/UID/GID comparison with connection-time `SO_PEERCRED`;
- terminal controller release on authenticated-process exit even when another process retains the
  connected descriptor;
- immediate closure and fail-closed rejection of every injected `SCM_RIGHTS` descriptor;
- a finite complete-request lease for `control.sock` clients; and
- exact active/stale/replacement inode ownership for the administrative socket pathname.

The direct registry grows from 303 to **313** checks. The final matrix passes GCC Debug, Clang Debug,
bounded GCC Release, Clang ASan+UBSan, GCC ThreadSanitizer, and three Clang static-analyzer lanes.

## Online primary-source review

The implementation review rechecked the following primary or first-party Linux references online on
2026-08-18:

- Linux `unix(7)`: <https://man7.org/linux/man-pages/man7/unix.7.html>
- Linux `recv(2)`/`recvmsg(2)`: <https://man7.org/linux/man-pages/man2/recv.2.html>
- Linux `pidfd_open(2)`: <https://man7.org/linux/man-pages/man2/pidfd_open.2.html>
- Linux socket implementation state: <https://github.com/torvalds/linux/blob/master/include/net/sock.h>
- Linux networking 2023 summary: <https://people.kernel.org/kuba/netdev-in-2023>

The relevant findings are bounded: `SO_PEERCRED` is connection-time evidence; `SO_PASSCRED` supplies
message-time sender credentials; `MSG_CTRUNC` reports lost ancillary evidence; `MSG_CMSG_CLOEXEC`
seals descriptors installed during receive; pidfds provide pollable process-lifetime identity; and
Linux 6.5 introduced sender-pidfd delivery through `SO_PASSPIDFD`/`SCM_PIDFD`.

These sources define kernel interfaces. They do not audit IoTox or establish that this construction is
a complete hostile-user boundary. The applied reasoning and nonclaims are retained in
`docs/research/message-bound-local-ipc-hardening-rev0026.md` and ADR 0076.

## Constructed local IPC boundary

### Shared record-security module

`src/local/seqpacket_security.cpp` now owns the security-sensitive record mechanics used by both local
protocols. Each receive allocates payload storage only to the protocol ceiling plus one
truncation-detection byte and uses a fixed 4096-byte ancillary buffer. The parser:

1. receives with `MSG_CMSG_CLOEXEC`;
2. rejects payload truncation and `MSG_CTRUNC`;
3. requires exactly one well-formed credential record when credentials are enabled;
4. requires exactly one sender pidfd when the runtime socket option was accepted;
5. rejects duplicate, malformed, unknown, and requirement-mismatched control records;
6. closes every delivered `SCM_RIGHTS` descriptor before rejecting the record; and
7. releases payload bytes to the protocol decoder only after the complete ancillary contract passes.

Listeners enable the options before bind/listen. Clients enable them before connect. Accepted sockets
verify option inheritance before consuming a record that may already be queued.

### Bidirectional process binding

Servers first record the connection-time peer tuple through `SO_PEERCRED`. Every request or terminal
record must then carry exact message-time PID/UID/GID evidence for the same process. This closes the
previous descriptor-handoff gap: a fork child or `SCM_RIGHTS` recipient cannot silently act as the
process that opened the connection merely because it possesses the same open file description.

Clients apply the same rule to responses. A fork-inherited server descriptor cannot forge a response
as the original server process, and response-side descriptor injection is closed and rejected before
decoding.

### Terminal process lifetime

The first valid terminal record binds the controller process. On this host, the kernel delivered an
`SCM_PIDFD` with the record; the server retains it and polls it beside the terminal socket and wake
descriptor. On supported older kernels where direct pidfd delivery is unavailable, the implementation
attempts `pidfd_open(2)` for the already authenticated PID.

Process exit releases the sole controller slot even if another process still holds or inherited the
connected socket. Every later record must continue to exact-match the bound process, and the pidfd is
rechecked before dispatch.

### Administrative request lease and pathname ownership

`ControlServer::Config::request_timeout` is a positive complete-record lease limited to 60 seconds.
The worker polls the accepted client and its stop wake descriptor together. A silent client therefore
loses the connection after a finite deadline rather than reserving the single worker indefinitely.

The control endpoint now requires an absolute pathname below a real owner-private parent, owner-only
socket permissions, and exact device/inode continuity. Startup probes an existing owned socket and
refuses to unlink a live listener, rechecks a stale candidate before removal, records the inode created
by bind, and removes only that exact inode during cleanup. A replacement socket installed at the same
pathname survives original-server shutdown. Clients verify type, ownership, mode, and the same inode
before and after connect.

## New adversarial evidence

Ten owned-registry checks were added:

1. a child cannot send a control request through its parent's connected descriptor;
2. a child cannot send a terminal record through its parent's controller descriptor;
3. a child cannot forge a control response through an inherited server descriptor;
4. request-side control `SCM_RIGHTS` is closed and rejected;
5. request-side terminal `SCM_RIGHTS` is closed and rejected;
6. response-side terminal `SCM_RIGHTS` is closed and rejected;
7. controller-process exit releases a terminal socket retained by another process;
8. a silent administrative client expires and a legitimate successor is admitted;
9. a second control server cannot remove an active listener; and
10. original-server shutdown preserves a different replacement socket inode.

The rights tests close the sender's original write endpoint and observe EOF only after the receiver has
closed the injected copy. Handler counters prove that rejected records are not dispatched.

## Compiler and execution matrix

```text
GCC 14.2 Debug warnings-as-errors configure/build:     PASS
GCC 14.2 Debug CTest:                                  14/14
Direct owned registry:                                 313/313
Clang 17 Debug warnings-as-errors configure/build:     PASS
Clang 17 Debug CTest:                                  14/14
GCC 14.2 Release warnings-as-errors bounded build:     PASS
GCC 14.2 Release CTest:                                14/14
Clang 17 ASan+UBSan warnings-as-errors build:          PASS
Clang ASan+UBSan owned registry shards:                16/16
Clang ASan+UBSan process lanes:                         4/4
Clang ASan+UBSan whole-binary lifecycle:                1/1
Clang ASan+UBSan product/analyzer lanes:                8/8
Clang ASan+UBSan total unique routes:                  29/29
GCC 14.2 ThreadSanitizer warnings-as-errors build:     PASS
GCC TSan owned registry shards:                        16/16
GCC TSan process lanes:                                 4/4
GCC TSan whole-binary lifecycle:                        1/1
GCC TSan product/analyzer lanes:                        8/8
GCC TSan total unique routes:                          29/29
Sanitizer runtime diagnostic scan:                     none
Clang static analyzer, seqpacket_security.cpp:         PASS
Clang static analyzer, control_socket.cpp:             PASS
Clang static analyzer, terminal_socket.cpp:            PASS
Python tool bytecode compilation:                      PASS
Ratox R7 analyzer self-test:                           PASS
Linux sender-credential/pidfd runtime probe:           PASS
Product identity:                                      IoTox 0.26.0 rev0026
```

The sanitizer presets split the same 313-check registry into sixteen deterministic shards. The 29
unique routes are those sixteen shards plus four separate process lanes, one whole-binary lifecycle
lane, and eight product/analyzer lanes. They are not 29 additional product checks.

Build invocations were deliberately resumed in bounded chunks when the execution wrapper ended a
single command window. Each final build graph then returned `ninja: no work to do`, and the normalized
build transcripts retain all successful chunks plus that completion proof.

### Host-capacity negative retained

One initial GCC Release attempt used `-j32`; the host killed one `cc1plus` process while compiling
`src/cli.cpp`. That log is retained as `gcc-release-build-overparallel-negative.log`. The same clean
configured graph completed without a source error under the repository's bounded `-j8` parallelism,
then passed all 14 Release CTest routes. The over-parallel result is classified as an environmental
capacity negative, not hidden and not promoted to a code failure or success.

## Qualification-host facts

```text
kernel: Linux 6.18.35 x86_64
CMake: 3.31.6
Ninja: 1.12.1
GCC: 14.2.0
Clang: 17.0.0
Python: 3.13.5
SO_PASSCRED: 16
SO_PASSPIDFD: 76
SCM_CREDENTIALS: 2
SCM_PIDFD: 4
runtime credential delivery: yes
runtime sender PID exact match: yes
runtime sender pidfd delivery: yes
cgroup filesystem: cgroup2fs, magic 0x63677270
/sys/fs/cgroup mount: ro,nosuid,nodev,noexec,relatime,nsdelegate
writable delegated subtree visible: no
```

The standalone kernel probe enabled both receive options on an owner-created seqpacket pair, sent one
record, and received the expected payload, credentials for the exact sender PID, and an `SCM_PIDFD`.
That proves the direct pidfd-delivery branch was available on this qualification host. It does not
qualify other kernels or libc/header combinations.

The cgroup mount remains read-only. Consequently, rev0025's positive delegated-cgroup lifecycle lane
still was not run on this host; no mock filesystem or invented success result was substituted. The
existing fail-closed and ordinary-path evidence remains green in the full regression matrix.

## Evidence inventory

Revision-owned evidence is retained under `artifacts/rev0026/`, including:

- clean configure logs and normalized complete build transcripts for five toolchain presets;
- CTest output for GCC Debug, Clang Debug, and GCC Release;
- verbose output for all 313 directly owned checks;
- ASan+UBSan and TSan shard/process/product route output and summaries;
- three static-analyzer logs and exit records;
- Linux socket-constant and sender-pidfd runtime probes;
- product identity, CLI help, Python compilation, and R7 analyzer self-test output;
- qualification-host facts and the sanitizer diagnostic scan;
- source-integrity and release-identity records;
- an exit-code inventory, validation summary, and SHA-256 manifest; and
- the retained host-capacity negative from the excessive Release parallelism attempt.

## Nonclaims and remaining work

rev0026 does not claim:

- cryptographic separation between processes that intentionally share a UID;
- denial of a new connection from a same-UID process where endpoint policy permits it;
- isolation from root, kernel compromise, ptrace-equivalent authority, or an equivalent daemon owner;
- a general fair or multiplexed administrative scheduler under hostile same-UID connection pressure;
- a namespace, sandbox, container, VM, mount allowlist, or complete syscall allowlist;
- PTY/controller continuity across daemon restart;
- automatic recovery of abandoned delegated-cgroup leaves after ungraceful daemon death;
- a positive delegated-cgroup lifecycle on this read-only qualification host;
- every target kernel, libc, service manager, LSM, filesystem, or local socket topology;
- public-network or two-physical-host R7 qualification;
- independent security audit, production certification, or production readiness.

The next local-IPC qualification work is a same-UID adversarial fairness review, restart behavior for
local controller state, and independent audit of all authority-bearing descriptor exports. The next
cgroup lane remains a genuine writable single-writer delegation. Public-network R7 qualification
remains a separate physical-host exercise with raw attested evidence.
