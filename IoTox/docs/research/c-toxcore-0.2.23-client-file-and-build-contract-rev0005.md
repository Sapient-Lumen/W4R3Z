# c-toxcore 0.2.23 client, file-transfer, and build contract — rev0005

**Status:** primary-source implementation research  
**Reviewed:** 2026-08-13  
**Target:** c-toxcore tag `v0.2.23`  
**Purpose:** constrain the ratox-successor implementation before real-network integration

## Sources reviewed

- Public client API: https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
- Upstream CMake: https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/CMakeLists.txt
- Release record: https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
- Ratox implementation used for interface comparison: https://raw.githubusercontent.com/pranomostro/ratox/master/ratox.c

The code in rev0005 was written against the declarations and behavioral comments in these exact upstream files. The cloudtainer did not compile or execute the upstream library. Claims below are therefore source-contract findings unless explicitly marked as mock-tested IoTox behavior.

## Release posture

c-toxcore 0.2.23 was released on 2026-06-03. The release notes describe fixes for critical bugs found during a manual audit. IoTox should pin a reviewed revision, preserve the exact source/archive digest, and retain the ability to update toxcore independently of application protocol changes.

The source-linked path records:

```text
c-toxcore-0.2.23.tar.gz
sha256=b0349f4829d3d1699a77e199850f870f48d376e2baaf2c69d27b28571c498cfe
```

The digest was computed from the release-tag archive fetched through the available file-transfer channel. Shell DNS was unavailable, so the archive is not embedded in the cube and the full source-linked build remains externally unverified.

## Build contract

The upstream CMake project defines a `toxcore_static` target when static output is enabled. Its configurable build surface permits IoTox to disable unrelated programs and optional subsystems:

```text
BUILD_TOXAV=OFF
MUST_BUILD_TOXAV=OFF
BOOTSTRAP_DAEMON=OFF
DHT_BOOTSTRAP=OFF
BUILD_FUN_UTILS=OFF
BUILD_FUZZ_TESTS=OFF
BUILD_MISC_TESTS=OFF
AUTOTEST=OFF
UNITTEST=OFF
ENABLE_SHARED=OFF
ENABLE_STATIC=ON
```

rev0005 accepts a pinned source tree through `IOTOX_TOXCORE_SOURCE_DIR`, adds it as a CMake subdirectory, requires the `toxcore_static` target, and links it into the one public `iotox` executable. In that mode the linked provider populates the same narrow function table used by the runtime-loaded provider.

This creates two provider modes without two products:

```text
source-linked provider    intended standalone/package route
runtime-loaded provider   exact mock tests and integration research
```

The runtime provider is not intended to force ordinary owners to locate a matching shared library.

## Tox object ownership

The public API repeatedly states that Tox instances are not generally thread-safe and that calls should be serialized. rev0005 therefore preserves one owner thread for each `Tox*` instance. No application service calls toxcore directly.

The owner accepts bounded work, owns all callback registration and iteration, and translates toxcore state into bounded C++ events. A timeout may cancel only work that has not begun. Once work begins, the caller cannot receive a false promise that it did not execute.

Required semantic events—friend requests, friendship mutation, control packets, and transfer lifecycle—must not be silently discarded. When the bounded event queue contains only required events, the owner applies backpressure. Observational events may be evicted and increment an audit counter.

## Friendship contract

The c-toxcore client API distinguishes:

- requesting friendship with a full Tox address and message;
- accepting a request by public key;
- deleting a friend by local friend number;
- enumerating local friend numbers and obtaining public keys;
- observing incoming friend requests through a callback.

rev0005 exposes those distinctions as:

```text
transport-peer-request TOX_ADDRESS_HEX MESSAGE
transport-peer-accept PUBLIC_KEY_HEX
transport-peer-remove FRIEND_NUMBER
peers
```

`transport-peer-add` remains only a compatibility alias for accept. Friendship is transport authorization, never IoTox ownership or actuator authority.

## File-transfer constants and identities

The public contract defines:

```text
TOX_MAX_FILENAME_LENGTH = 255 bytes
TOX_FILE_ID_LENGTH      = 32 bytes
maximum transfers       = 256 per friend per direction
```

The file number returned by toxcore is an opaque transfer handle. Upstream comments explicitly warn applications not to rely on patterns in file numbers. The current implementation encodes incoming direction in high bits, but that implementation detail is used only to make the exact mock realistic; IoTox product logic does not decode, mask, increment, or derive meaning from the handle.

