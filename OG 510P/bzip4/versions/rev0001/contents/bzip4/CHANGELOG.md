# Changelog

## rev0001 — Huntstag — 2026-06-18

### Established

- Imported and checksum-recorded the bzip3 1.5.3 source baseline.
- Ported the active codec and CLI to strict C++20 under GCC, without `-fpermissive` or C translation units.
- Preserved BZ3v1 CLI stream compatibility and `.bz3` naming.
- Added a move-only RAII block-codec API and CMake install/export support.
- Added corpus benchmark and redundancy-probe tools.
- Added release, parallel CLI, malformed-header, exact-block-frame, move-semantics, random-data, all-byte-value, and sanitizer tests.

### Corrected while porting

- Replaced variable-length arrays with `std::vector`.
- Replaced implicit `void*` conversions with typed C++ allocations or RAII storage.
- Made `bz3_free(nullptr)` safe.
- Reclaimed parsed CLI arguments through `std::unique_ptr` rather than leaking them for process lifetime.
- Expressed libsais marker decrement and suffix-group-marker subtraction as defined modulo-32-bit arithmetic using `std::bit_cast`, eliminating signed-overflow undefined behavior while preserving output.
- Rejected negative compressed/original block lengths before they can become huge unsigned I/O sizes.
- Fixed high-level `bz3_compress` data loss when input size is exactly divisible by block size.
- Allowed the high-level decoder to accept a valid compressed block up to `bz3_bound(block_size)`, rather than incorrectly limiting it to the uncompressed block size.

### Deliberately deferred

- New `.bz4` container semantics.
- Long-range deduplication.
- Similarity ordering and format-aware splitting.
- Executable-specific transforms or self-extracting launchers.
- Compression-ratio or speed claims beyond recorded baseline tests.
