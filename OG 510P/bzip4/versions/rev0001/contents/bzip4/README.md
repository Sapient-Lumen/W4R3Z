# bzip4 rev0001 — Huntstag

`bzip4` is an experimental **C++20-only active codebase** derived from bzip3 1.5.3. Revision 0001 establishes a trustworthy, measurable baseline before changing the compression pipeline.

The executable is named `bzip4`, but this revision deliberately writes and reads the established **BZ3v1** stream format and keeps the `.bz3` extension. That gives us a byte-compatible control while we hunt for improvements. A future `.bz4` container will only be introduced when an experiment needs metadata that BZ3v1 cannot represent, such as reversible long-range deduplication or structural stream splitting.

## What rev0001 contains

- A strict GCC C++20 port of the bzip3 1.5.3 codec and CLI. No active `.c` translation units are built.
- A C++ RAII block API in `include/bzip4/codec.hpp`.
- The `bzip4` command-line compressor, decoder, tester, and recovery tool.
- `bzip4_bench`, a verified block-codec size and throughput harness.
- `bzip4_probe`, a corpus probe for entropy, repeated fixed-size chunks, duplicate lines, and long duplicate gaps.
- Release and sanitizer tests, malformed-header tests, and bidirectional interoperability validation against a separately built upstream C reference.
- An immutable upstream source snapshot under `upstream/bzip3-1.5.3/` for provenance. It is excluded from the active build.

## Build

Requirements: GCC with C++20 support, CMake 3.20 or newer, Ninja or Make, and POSIX threads.

```bash
cmake -S . -B build -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_CXX_COMPILER=g++
cmake --build build -j
ctest --test-dir build --output-on-failure
```

Equivalent presets are included:

```bash
cmake --preset release-gcc
cmake --build --preset release-gcc
ctest --preset release-gcc
```

Sanitizer build:

```bash
cmake -S . -B build-sanitize -G Ninja \
  -DCMAKE_BUILD_TYPE=Debug \
  -DCMAKE_CXX_COMPILER=g++ \
  -DBZIP4_ENABLE_SANITIZERS=ON
cmake --build build-sanitize -j
ASAN_OPTIONS=detect_leaks=1:halt_on_error=1 \
UBSAN_OPTIONS=halt_on_error=1 \
ctest --test-dir build-sanitize --output-on-failure
```

## CLI

```bash
# Compress; output remains a BZ3v1-compatible stream.
./build/bzip4 -f -b 64 -j 4 corpus.tar corpus.tar.bz3

# Validate without writing output.
./build/bzip4 -t -j 4 corpus.tar.bz3

# Decompress.
./build/bzip4 -d -f -j 4 corpus.tar.bz3 restored.tar
```

`-b` is the block size in MiB. BZ3v1 accepts 65 KiB through 511 MiB. Larger blocks can improve ratio at a substantial memory cost.

## C++ API

```cpp
#include <bzip4/codec.hpp>
#include <cstdint>
#include <vector>

std::vector<std::uint8_t> input = /* ... */;
bzip4::block_codec codec(16 * 1024 * 1024);

auto compressed = codec.encode(input);
auto restored = codec.decode(compressed, input.size());
```

The block API owns codec state, rejects oversized inputs, supports moves, and reports failures with `bzip4::codec_error`. The lower-level compatible `bz3_*` API remains available through `include/bzip4/libbz3.hpp`.

## Start hunting on a corpus

```bash
./build/bzip4_probe path/to/corpus
./build/bzip4_bench path/to/corpus 16 3
```

`bzip4_probe` is deliberately diagnostic rather than predictive. A high duplicate-line fraction with a low duplicate-4-KiB-chunk fraction, for example, suggests that exact fixed chunking misses structure and that record-aware ordering, line dictionaries, or content-defined chunking deserves a trial. Fingerprints are dual 64-bit hashes, so duplicate counts are probabilistic diagnostics rather than cryptographic proof.

`bzip4_bench` reports verified compressed block bytes, bits per input byte, and average encode/decode throughput. It reads the input into memory so repeated iterations do not measure disk I/O.

## Compatibility contract for rev0001

- CLI archives use magic `BZ3v1` and are intended to interoperate with bzip3 1.5.3.
- The codec algorithm and normal CLI output are unchanged except for C++ safety fixes.
- The compatible `bz3_compress`/`bz3_decompress` in-memory API retains upstream's separate frame layout, which includes a block-count field and is **not** the CLI byte stream despite sharing the `BZ3v1` magic. Rev0001 fixes two edge bugs in that API.
- No transform, dedup layer, binary packer, or new container is enabled yet.

## The optimization thesis

The first major target is not a magical universal 2× improvement inside the entropy coder. It is **redundancy that the current block pipeline cannot see or cannot cluster well**. Upstream’s own Perl-release benchmark reports 546,456,978 bytes for bzip3 at 511 MiB blocks and 60,672,608 bytes after long-range deduplication followed by bzip3. That makes long-range structure, similarity ordering, and reversible format-aware transforms first-class research tracks.

The full experiment map is in [`docs/OPTIMIZATION-HUNT.md`](docs/OPTIMIZATION-HUNT.md). Binary packing is treated separately in [`docs/BINARY-PACKING.md`](docs/BINARY-PACKING.md), because a good codec and a safe executable launcher have different constraints.

## Repository map

```text
include/bzip4/          Public C++ and compatible codec headers
src/                    Active C++20 codec and CLI
src/detail/             C++20 internal amalgamated dependencies
tools/                  Corpus benchmark and redundancy probe
 tests/                  C++ API and CLI integration tests
 docs/                   Port, research, format, and benchmark notes
 artifacts/              Generated test report for this revision
 upstream/bzip3-1.5.3/   Unmodified provenance snapshot; not built
 licenses/               LGPLv3 and bundled libsais Apache-2.0 text
```

## Licensing and provenance

The derived codec remains under the upstream project’s LGPLv3 terms. The bundled libsais license text is retained. See [`NOTICE.md`](NOTICE.md) and [`docs/PROVENANCE.md`](docs/PROVENANCE.md). This project is experimental; retain originals and verify important archives before deleting source data.
