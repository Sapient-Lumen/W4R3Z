# IoToxmutorr

**Revision:** rev0002  
**Codename:** Small Circles Cube  
**Language:** C++20 for all project implementation, tests, simulations, and benchmarks

IoToxmutorr is a performance-minded experiment in mutable, content-addressed replication over Tox. It grows from the rev0001 IoTox foundation: c-toxcore remains isolated behind one C++ owner thread, while the new `iotox::mutorr` core can be tested deterministically without a live network.

The central idea is that a shared directory is not a thirty-member chatroom. Each mutable namespace gets its own **Cube**: an authorized member snapshot, a bounded-degree circle mesh for gossip, and a deterministic replica set for durable storage.

## What rev0002 adds

- `iotox::mutorr::Cube`, a deterministic namespace-scoped overlay planner;
- four-neighbor circle topology by default: two predecessors and two successors on a ring of 256-bit member identities;
- rendezvous-hash custodian selection with a default replication factor of three;
- an allocation-free custodian-selection hot path for repeated placement decisions;
- a fixed-size linked mutable-head record with namespace, writer, generation, root, previous root, metadata, and an opaque 64-byte signature;
- progression decisions for initial, advance, duplicate, stale, conflicting, and history-required heads;
- four Mutorr control message types in the existing Tox lossless-packet frame;
- a native C++ `cube-demo` and a native C++ microbenchmark;
- 22 registered C++ tests plus CLI and benchmark smoke checks.

## Thirty-device shape

With the default four-neighbor Cube:

```text
full mesh:       30 * 29 / 2 = 435 peer pairs
mutorr cube:     30 * 4  / 2 =  60 peer pairs
reduction:                         86.21 percent
worst path:                         8 hops
```

Every member given the same authorized member set computes the same sorted ring. No coordinator assigns groups. Adding one member changes only the nearby ring neighborhoods. A small membership of five or fewer automatically collapses to a complete local circle.

A namespace can select three custodians without a central tracker. Each member scores the pair `(namespace ID, member ID)` and the same highest-scoring members win everywhere. Adding a device either leaves an existing replica set unchanged or inserts the new device while retaining the prior winners; unrelated existing members do not reshuffle.

## Mutable-head model

The mutable pointer is small; the directory objects beneath it are intended to be immutable and content-addressed.

```text
namespace + writer
        |
        v
  generation 43
  root = H(new tree)
  previous = H(old tree)
  signature = ...
        |
        v
 immutable directory/object DAG
```

The current head wire record is 221 bytes and fits comfortably in the existing Tox lossless control frame. The 157-byte signing body is exposed separately so a future signing adapter can sign exactly one canonical byte sequence.

rev0002 does **not** claim cryptographic completion. It carries an application signing key and opaque signature but does not choose or implement the signature algorithm. It also expects production member, namespace, and object identifiers to come from cryptographically strong code outside the synthetic simulation helper.

## Performance choices

- member IDs are fixed 32-byte values stored contiguously;
- membership is sorted once when a Cube is built;
- neighbor spans are precomputed in one flat adjacency vector;
- custodian selection is `O(members * replicas)` and uses a fixed 32-entry stack array;
- the hot `custodian_indices_into` API performs no heap allocation and no full sort;
- mutable-head comparison is fixed-size and `O(1)`;
- no external C++ framework or runtime is required for tests or benchmarks.

The packaged GCC release benchmark records the actual container result. Benchmark numbers are machine-specific and are not protocol guarantees.

## Build and test

```sh
cmake --preset gcc-debug
cmake --build --preset gcc-debug
ctest --preset gcc-debug
```

Additional verified presets:

```sh
cmake --preset clang-debug
cmake --build --preset clang-debug
ctest --preset clang-debug

cmake --preset clang-asan-ubsan
cmake --build --preset clang-asan-ubsan
ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 \
UBSAN_OPTIONS=halt_on_error=1 \
ctest --preset clang-asan-ubsan

cmake --preset gcc-tsan
cmake --build --preset gcc-tsan
TSAN_OPTIONS=halt_on_error=1:second_deadlock_stack=1 \
ctest --preset gcc-tsan

cmake --preset gcc-release
cmake --build --preset gcc-release
ctest --preset gcc-release
```

CMake and the small shell wrappers are build orchestration. Project logic, test logic, deterministic fixtures, simulation, and benchmarking are C++20.

## Commands

Inspect the build:

```sh
./build/gcc-debug/iotoxmutorr info
```

Model the default thirty-device Cube:

```sh
./build/gcc-release/iotoxmutorr cube-demo \
  --nodes 30 --neighbors 4 --replicas 3 --namespaces 4096
```

Run the native benchmark:

```sh
./build/gcc-release/iotoxmutorr_bench \
  --nodes 30 --namespaces 200000 --rounds 5
```

Exercise the retained Tox runtime boundary against the deterministic C++ ABI mock:

```sh
./tools/run-mock-node.sh
```

Probe or run with a compatible real c-toxcore shared library:

```sh
./build/gcc-debug/iotoxmutorr toxcore-probe --library /absolute/path/to/libtoxcore.so.2
./build/gcc-debug/iotoxmutorr node \
  --library /absolute/path/to/libtoxcore.so.2 \
  --state ./device.toxsave \
  --network tox/native \
  --run-ms 1000
```

## Boundaries that remain

rev0002 plans the overlay and mutable pointer but does not yet wire them into a live replication engine. Still absent are membership synchronization, authorization policy, signature verification, cryptographic content hashing, immutable object storage, gossip deduplication, anti-entropy inventory exchange, Tox file-transfer plumbing, durable queues, public bootstrap configuration, and real two-host resource measurements.

The next coherent slice is to connect `MUTORR_HEAD`, inventory, want, and object-transfer state to the transport mock first, then to two pinned real toxcore nodes. See `docs/mutorr-cube.md`, `docs/architecture.md`, `docs/protocol-draft.md`, and `docs/testing.md`.
