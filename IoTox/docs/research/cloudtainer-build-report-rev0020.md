# Cloudtainer build report — IoTox rev0020

**Revision:** rev0020
**Version:** 0.20.0
**Codename:** Restart Fence
**Outer linked revision:** rev0007
**Date:** 2026-08-17 America/New_York

## 1. Result

rev0020 completes the first deterministic-provider R6 restart/fault construction above rev0019's
private controller stream. The source builds under warnings-as-errors, the complete GCC Debug suite
passes 13/13, the direct registry passes 284/284, all 13 registered suites pass under Clang 17
ASan+UBSan in isolated lanes, the source-controlled controller and restart gates pass 1,000 and 100
consecutive process repetitions respectively, and the retained full-path R6 oracle passes against the
final product, mock transport, and PTY helper.

This is construction evidence, not a production remote-shell, public-network, power-cut, or complete
sandbox claim.

## 2. Product construction

### Signed host-incarnation lease

An enabled Ratox host now reserves one nonzero device-bound incarnation before constructing the live
service, terminal listener, or toxcore transport. Client-only activation remains lease-free.

The durable format is one exact 128-byte `IOTXRIN1` record containing format/algorithm bytes, the
stable Ed25519 device public key, a big-endian incarnation, its complement, and a signature over the
first 64 bytes. First allocation is random below the high bit; each successful successor advances
exactly once. Zero, wrong device, malformed record, signature/complement failure, and exhaustion fail
closed.

The default lane is `<savedata-parent>/ratox/incarnation.state`. Construction uses descriptor-relative
`openat`, `O_NOFOLLOW`, `O_CLOEXEC`, rejected `..`, a final same-euid exact-0700 directory, exact-0600
single-link regular lock/state files, nonblocking exclusive `flock`, and post-lock descriptor/path
identity revalidation. Existing unsafe permissions are rejected rather than repaired.

Commit uses a private exclusive temporary inode, exact metadata and size checks, file `fsync`, path
identity revalidation, descriptor-retained `renameat`, installed-path identity verification, directory
`fsync`, strict reopen, and signature verification. Every directory created by first-start traversal is
also fsynced after exact-mode enforcement, followed by an fsync of the containing directory entry before
descent. Keeping the temporary descriptor open through rename closes the same-owner substitution
interval that would exist if it were closed after the last pre-rename check.

### Authority and restart semantics

Agent route state now distinguishes:

```text
authenticated principal for this confirmed online epoch
current exact-head authority for an effect
```

The authenticated mapping may survive a signed revocation solely long enough to return one explicit,
replayable denied ATTACH/RESUME result. It cannot authorize OPEN, PTY creation, input, resize, close,
or any other effect. Every effect packet remains revalidated against the current signed ledger head.

Host status publishes only `ratox-host-incarnation` and `ratox-incarnation-lease-held`. Startup failure
cleanup releases transport, listener, service, PTY, and lease resources but preserves `phase=failed`
and its failure event instead of rewriting the runtime evidence to `stopped`.

### Local controller fault gate

The private terminal server now enforces a configurable first-OPEN lease (product default five
seconds, accepted range one millisecond through sixty seconds). A silent same-user connection receives
a typed timeout and cannot monopolize the sole slot.

While a controller is active, at most four contenders are consumed under one shared 20 ms grace. Only
their first canonical OPEN record is decoded; it is never dispatched. The server returns typed
`resource_exhausted` with the exact contender stream ID. Active-controller data/death is processed
before listener contention so a queued successor is not rejected on behalf of a dead controller.

DETACH now has a bounded two-phase close: final OUTPUT and DETACHED packets drain first, then the
connection accepts only cumulative OUTPUT_ACK records for a 1 ms through 5 s lease (250 ms by default).
Successors remain in the kernel backlog during that phase. Socket sends consume the remaining absolute
detach deadline rather than receiving a fresh timeout per packet, and post-DETACH effects are rejected
before they can reach the Agent handler.

### Mock and fault-injection fidelity

The exact c-toxcore double can reject a configured number of exact-byte Ratox packets with SENDQ and
requires retries to preserve the frozen bytes. Friend removal clears mock session, epoch, pending,
frozen-packet, and command state so friend-number reuse cannot inherit prior online-epoch evidence.

## 3. Source-controlled tests added

```text
tests/test_interactive_incarnation.cpp
tests/test_terminal_socket.cpp
tests/test_terminal_controller_process.cpp
tests/test_ratox_restart_process.cpp
```

The incarnation suite covers same- and cross-process exclusion, signed advancement, wrong identity,
tamper, malformed shape, wrong mode/type/owner assumptions available to the fixture, hard/symbolic
links, nested no-follow traversal, default path, wraparound, and lease release.

`iotox.terminal-controller-process` drives the installed CLI across winner/loser contention, abrupt
winner death, replacement resume, render-before-ACK, exact cumulative ACK, clean detach, and explicit
empty-server restart refusal.

`iotox.ratox-restart-fence-process` launches the shipped daemon with the exact mock provider and proves
one held signed record, contender exit 3, failed runtime projection, no contender increment, clean
release, and successor value exactly equal to the first value plus one.

## 4. Defects found and fixed during construction

