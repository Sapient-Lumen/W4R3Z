# rev0002 contents

## Mutorr C++ core

- `include/iotox/mutorr/id.hpp` and `src/mutorr/id.cpp`;
- `include/iotox/mutorr/cube.hpp` and `src/mutorr/cube.cpp`;
- `include/iotox/mutorr/head.hpp` and `src/mutorr/head.cpp`;
- deterministic circle topology, rendezvous placement, fixed mutable-head encoding, and linked-head evaluation.

## Retained Tox foundation

- network-stack type model;
- versioned lossless custom-packet frame;
- atomic savedata store;
- runtime c-toxcore ABI loader;
- single-owner-thread `ToxTransport`;
- deterministic C++ toxcore ABI mock.

## Native programs

- `iotoxmutorr`: information, Cube demonstration, packet demonstration, toxcore probe, and node lifecycle;
- `iotoxmutorr_bench`: release-oriented Cube, placement, and mutable-head benchmark.

## C++ tests and fuzzing

- self-contained C++ registry/assertion harness;
- 22 registered unit/integration tests;
- CTest command checks for CLI, Cube shape, and benchmark execution;
- packet-frame and mutable-head Clang libFuzzer targets;
- GCC, Clang, ASan/UBSan, TSan, and release presets.

## Documentation

- current README and build guide;
- Cube algorithm and performance design;
- architecture and protocol draft;
- testing strategy and benchmark report;
- threat model, network routing plan, retained ratox assessment, roadmap, and decision records;
- revision packaging policy and historical rev0001 research report.

## Packaged artifacts

The release package includes Linux x86-64 GCC 14 release binaries, the test runner, the ABI mock shared library, captured test/benchmark output, file and dependency reports, and SHA-256 checksums. A real c-toxcore shared library is not included.
