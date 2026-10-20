# Cloudtainer build report — IoTox rev0007

**Date:** 2026-08-13 America/New_York  
**Revision:** rev0007  
**Version:** 0.7.0  
**Codename:** Peers Speak First  
**Northstar:** one installed C++20 ratox successor executable  
**Strongest evidence:** compiled, unit-tested, exact-mock-ABI-tested, process-tested

## Result

rev0007 advances `iotox` from a general Tox client/file surface into the beginning of a real
machine peer. A friend entering a true online epoch now causes the agent to generate and send
one canonical IoTox HELLO, receive and freeze the peer's first valid HELLO, negotiate a
bounded capability session, and project the result through the same executable and private
ratox-style tree. The agent also owns a live incoming friend-request inbox with explicit
list, accept, and reject operations.

The installed product surface remains exactly one executable:

```text
bin/iotox
```

Optional libraries, mocks, tests, fuzzers, benchmarks, and the Mutorr research program remain
build/evidence facilities and are absent from the install graph.

## Product work completed

### Canonical connection-scoped IoTox session

The reliable custom-packet lane now has a fixed first exchange:

```text
Tox friend offline -> online
        |
        +-- fresh 128-bit OS-CSPRNG nonce
        +-- exact 64-byte IHL1 HELLO
        +-- strict IoTox frame encode
        +-- toxcore lossless send
        +-- first peer HELLO frozen for the epoch
        +-- symmetric fail-closed negotiation
        +-- complete private runtime projection
```

The HELLO carries protocol range, implementation version/revision, maximum frame payload,
supported/required feature masks, maximum finite-file size, and the epoch nonce. The decoder
rejects malformed magic/version/flags, invalid ranges, impossible limits, required bits not
also supported, all-zero nonces, and nonzero reserved bytes.

The first valid peer payload is immutable until a true offline transition. A byte-identical
retry is idempotent even with a fresh outer message ID; a changed payload is a conflict. A
continuous TCP/UDP path change does not create a new epoch. Required features fail closed.

A negotiated session is rendered with:

```text
authorization=none-transport-session-only
```

This is deliberate. The session establishes machine-protocol compatibility, not owner,
controller, actuator, firmware, or delegation authority.

### Live explicit friend-request inbox

The c-toxcore callback's 32-byte public key and bounded message are copied before callback
return, stored in a bounded same-key serialized live inbox, and transactionally projected at:

```text
requests/<PUBLIC_KEY>/
  public-key
  message
  message-bytes
  received-unix-ms
```

The one executable exposes:

```text
iotox requests
iotox request-accept PUBLIC_KEY
iotox request-reject PUBLIC_KEY
```

`request-accept` requires a matching live request. Direct acceptance of a known key remains a
separate low-level transport operation. Neither path creates IoTox application authority.
The inbox is explicitly transient and is not represented as savedata, an audit log, or a
pairing proof.

### One binary, two roles

The actual process fixture launches:

```text
iotox run ...
```

and uses the same `iotox` executable as the local client. The path crosses Unix
`SOCK_SEQPACKET`, the bounded local decoder, agent service, toxcore owner queue/thread, exact
loadable C ABI mock, callbacks, event pump, session/request state, runtime tree, journals, and
savedata store.

The fixture exercises identity restart continuity, outgoing friendship, an incoming request
decision, profile/presence, byte-preserving action text, typing, receipt, automatic HELLO,
compatible session inspection, decoded frame evidence, idempotent HELLO retry, both finite
file directions, clean shutdown, and restart.

### Source-linked guard and real-peer handoff

The source-linked provider now fails compilation unless it sees canonical c-toxcore headers
whose public API is compatible with 0.2.23. The runtime provider may still use the narrow
fallback declaration set for the exact mock and explicit operator integration.

`tools/run-real-peer-smoke.sh` is prepared for the first networked CLI. Given a verified
source-linked `iotox`, it launches two real agents, requests and accepts friendship, waits for
compatible sessions in both directions, sends a normal Tox message, stops both agents, and
verifies identity continuity after restart. It is retained handoff code, not passing evidence
in this cube.