1. A silent local connection could hold the only pre-OPEN controller slot indefinitely. A finite lease
   and typed timeout now bound it.
2. A contender could be disconnected before its typed busy packet was consumed. The bounded
   consume-and-deny path now preserves the exact stream identity without dispatch.
3. Listener readiness could be processed before active-controller death, falsely denying a valid
   replacement. Active terminal descriptors now have priority.
4. Revocation removed all route identity, preventing an explicit denial and making absence ambiguous.
   Authentication is retained separately from effect authority only for the denial path.
5. Friend-number reuse in the mock could retain prior epoch/session queues. Removal now scrubs every
   associated mock transport lane.
6. Cleanup after failed startup overwrote `phase=failed` with `stopped`. Cleanup now releases resources
   while preserving the failure projection.
7. Closing the temporary incarnation descriptor before rename left an unnecessary substitution
   interval. The descriptor now remains open through rename and installed-path verification.
8. Current one-binary version assertions still expected rev0019. They now require 0.20.0/rev0020.
9. First-start durability synchronized the final record but not every newly created directory name.
   Each new directory inode and containing entry is now synchronized in construction order.
10. Direct enabled-service callers inherited a reusable incarnation of one. The neutral service default
    is now the invalid zero sentinel; an enabled caller must inject an acquired nonzero lease.
11. Immediate close after DETACH could discard a final cumulative OUTPUT_ACK. A bounded ACK-only phase
    now commits ordered acknowledgements without permitting any new controller effect.

## 5. Validation

### GCC Debug warnings-as-errors

Toolchain:

```text
Linux x86_64 kernel 6.18.35
GCC 14.2.0
CMake 3.31.6
Ninja 1.12.1
```

Results:

```text
284/284 direct owned checks passed
13/13 default CTest targets passed sequentially
terminal controller process gate passed; 1,000/1,000 repeated runs passed
shipped-binary restart fence process gate passed; 100/100 repeated runs passed
```

The first complete CTest attempt used a stale `iotox_cli_process_tests` executable after source
version assertions changed. Its peer description already showed a successful 0.20.0/rev0020 result;
a complete rebuild relinked the fixture and the final 13/13 run passed. The stale-binary attempt is not
retained as final evidence.

### Clang 17 ASan+UBSan

Clang 17 built the complete product, exact doubles, 284-check registry, installed binary, and all
process fixtures with AddressSanitizer and UndefinedBehaviorSanitizer. Leak detection, strict string
checks, initialization-order checks, abort-on-error, stack traces, and halt-on-UB were enabled. The
unit/integration registry passed 1/1 and the remaining process/CLI targets passed 12/12 in isolated
CTest lanes, for an aggregate 13/13 with no sanitizer report.

### Retained full-path R6 oracle

A compiled full-path R6 oracle survived the earlier workspace reset while its source did not. It was
run against the final rev0020 `iotox`, final mock toxcore library, and final PTY fixture and reported:

```text
Ratox R6 separate-process reconnect, replacement, pressure, revocation, and restart gates passed
```

This oracle crosses the actual Agent, private controller stream, packet `0xA2`, mock Tox owner thread,
profile resolver, native PTY helper, reconnect, controller replacement, SENDQ retry, signed revocation,
explicit denial, daemon replacement, and stale-session refusal. Because the oracle source is not in the
packaged repository, it is retained as supplementary validation only; the controller and restart
process gates listed above are the source-controlled release gates.

## 6. Evidence files

```text
artifacts/rev0020/gcc-debug-build.log
artifacts/rev0020/focused-unit-integration.log
artifacts/rev0020/gcc-debug-ctest.log
artifacts/rev0020/terminal-controller-process.log
artifacts/rev0020/terminal-controller-process-1000.log
artifacts/rev0020/ratox-restart-fence-process.log
artifacts/rev0020/ratox-restart-fence-process-100.log
artifacts/rev0020/ratox-r6-full-path-oracle.log
artifacts/rev0020/clang-asan-ubsan-ctest.log
artifacts/rev0020/SHA256SUMS
artifacts/reports/validation-summary.txt
```

## 7. Research boundary

Primary Linux semantics were rechecked in `docs/research/sources.md` and applied in ADR 0068. In
particular, `O_CLOEXEC` avoids a multithreaded open/fcntl leak race; `O_NOFOLLOW` constrains the final
component of an open and descriptor-relative traversal is needed for the complete lane; `flock` is
advisory and attached to an open file description; rename replacement is atomic but durable commit
requires synchronization of the file and containing directory; and pathname check/use substitution is
the CWE-367 class. These references define platform behavior and do not review IoTox.

## 8. Nonclaims and next work

rev0020 does not prove public Tox bootstrap, NAT traversal, relay behavior, two-physical-host terminal
latency, hardware power-cut durability, rollback resistance against an equivalent owner or restored
snapshot, live PTY/controller-state survival across daemon restart, multi-controller policy, or full
namespace/cgroup/seccomp/LSM/filesystem confinement.

The next evidence phase is R7: complete-service testing on two physical hosts over observed direct UDP
and forced TCP, idle and beside 1/8/16/32/64 bulk streams, with latency, reconnect convergence,
CPU/RSS/context-switch, and power evidence. R8 remains focused review and production-support policy.
