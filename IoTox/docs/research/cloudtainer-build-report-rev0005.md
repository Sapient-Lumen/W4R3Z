# Cloudtainer build report — IoTox rev0005

**Date:** 2026-08-13  
**Evidence class:** local build and exact mock-ABI execution  
**Northstar:** one standalone-capable C++20 ratox successor binary

## Result

rev0005 turns the rev0004 two-process product shape into one public executable:

```text
iotox run ...       foreground device/network agent
iotox status        local control through the same executable
iotox peers         local peer projection
iotox file-send ... finite regular-file offer
iotox file-receive  explicit paused-offer acceptance
iotox files         transfer projection
```

Internal libraries, test executables, and loadable ABI mocks remain development artifacts. There is no `iotoxd` product target.

## Environment

The retained artifacts identify exact compiler and operating-system details in `artifacts/reports/build-info.txt`. The intended matrix is:

- GCC debug;
- GCC release;
- Clang debug;
- Clang AddressSanitizer plus UndefinedBehaviorSanitizer;
- GCC ThreadSanitizer;
- Clang libFuzzer smoke;
- Mutorr preservation build.

The cloudtainer has CMake, Ninja, GCC, and Clang. Shell network name resolution is unavailable, so no real c-toxcore source tree or binary could be fetched by the build scripts.

## Implemented in rev0005

### One product process

`iotox run` owns toxcore, the owner thread, savedata, runtime projection, local `SOCK_SEQPACKET` control socket, peer lifecycle, packet transport, and transfer manager. Every local command is another invocation of the same binary.

### Dual internal toxcore provider

The same `toxcore::abi::Api` table can be populated by:

- exact symbols loaded from an operator-supplied shared library;
- direct linked function addresses when CMake receives `IOTOX_TOXCORE_SOURCE_DIR`.

Upstream c-toxcore is configured as a static subproject with optional applications and toxav disabled. This is the standalone direction, although this environment could not execute it.

### Stronger owner boundary

The owner queue is bounded. A command timeout cancels only work that has not started. Mutation saves are separate from shutdown saves. Required semantic events are never silently discarded; bounded observational event loss is counted.

### Ratox-style peer surface

The private runtime tree publishes:

```text
self
status
peers/<public-key>/...
requests/<public-key>/...
transfers/<direction>-<friend>-<file>/...
events
control.sock
```

Friend-request and transfer records are constructed in private temporary directories and atomically renamed into view, so observers never see partially written records.

### Finite file transfer

A new C++ `FileTransferManager` consumes the c-toxcore 0.2.23 file-transfer API through the owner-thread seam. It handles finite regular files only and fails closed on:

- source symlinks;
- non-regular sources;
- oversized sources/offers;
- source mutation;
- destination collision;
- out-of-order or overrun receive chunks;
- pending-offer, active-send, and active-receive limits;
- malformed filenames and unsafe output projection.

Accepted incoming bytes first land in a private same-directory temporary file. Completion uses file and directory synchronization plus no-clobber publication.

### Mock fidelity additions

The loadable test library now models:

- incoming friend requests;
- friend acceptance, deletion, list, and savedata continuity;
- outgoing file offers and chunk requests;
- incoming paused offers and data delivery;
- c-toxcore's direction-distinct file handles;
- deterministic capture of sent bytes.

It remains an ABI/lifecycle fixture, not an implementation of Tox networking.

## Test inventory

The C++ runner reports:

```text
tests=44
failures=0
```

The default CTest graph contains seven entries, including a separate process fixture that launches the product binary. The process fixture exercises peer request/accept/remove/list, packet exchange, outgoing and incoming file transfer through public commands, runtime projection, clean shutdown, state persistence, restart identity continuity, and friend-list continuity.

The retained final matrix passes GCC debug/release, Clang debug, Clang ASan/UBSan, GCC TSan, the nine-entry Mutorr preservation build, and 5,000-run smoke executions for each of the two Clang fuzzers. The exact logs remain authoritative over this summary.

## Defects found during this revision

The test facility exposed and drove repairs for several real design defects:

1. Startup could report success immediately before the running flag became observable. The invariant is now tested.
2. A request directory could become visible before all files inside were complete. Request and transfer projection now publish transactionally.
3. Status could lag a successfully accepted request. Mutation completion now synchronizes the projection before returning.
4. The first mock file-number model did not match c-toxcore's direction distinction. The fixture now mirrors the upstream handle contract while product code treats handles as opaque.
5. Transfer failure cases needed explicit semantics for zero-byte sources, destination collision, source mutation, and offer floods. They now have compiled tests.
6. ThreadSanitizer found the mock reading process environment while a test changed it. The fixture now snapshots environment configuration into each mock `Tox` object before the owner thread starts. The repaired TSan lane passes all seven CTest entries.

## What is not proven

rev0005 does not prove:

- compilation against the actual c-toxcore headers and target;
- cryptographic or protocol correctness of toxcore;
- public bootstrap or DHT connectivity;
- NAT traversal;
- TCP-relay behavior;
- real peer discovery or connection timing;
- real file-transfer timing, pause, seek, reconnect, or congestion behavior;
- Tor-routed Tox or I2P-routed Tox;
- authorization-ledger enforcement;
- production hardening or target-device resource fitness.

The honest evidence label is **adapter-verified**. The next external gate is **source-linked and real-peer integration verified**.