## Primary-source findings applied

The rev0007 implementation was checked against the pinned official c-toxcore 0.2.23 public
headers and release/build records.

Applied constraints include:

- one `Tox*` must be serialized; IoTox retains one exclusive owner thread;
- friend numbers are local indices and may change after savedata reload; operator selection is
  public-key-first;
- a friend-add does not itself mean the peer is online; the session starts only on a real
  connection callback;
- incoming request pointers are callback-scoped inputs and are copied immediately;
- reliable custom packets have a published 1,373-byte maximum, leaving 1,332 bytes after the
  IoTox frame header;
- `tox_options_set_experimental_disable_dns` is declared in the public `tox_options.h` for
  0.2.23 and may support future explicit Tor leak prevention, but it remains an experimental
  upstream option and no routed-Tox claim is made;
- the official CMake project provides `toxcore_static` under its static-build configuration;
- c-toxcore 0.2.23 is a security-relevant update and public API compatibility does not remove
  the need for sandboxing, pin review, and prompt upgrade practice.

## Verification retained

The final isolated source tree passed:

```text
GCC 14 debug                          build pass; CTest 7/7
GCC 14 release                        build pass; CTest 7/7
Clang 17 debug                        build pass; CTest 7/7
Clang 17 ASan + UBSan                 build pass; CTest 7/7
GCC 14 ThreadSanitizer                build pass; CTest 7/7
owned unit/integration executable     60 tests; 0 failures
frame decoder libFuzzer               5,000 runs; no crash
HELLO/session decoder libFuzzer       5,000 runs; no crash
local-control decoder libFuzzer       5,000 runs; no crash
Mutorr preservation configuration     build pass; CTest 9/9
installed executable count            1 (`bin/iotox`)
prebuilt convenience smoke             pass
```

Warnings are errors in the normal compiler lanes. The sanitizer and fuzzer results are
bounded executions, not proof of memory or parser safety.

During pre-final work, an orphaned matrix process from an older working tree deleted shared
build directories and caused misleading interrupted builds. The process was terminated and
all final evidence above was regenerated in the isolated
`/mnt/data/iotox-rev0007-final/IoTox` tree. The retained final logs, not the interrupted
pre-final runs, are authoritative.

## Source-linked attempt

The dependency lock pins:

```text
c-toxcore 0.2.23
sha256 b0349f4829d3d1699a77e199850f870f48d376e2baaf2c69d27b28571c498cfe

libsodium 1.0.22
sha256 adbdd8f16149e81ac6078a03aca6fc03b592b89ef7b5ed83841c086191be3349
```

The repository's own fetch path was executed. The cloudtainer shell could not resolve the
upstream download host and therefore could not obtain the immutable archives. No hash was
weakened, no copied substitute source was used, and the source-linked lane is not called a
pass.

## What rev0007 proves

```text
owned C++ session/request code compiles under GCC and Clang
strict bounded codecs survive the retained tests/fuzz smoke
one process owns the Tox ABI and local operator surface
connection callbacks drive automatic HELLO state through the exact mock ABI
the first HELLO is frozen and deterministic negotiation is implemented
incoming requests require an explicit local decision
the install graph exposes one product executable
```

## What rev0007 does not prove

```text
official c-toxcore source compiles and links with IoTox
real Tox encryption, DHT, NAT traversal, or relay behavior
two genuine peer timing, ordering, disconnect, or congestion behavior
Tor- or I2P-routed Tox and leak prevention
stable IoTox device identity or signed authorization
mutual transcript confirmation beyond HELLO negotiation
durable commands, replay defense, idempotent physical execution, or OTA
a remembered RecallRoot can re-enter a live device
target-hardware resource, suspend, flash, or power behavior
production readiness
```

The next product gates remain official source-linked compilation, two genuine native peers,
then a bounded transcript-confirmation message before application authorization and durable
commands.
