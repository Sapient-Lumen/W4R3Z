# Cloud container build report

**Date:** 2026-08-13  
**Revision:** rev0001  
**Codename:** Just Werx Foundation

## Toolchain discovered

```text
Host: Linux x86-64
GCC/G++ 14.2.0
Clang/Clang++ 17.0.0
CMake 3.31.6
Ninja 1.12.1
Git, CTest, zip, readelf, nm, file, ldd, and sha256sum present
```

The container contained a libsodium runtime library but no toxcore headers, no toxcore shared library, and no toxcore pkg-config entry. Shell DNS access to GitHub was unavailable during the research/build work. Official source and release material was inspected through the research interface, but the real c-toxcore source archive or binary was not incorporated into rev0001.

## What was built

Every IoTox-owned implementation and test translation unit is C++20. The release build produced:

```text
iotox                         command-line research node and transport probe
iotox_tests                   self-contained unit/integration runner
libtoxcore-iotox-mock.so      deterministic C++ ABI boundary double
iotox_frame_fuzzer            Clang libFuzzer decoder target
```

The product executable uses `dlopen` and a narrow typed table to load c-toxcore at runtime. If official toxcore development headers are installed, the adapter consumes their canonical declarations. Otherwise, it uses an isolated fallback reproducing only the global C types and function signatures consumed from c-toxcore 0.2.23. The mock forces that fallback and exports the same signatures.

## Successful verification

```text
GCC 14 debug configure/build, warnings-as-errors: pass
GCC 14 debug CTest: pass
Clang 17 debug configure/build, warnings-as-errors: pass
Clang 17 debug CTest: pass
Clang 17 AddressSanitizer + UndefinedBehaviorSanitizer CTest: pass
GCC 14 ThreadSanitizer CTest: pass
GCC 14 release configure/build: pass
GCC 14 release CTest: pass
Detailed C++ test runner: 9 tests, 0 failures
CLI info smoke: pass
Runtime shared-library probe against mock: pass
Mock-backed owner-thread node lifecycle: pass
Tox identity save/reload through mock: pass
Persisted state mode: 0600
Negative duration input rejection: pass
```

Clang 17's installed ThreadSanitizer runtime could not link in this container because that Swift-flavoured distribution expects libdispatch/Blocks symbols. GCC 14 ThreadSanitizer built and ran successfully, so rev0001 includes a verified `gcc-tsan` preset rather than representing the Clang failure as a product defect.

## Fuzzer run

The fixed IoTox frame decoder was built with libFuzzer, AddressSanitizer, and UndefinedBehaviorSanitizer and exercised with the retained seed corpus:

```text
executed units: 1,656,425
average executions/second: 236,632
edge coverage counters reported: 108
feature counters reported: 139
new crashing inputs: 0
slowest input: below one second
```

This is a short smoke campaign, not a security proof or a claim of exhaustive protocol coverage.

## Defects found during construction

The testing facility found and drove fixes for two boundary problems before packaging:

1. The first mock used independently declared namespaced opaque types. It happened to call correctly on ordinary GCC/Clang builds, but UBSan identified that the C++ function-pointer types were not identical. The ABI layer now uses official global c-toxcore types or an exact global fallback, and compile-time contract assertions protect the consumed table.
2. The initial atomic state writer used a PID-derived temporary filename. It now uses a randomized same-directory `mkstemp` file, enforces close-on-exec and mode `0600`, detects zero-progress writes, flushes the file, atomically renames it, and flushes the parent directory.

## Important limitation

The runtime adapter has been exercised against a C++ shared library implementing the exact consumed ABI declarations. It has **not** been run against the real c-toxcore binary in this container, and rev0001 has not joined the public Tox network. Public bootstrap/TCP-relay configuration is deliberately still absent.

The first gate for rev0002 should be a pinned real c-toxcore build plus two-node native Tox tests using controlled bootstrap/relay fixtures. Until that passes, the package should be described as a compiled C++ foundation and testbed, not as a production-connected IoT daemon.
