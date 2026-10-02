# IoTox

**Revision:** rev0003
**Version:** 0.3.0
**Codename:** Small Circles, One Home
**Language:** C++20 for every IoTox-owned implementation, test, simulation, and benchmark
translation unit

IoTox is a self-owned, peer-to-peer IoT agent built around Tox. It keeps ratox's best
idea—the network should feel small, local, inspectable, scriptable, and likely to “just
werx”—while making owner re-entry, authorization, protocol framing, persistence,
routing, testing, and optional replication explicit.

The two defining sentences are now:

> From memory, you can reach your devices.
>
> Authorized devices may form small circles to carry selected state for one another.

The first is implemented as the frozen RecallRoot-v1 Argon2id research contract. The
second comes from the user-supplied Milehigh IoToxmutorr branch, now absorbed as the
optional `iotox::mutorr` subsystem rather than a product rename.

## What IoTox is becoming

```text
permanent generated owner phrase
              |
        RecallRoot-v1
              |
 independent authorization ledger
              |
      +-------+------------------+
      |                          |
commands / state           optional Mutorr namespaces
results / pairing          small circles / custodians
      |                          |
      +-------+------------------+
              |
          IoTox protocol
              |
              Tox
   native / future Tor / future I2P
```

Tox remains the primary connection fabric. IoTox decides authority above Tox friendship.
A future ratox-style filesystem/FIFO surface will remain a simple façade over a
structured local core.

Read `docs/what-iotox-is-becoming.md` for the full synthesis.

## What rev0003 contains

rev0003 preserves rev0001 and rev0002 and adds:

- the reviewed Milehigh Small Circles contribution and provenance record;
- C++ `iotox::mutorr::Id256` identifiers;
- deterministic namespace-scoped `Cube` topology;
- default four-neighbor symmetric circles;
- rendezvous-selected preferred custodians with a default replication factor of three;
- an allocation-free custodian-selection hot path;
- a fixed 221-byte linked mutable-head record with a 157-byte canonical signing body;
- head progression decisions for initial, advance, duplicate, stale, conflict,
  missing-history, different-stream, and invalid records;
- provisional `MUTORR_HEAD`, `MUTORR_INVENTORY`, `MUTORR_WANT`, and
  `MUTORR_OBJECT_OFFER` frame types;
- `iotox cube-demo` and native `iotox_bench`;
- a corrected owner-thread startup barrier, after Clang exposed that `start()` could return just before the running state became observable;
- a second Clang fuzz target and retained corpus;
- 25 combined registered C++ tests;
- ADR 0008: Mutorr is optional namespace replication inside IoTox;
- integrated architecture, vision, protocol, threat, roadmap, network, and open-question
  documents;
- preserved rev0002 and Milehigh source documents/reports under history directories.

One integration hardening change rejects the all-zero reserved Cube member identity.

## Existing foundation retained

- CMake project configured as `LANGUAGES CXX`;
- GCC and Clang strict-warning builds;
- Clang ASan/UBSan and GCC TSan lanes;
- one C++ owner thread for every toxcore instance;
- runtime c-toxcore 0.2 ABI adapter and exact C++ test double;
- typed callback-to-event translation;
- explicit friend acceptance and lossless packet exchange;
- atomic private Tox savedata persistence;
- strict fixed IoTox lossless-packet envelope;
- explicit Tox/native, Tox/Tor, and Tox/I2P route model;
- pinned EFF long word list;
- RecallRoot-v1 phrase parser and Argon2 runtime boundary;
- exact Argon2 ABI mock and real known-answer test;
- no vendor recovery or device-reassignment authority;
- authorization ledger independent of Tox friendship.

## RecallRoot-v1

```text
contract:          iotox-recall-root-v1
phrase:            8 independently generated words
word list:         pinned EFF long list, 7776 entries
canonical form:    lowercase ASCII, one space between words
algorithm:         Argon2id version 19
memory:            65536 KiB
iterations:        3
parallelism:       4 lanes / 4 threads
salt:              ASCII IoToxRecallRoot1
output:            32 bytes
nominal entropy:   approximately 103.4 bits under uniform generation
```

The fixed public salt and parameters are intentional: the same phrase derives the same
root without stored metadata. This allows offline guessing, so a generated phrase is a
product requirement, not a suggestion.

The exact application key hierarchy, deterministic/reproducible Tox endpoint behavior,
and live device re-entry handshake remain open.

## Mutorr Small Circles

A Cube is one authorized namespace's replication plan. It is not a Tox group and not a
global mesh.

For thirty members with degree four:

```text
full mesh:       30 * 29 / 2 = 435 peer pairs
small circle:    30 * 4  / 2 =  60 peer pairs
edge reduction:                  86.21 percent
diameter:                         8 hops
```

All members with the same snapshot sort the same 256-bit IDs, compute the same circle,
and select the same preferred custodians.

