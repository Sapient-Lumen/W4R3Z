# IoTox testing and performance strategy

## Principle

IoTox treats testability as architecture. Network libraries, recovery contracts,
durable state, and replication planners sit behind boundaries that can be exercised
without pretending a public network is deterministic.

All IoTox-owned test, simulation, benchmark, and fuzz harness code is C++20. CTest and
small shell scripts orchestrate compiled programs; they do not contain product logic.

## Current test doubles

### c-toxcore ABI mock

`libtoxcore-iotox-mock.so` is a C++ shared library that exports the exact consumed C ABI.
It covers:

- runtime symbol loading and version checks;
- options and savedata;
- Tox object lifecycle;
- iteration and callbacks;
- self/friend connection events;
- explicit friend acceptance;
- lossless packet send/echo/receive;
- state snapshot and restart.

This validates the C++ boundary and owner-thread lifecycle. It does not validate real
Tox cryptography, NAT traversal, relays, DHT behavior, public bootstrap, or real file
transfer.

### Argon2 ABI mock

`libargon2-iotox-mock.so` verifies the exact frozen RecallRoot-v1 parameters crossing
the C ABI boundary. A separate test uses the container's real `libargon2.so.1` and a
known-answer root.

## rev0003 registered C++ tests

The integrated test runner contains 25 tests. The retained rev0003 matrix passes all
six CTest commands under GCC debug, Clang debug, Clang ASan/UBSan, GCC TSan, and GCC
release. Coverage includes:

### Dependency boundaries

- exact c-toxcore function and callback types;
- shared-library loading and version checks;
- one-owner-thread lifecycle;
- startup publication invariant: a successful `start()` already implies `running()` and
  permits immediate public operations;
- callback-to-event translation;
- friend acceptance and lossless packet exchange;
- state save/reload.

### Network model

- Tox routes remain separate from direct overlays;
- unknown network names fail closed;
- reserved Tor/I2P routes fail instead of silently becoming native.

### IoTox frame

- encode/decode round trip;
- malformed and truncated input rejection;
- packet identifier and message-type validation;
- payload-length and custom-packet capacity enforcement;
- Mutorr head embedding within one lossless packet.

### Persistence

- randomized private temporary file;
- atomic replacement;
- mode `0600`;
- data round trip.

### RecallRoot-v1

- exact 7,776-entry pinned word list and digest;
- canonical eight-word phrase parsing;
- weak structure and foreign word rejection;
- exact Argon2 context through the mock;
- real known-answer output.

### Mutorr identifiers and Cube

- canonical 256-bit hex round trip and malformed-input rejection;
- deterministic topology independent of discovery order;
- thirty members, degree four, sixty edges, connectivity, and diameter eight;
- complete-graph behavior for small Cubes;
- single-member behavior;
- local neighborhood perturbation after one join;
- deterministic, balanced, and minimally disrupted rendezvous placement;
- allocation-free custodian output matching the convenience API;
- invalid configuration, duplicate identity, and reserved zero-identity rejection.

### Mutorr heads

- fixed canonical signing and wire sizes;
- encode/decode round trip;
- initial, advance, duplicate, stale, conflict, and history-required decisions;
- malformed linkage rejection;
- fit within the IoTox control packet.

## CTest command checks

The configured suite also runs:

- `iotox info`;
- `iotox recovery-contract`;
- the real Argon2 known-answer command;
- a thirty-device `iotox cube-demo`;
- an `iotox_bench` smoke run.

## Compiler matrix

Expected and retained lanes:

```text
GCC 14 debug, strict warnings as errors
Clang 17 debug, strict warnings as errors
Clang 17 AddressSanitizer + UndefinedBehaviorSanitizer
GCC 14 ThreadSanitizer
GCC 14 release
```

ASan/UBSan and TSan remain separate. All normal project targets use warnings as errors.

## Fuzzing

With `IOTOX_BUILD_FUZZER=ON`, Clang builds:

- `iotox_frame_fuzzer` for the outer fixed IoTox frame;
- `iotox_mutorr_head_fuzzer` for the fixed mutable-head decoder.

The fuzz targets compile the relevant decoder source directly so instrumentation covers
the parser rather than only the harness.

Future fuzz targets should cover:

- canonical authorization records;
- re-entry transcripts;
- command/result payloads;
- membership epochs;
- inventory, want, and object-offer payloads;
- Merkle manifests;
- durable journal recovery;
- Tox file-transfer state machines;
- local IPC framing.

## Native benchmark

`iotox_bench` measures:

- Cube construction for a fixed member set;
- allocation-free three-custodian selection;
- linked-head progression evaluation.

These are microbenchmarks. They exclude toxcore, sockets, signatures, hashing,
encryption, disk, gossip queues, Merkle traversal, file transfer, and power behavior.
Results are descriptive for the build container only.

## Required next tests: real Tox

- compile against official c-toxcore headers;
- controlled bootstrap and TCP relay;
- two genuine peers;
- bidirectional `HELLO` exchange;
- save/restart and stable identity;
- disconnect, reconnect, and relay-only operation;
- custom-packet duplicate/retry behavior;
- one real file transfer;
- resource and traffic capture;
- malformed packet pressure against real callbacks.

## Required next tests: re-entry and authorization

- independent key-derivation vectors;
- reconstruction from total controller-state loss;
- challenge freshness and replay rejection;
- ownership-epoch mismatch;
- delegated controller grant and revocation;
- ledger rollback and partial-write recovery;
- phrase-compromise transition races;
- no secret in logs, argv, environment, crash output, or reports.

## Required next tests: Mutorr simulation

- signed/test-signed membership epochs;
- stale and divergent membership views;
- degrees 2/4/6 under random and correlated offline behavior;
- bounded gossip deduplication and retry;
- queue pressure and malicious unique announcements;
- custodian failure and repair;
- missing history and fork evidence;
- object availability convergence;
- revoked member and key-rotation behavior;
- 30, 100, and 1,000-node deterministic simulations.

## Target-hardware testing

Before product claims, measure on actual target classes:

- resident and peak memory;
- thread and descriptor count;
- bootstrap and reconnect time;
- idle and active traffic;
- CPU wakeups;
- suspend/resume;
- flash write frequency;
- thermal behavior;
- battery or wall power;
- filesystem-full and power-cut recovery;
- long-duration reconnect churn.

A cloud-container build proves portability across two compilers on one Linux class. It
does not prove embedded suitability.

## Evidence policy

Every datacube should retain:

- compiler and kernel information;
- exact test output;
- sanitizer output;
- fuzzer smoke output and corpus;
- benchmark command and result;
- binary file types and runtime dependencies;
- checksums;
- explicit skips and unverified claims;
- provenance for imported branches or retained data.
