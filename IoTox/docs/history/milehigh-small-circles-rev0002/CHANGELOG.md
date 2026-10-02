# Changelog

## rev0002 — Small Circles Cube — 2026-08-13

- Forked the deliverable name to **IoToxmutorr** while retaining the isolated IoTox toxcore boundary.
- Added a deterministic namespace-scoped `Cube` built from sorted 256-bit member identities.
- Added a symmetric default topology with two clockwise and two counter-clockwise neighbors.
- Demonstrated 30 members with 60 overlay edges instead of 435 full-mesh pairs and an eight-hop diameter.
- Added rendezvous-hash custodian selection with deterministic tie-breaking and minimal disruption when members join.
- Added an allocation-free `custodian_indices_into` hot path using a fixed 32-candidate stack buffer.
- Added fixed-size 256-bit identifiers, canonical hex parsing, and deterministic synthetic IDs for C++ simulations only.
- Added a 221-byte linked mutable-head wire record and a 157-byte canonical signing body.
- Added head progression decisions for initial, advance, duplicate, stale, conflict, missing-history, different-stream, and invalid cases.
- Reserved `MUTORR_HEAD`, `MUTORR_INVENTORY`, `MUTORR_WANT`, and `MUTORR_OBJECT_OFFER` message types in the lossless packet lane.
- Added a native `cube-demo`, a native microbenchmark, a second fuzz target, and 13 new registered C++ tests.
- Verified GCC debug, Clang debug, Clang ASan/UBSan, GCC TSan, and GCC release builds and tests.

## rev0001 — Just Werx Foundation — 2026-08-13

- Established a C++20-only IoTox project with CMake and Ninja presets.
- Added GCC 14, Clang 17, Clang ASan/UBSan, and GCC ThreadSanitizer build-and-test paths.
- Added a runtime c-toxcore 0.2.23 ABI loader with explicit symbol validation and exact official/fallback C type declarations.
- Added one owner thread for every operation on a Tox instance.
- Added callback-to-event translation for self connection, friend connection, friend requests, and lossless custom packets.
- Added explicit friend acceptance and lossless packet sending.
- Added randomized temporary files and atomic mode-0600 Tox savedata persistence with file and directory flushing.
- Added an initial versioned IoTox lossless-packet envelope.
- Added a deterministic C++ c-toxcore ABI mock, compile-time ABI contracts, and integration tests.
- Separated Tox-over-I2P/Tor route planning from future direct I2P/Tor transports.
- Preserved the ratox-inspired filesystem façade as a planned compatibility surface rather than the core API.
