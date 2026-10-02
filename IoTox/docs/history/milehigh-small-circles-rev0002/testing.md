# Testing and performance strategy

## C++ test environment

All project test logic is C++20. The repository uses a small self-contained test registry and assertion harness rather than an external test framework. CTest launches the compiled programs; it does not contain product test logic.

The integration fixture is a C++ shared library named `libtoxcore-iotoxmutorr-mock.so`. It exports the exact consumed c-toxcore ABI types and exercises runtime symbol loading, options/savedata, instance lifecycle, iteration, callbacks, friend acceptance, packet send/receive, state snapshots, and restart.

## rev0002 coverage

The 22 registered C++ tests cover:

- exact toxcore ABI function and callback types;
- 256-bit ID parsing and canonical hex;
- deterministic Cube construction independent of input order;
- 30-device degree, edge count, symmetry, connectivity, and diameter;
- complete-graph behavior for small Cubes;
- local neighbor perturbation when one member joins;
- deterministic and balanced three-custodian rendezvous placement;
- minimal placement disruption after a join;
- allocation-free custodian output matching the convenience API;
- mutable-head canonical signing bytes and wire round trip;
- head advance, duplicate, stale, conflict, and history-required decisions;
- rejection of malformed linked heads;
- embedding a mutable head inside the Tox lossless frame;
- inherited network, frame, state-store, and Tox owner-thread behavior.

CTest also checks `info`, the 30-device `cube-demo`, and native benchmark execution.

## Verified compiler matrix

```text
GCC 14 debug, strict warnings
Clang 17 debug, strict warnings
Clang 17 ASan + UBSan
GCC 14 ThreadSanitizer
GCC 14 release
```

All normal targets use warnings-as-errors. TSan is separate from ASan/UBSan.

## Fuzzing

With `IOTOX_BUILD_FUZZER=ON`, Clang builds:

- `iotoxmutorr_frame_fuzzer` for the outer lossless frame;
- `iotoxmutorr_mutorr_head_fuzzer` for the fixed mutable-head decoder.

Future fuzz targets should cover inventories, want lists, object offers, durable records, membership epochs, and transfer state machines.

## Native benchmark

`iotoxmutorr_bench` is a C++20 microbenchmark with no third-party framework. It measures:

- Cube construction for a fixed membership;
- allocation-free three-custodian selection;
- linked-head evaluation.

The package captures a GCC release run for 30 nodes, 200,000 namespaces per round, and five rounds. Results are descriptive for the build container only. They are not cross-device promises and should be repeated on each target class with CPU frequency policy, thermal state, and compiler flags recorded.

## Next tests

- membership epochs under partial and reordered views;
- gossip deduplication and bounded queue pressure;
- simulated packet loss, reconnect, sleep, and clock rollback;
- Merkle inventory convergence and sparse object fetch;
- signature adapter test vectors and malicious-record rejection;
- two real pinned toxcore nodes exchanging heads and files;
- target hardware memory, CPU, traffic, wakeups, and power;
- long-running churn, full disk, interrupted writes, and restart recovery.
