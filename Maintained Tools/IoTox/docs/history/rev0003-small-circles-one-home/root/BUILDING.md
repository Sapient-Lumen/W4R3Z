# Building IoTox rev0003

## Required

- CMake 3.20 or newer;
- Ninja;
- a C++20 compiler;
- POSIX APIs: threads, `dlopen`, file descriptors, `fsync`, and atomic rename.

Every IoTox-owned implementation, test, simulation, fuzz harness, and benchmark source
is C++20. External C libraries remain isolated runtime dependencies.

## Runtime dependencies

### Argon2

RecallRoot-v1 derivation and its real known-answer CTest require an Argon2
reference-compatible shared library. Discovery order is:

```text
--argon2-library PATH
IOTOX_ARGON2_LIBRARY
libargon2.so.1
libargon2.so
libargon2.dylib
```

The build does not require `argon2.h`. Tests build `libargon2-iotox-mock.so` from C++ to
verify the exact consumed ABI and fixed contract fields.

### c-toxcore

A real Tox node requires c-toxcore 0.2.23 or a later patch release within the targeted
0.2 ABI line, exposed as `libtoxcore.so.2`, `libtoxcore.so`, or an explicit path supplied
through `--library` or `IOTOX_TOXCORE_LIBRARY`.

The default build does not require toxcore headers or libraries. The integration suite
builds `libtoxcore-iotox-mock.so` from C++ and loads it exactly as the program loads a
real runtime.

A production-quality revision still needs a pinned real c-toxcore build compiled against
official headers and tested in a controlled two-peer fixture.

## Recommended matrix

```sh
./tools/build-matrix.sh
```

The script configures, builds, and tests:

```text
gcc-debug
clang-debug
clang-asan-ubsan
gcc-tsan
```

Release lane:

```sh
cmake --preset gcc-release
cmake --build --preset gcc-release
ctest --preset gcc-release
```

## Research commands

Inspect project and network status:

```sh
./build/gcc-release/iotox info
```

Inspect and verify the RecallRoot contract:

```sh
./build/gcc-release/iotox recovery-contract
./build/gcc-release/iotox recovery-self-test \
  --wordlist third_party/eff_large_wordlist_2016-07-18.txt
```

Run the Small Circles demonstration and benchmark:

```sh
./build/gcc-release/iotox cube-demo \
  --nodes 30 --neighbors 4 --replicas 3 --namespaces 4096

./build/gcc-release/iotox_bench \
  --nodes 30 --namespaces 200000 --rounds 5
```

Exercise the Tox lifecycle with the exact mock:

```sh
./tools/run-mock-node.sh
```

## Fuzzers

Configure the two Clang libFuzzer targets:

```sh
cmake -S . -B build/clang-fuzz -G Ninja \
  -DCMAKE_CXX_COMPILER=/usr/local/swift/usr/bin/clang++ \
  -DCMAKE_BUILD_TYPE=Debug \
  -DIOTOX_BUILD_FUZZER=ON
cmake --build build/clang-fuzz --parallel
```

Frame decoder:

```sh
./build/clang-fuzz/iotox_frame_fuzzer \
  tests/fuzz_corpus/frame -max_total_time=30
```

Mutable-head decoder:

```sh
./build/clang-fuzz/iotox_mutorr_head_fuzzer \
  tests/fuzz_corpus/mutorr_head -max_total_time=30
```

## ThreadSanitizer

```sh
cmake --preset gcc-tsan
cmake --build --preset gcc-tsan
TSAN_OPTIONS=halt_on_error=1:second_deadlock_stack=1 ctest --preset gcc-tsan
```

The retained container lane uses GCC for ThreadSanitizer. The installed Swift-flavoured
Clang runtime expects unavailable libdispatch/Blocks symbols.

## Benchmark note

`IOTOX_BUILD_BENCHMARK` defaults to `ON`. Disable it for smaller builds:

```sh
cmake -S . -B build/minimal -G Ninja \
  -DCMAKE_CXX_COMPILER=g++ \
  -DIOTOX_BUILD_BENCHMARK=OFF
```

The benchmark measures only in-process Mutorr planning and head evaluation. It is not a
network, disk, cryptographic, or power benchmark.

## Secret-entry warning

`recovery-self-test` uses one public known-answer phrase. There is intentionally no CLI
for deriving an owner's real recall root. Do not add an argv-based secret command for
convenience.

A production input path must use a protected TTY/file descriptor or platform credential
UI, minimize copies, avoid logs/clipboard/process listings, wipe controlled buffers, and
document limits imposed by external libraries and operating systems.
