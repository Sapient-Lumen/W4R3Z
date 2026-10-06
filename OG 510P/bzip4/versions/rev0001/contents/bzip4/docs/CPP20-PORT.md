# C++20 port notes

## Port boundary

Only the top-level active tree is the bzip4 implementation:

- `src/*.cpp`
- `src/detail/*.hpp`
- `include/bzip4/*.hpp`
- `tools/*.cpp`
- `tests/*.cpp`

The `upstream/` directory is an immutable research reference and is excluded from CMake. There are no active C translation units.

## Source mapping

| Upstream bzip3 1.5.3 | Active bzip4 rev0001 |
|---|---|
| `src/libbz3.c` | `src/libbz3.cpp` |
| `src/main.c` | `src/main.cpp` |
| `include/libbz3.h` | `include/bzip4/libbz3.hpp` |
| `include/common.h` | `src/detail/common.hpp` |
| `include/libsais.h` | `src/detail/libsais.hpp` |
| `include/yarg.h` | `src/detail/yarg.hpp` |

## Language and build rules

- `CMAKE_CXX_STANDARD` is 20 and required.
- Compiler extensions are disabled with `CMAKE_CXX_EXTENSIONS OFF`.
- GCC warnings are enabled; no permissive conversion mode is used.
- Threads are linked through `Threads::Threads`.
- The compatible C ABI declarations remain inside `extern "C"`, allowing existing callers to link against the C++ implementation when ABI-compatible.

## Mechanical C-to-C++ changes

- Added explicit allocation casts where legacy internal allocation remains.
- Replaced all runtime-sized stack arrays with `std::vector`.
- Repaired the argument parser’s `goto`/initialization ordering for C++ lifetime rules.
- Replaced process-lifetime argument leaks with an owning `std::unique_ptr` and `yarg_destroy` deleter.
- Replaced CLI block/state raw ownership with vectors and unique pointers.
- Added a null guard to `bz3_free`.

## Defined arithmetic hardening

Bundled libsais paths used signed marker subtraction that can cross `INT32_MIN`. C builds commonly rely on two’s-complement wrapping there, but signed overflow is undefined in both C and C++. The port performs the same modulo-2^32 bit operations with `std::bit_cast` and unsigned subtraction. Differential output stayed byte-identical, and UBSan no longer reports those paths.

## High-level frame corrections

Two edge cases were corrected:

1. When `in_size % block_size == 0`, upstream replaced the final block length with zero. The port now keeps a full final block unless the remainder is nonzero.
2. A compressed incompressible block may be larger than its original block but still no larger than `bz3_bound(block_size)`. The high-level decoder now applies the bound rather than rejecting anything over `block_size`.

These corrections affect only faulty edge behavior in the in-memory frame API. The normal CLI path already used the correct encoded bound. The upstream in-memory frame has an extra block-count field after the common magic and block size, so it must not be fed directly to the CLI parser; the two interfaces retain their respective upstream layouts.

## New C++ API

`bzip4::block_codec` is a move-only owner of `bz3_state`. It accepts `std::span<const std::uint8_t>`, returns vectors, enforces configured block limits, and throws `bzip4::codec_error` carrying the bzip3 error code. It intentionally remains a block API; future container and transform layers should be composed above it rather than hidden inside it.