A transfer's stable file ID is distinct from its file number. The file ID supports locating a transfer after local handle churn, but durable restart/resume policy is not yet implemented.

## Sending contract

A finite outgoing transfer begins with `tox_file_send`, including:

- friend number;
- kind;
- known byte size;
- optional stable file ID;
- filename bytes.

The remote peer begins paused. c-toxcore asks for data with the chunk-request callback. The sender must return the exact requested region through `tox_file_send_chunk`. For a known-size transfer, a terminal zero-length request need not be answered.

rev0005 consequently does not push a file in a blocking loop. `FileTransferManager`:

1. opens an absolute path with `O_NOFOLLOW|O_CLOEXEC`;
2. requires a finite regular file within configured size limits;
3. freezes device, inode, size, and modification time;
4. gives toxcore the offer;
5. services exact positional chunk requests from the owner-thread event stream;
6. verifies source metadata before and after each read;
7. fails and cancels if the source changes.

The manager uses duplicated descriptors rather than reopening by pathname. A zero-byte source is valid and is completed without waiting forever for a chunk request that may never arrive.

This is mock-tested behavior, not real-network evidence.

## Receiving contract

An incoming offer callback provides friend number, opaque file number, kind, size, and filename. It begins paused. The receiver accepts it by sending `TOX_FILE_CONTROL_RESUME`. The seek API is a receiving-side operation and must be used before resuming.

Chunk receipt is positional. A callback with length zero is terminal and requires application resources to be released.

rev0005 deliberately separates the offer from destination selection:

```text
file-receive FRIEND_NUMBER FILE_NUMBER PATH
```

Before sending resume, the manager:

1. verifies the offer remains pending and within limits;
2. resolves an absolute destination;
3. requires the immediate parent to be a real directory owned by the effective user;
4. rejects an existing destination;
5. creates a private `0600` temporary regular file in the same directory;
6. records an accepted transfer before transport resume.

Received chunks must be ordered, bounded, and within the offered size. On terminal completion, the manager verifies the exact final position and size, fsyncs the file, publishes without clobber using same-directory `link` plus `unlink`, and fsyncs the directory. Failure or cancellation removes the temporary file.

Symlink and ancestor-policy hardening remains incomplete: rev0005 checks the immediate parent and final target but does not yet traverse every ancestor with `openat2`/`openat` policy.

## Control and seek contract

File control operations include resume, pause, and cancel. Controls are scoped by friend number plus opaque file number. The c-toxcore callback represents a control received from the remote peer; a local call does not imply the callback will be echoed.

The rev0005 mock still models only the subset required for deterministic manager tests. It is not a network simulator and does not model congestion, arbitrary reordering, malicious peers, transport loss, or every remote control timing sequence.

## Ratox comparison

Ratox's elegance comes from projecting peer and transfer activity as ordinary Unix objects. Its implementation is intentionally compact and couples one peer record to a small amount of live transfer state. IoTox keeps the local legibility but replaces the transfer core:

- multiple opaque transfer handles;
- bounded pending offers, sends, and receives;
- explicit destination acceptance;
- source mutation detection;
- no-clobber final publication;
- exact event and control semantics;
- transactional runtime projections;
- one structured core beneath the filesystem view.

The filesystem is an operator surface. It is not the transfer database or protocol framing layer.

## Evidence classification

| Statement | rev0005 evidence |
|---|---|
| Function names, constants, and callback semantics match 0.2.23 headers | primary-source reviewed |
| `toxcore_static` and build-disable options exist | primary-source reviewed |
| Runtime-loaded ABI table resolves and executes the consumed subset | exact mock tested |
| One owner thread serializes calls and callbacks | compiled/tested |
| Friendship and finite file paths work through one public executable | process tested against mock |
| Source-linked c-toxcore compiles | not tested here |
| Two real Tox peers transfer a file | not tested here |
| NAT traversal, TCP relay, congestion, or public bootstrap works | not tested here |

## Next real-toxcore experiment

The first external workstation pass should:

1. fetch and verify pinned c-toxcore and libsodium sources;
2. configure `tools/build-standalone.sh` with warnings enabled;
3. resolve all compile/link differences against official headers without weakening the narrow provider;
4. run two isolated IoTox processes with separate state/runtime roots;
5. bootstrap through an operator-controlled local fixture where possible;
6. request and accept friendship;
7. exchange HELLO packets;
8. send empty, tiny, boundary-sized, and multi-chunk files in both directions;
9. pause, resume, cancel, disconnect, restart, and retry;
10. retain exact logs, source revisions, dependency versions, and packet/transfer observations.