The current placement mixer is deterministic and fast but not adversarially secure.
The head record carries a signature slot but no selected signing implementation. No
cryptographic object digest, object encryption, membership epoch, gossip engine,
durable object store, anti-entropy, or live Tox replication is claimed.

The basic device plane remains independent of Mutorr.

## Network status

| Stack | rev0003 state | Meaning |
|---|---|---|
| Tox/native | adapter-verified | Lifecycle and lossless-packet adapter verified against the exact C++ ABI mock; real network proof remains next |
| Tox/Tor | reserved | Future explicitly configured TCP-only Tox route through Tor plumbing and leak tests |
| Tox/I2P | reserved | Future explicitly configured Tox relay/bootstrap route through I2P plumbing and leak tests |
| Tor-direct | out of scope | Separate later IoTox transport without Tox semantics |
| I2P-direct | out of scope | Separate later IoTox transport without Tox semantics |

Reserved routes fail explicitly and never silently become native.

IoTox intends to contribute useful Tox bootstrap/TCP-relay capacity, owner-operated
server tooling, measurements, documentation, and upstream fixes. Running infrastructure
grants no ownership authority.

## Build

```sh
cmake --preset gcc-debug
cmake --build --preset gcc-debug
ctest --preset gcc-debug
```

Complete checked matrix:

```sh
./tools/build-matrix.sh
```

Individual presets:

```text
gcc-debug
clang-debug
clang-asan-ubsan
gcc-tsan
gcc-release
```

## Commands

Show encoded project status:

```sh
./build/gcc-debug/iotox info
```

Show the frozen recall contract:

```sh
./build/gcc-debug/iotox recovery-contract
```

Run the public real-Argon2 known-answer test:

```sh
./build/gcc-debug/iotox recovery-self-test \
  --wordlist third_party/eff_large_wordlist_2016-07-18.txt
```

Model a thirty-member namespace circle:

```sh
./build/gcc-release/iotox cube-demo \
  --nodes 30 --neighbors 4 --replicas 3 --namespaces 4096
```

Run the native C++ microbenchmark:

```sh
./build/gcc-release/iotox_bench \
  --nodes 30 --namespaces 200000 --rounds 5
```

Exercise the toxcore owner-thread boundary with the exact mock:

```sh
./tools/run-mock-node.sh
```

Probe or run with a compatible real c-toxcore shared library:

```sh
./build/gcc-debug/iotox toxcore-probe --library /absolute/path/to/libtoxcore.so.2
./build/gcc-debug/iotox node \
  --library /absolute/path/to/libtoxcore.so.2 \
  --state ./device.toxsave \
  --network tox/native \
  --run-ms 1000
```

The CLI deliberately has no command that accepts a real recall phrase in argv.

## Test facility

The combined C++ test runner currently covers:

- exact c-toxcore and Argon2 ABI boundaries;
- owner-thread lifecycle and callbacks;
- save/reload and private atomic state;
- network-route separation and fail-closed behavior;
- frame round trip and malformed input;
- RecallRoot word list, phrase structure, and known-answer derivation;
- Mutorr IDs, topology, join locality, placement, head encoding, progression, and frame
  integration.

Clang fuzz targets:

```text
iotox_frame_fuzzer
iotox_mutorr_head_fuzzer
```

The benchmark is descriptive for the current machine only. It is not an end-to-end
network or embedded-power result.

## Current boundaries

This is still a research datacube, not a deployable appliance. Missing work includes:

- a pinned real c-toxcore build and controlled two-peer fixture;
- public bootstrap and TCP-relay configuration;
- real NAT, relay, reconnect, and file-transfer evidence;
- RecallRoot subkeys and live re-entry;
- stable device application identity and physical claim;
- authorization-ledger implementation;
- durable command/result queues and idempotency;
- application signatures;
- Mutorr membership epochs, cryptographic placement, digest, encryption, gossip,
  anti-entropy, durability, deletion, and multi-writer semantics;
- structured Unix API and ratox-style façade;
- Tox/Tor and Tox/I2P routes;
- target-hardware reliability and power measurements;
- independent security and licensing review.

## Repository map

```text
include/iotox/             public C++ interfaces
include/iotox/mutorr/      optional namespace planner and head records
include/iotox/security/    RecallRoot and Argon2 boundary
include/iotox/toxcore/     isolated c-toxcore ABI boundary
src/                       implementation and research CLI
src/mutorr/                Small Circles implementation
src/security/              RecallRoot implementation
src/toxcore/               runtime loader and owner thread
tests/                     C++ tests, mocks, fuzzers, corpora
docs/                      architecture, decisions, research, history
artifacts/                 selected binaries, checksums, reports, retained evidence
third_party/               pinned word list and attribution
tools/                     build, test, mock-node, packaging scripts
```

## Side-project posture

IoTox may not become a complete commercial product. Each revision is therefore intended
to remain useful on its own: buildable code, tests, measurements, decisions, uncertainty,
and provenance are packaged together. A partial result can still become a ratox
successor, a Tox test facility, server tooling, upstream fixes, or a reusable replication
experiment.
