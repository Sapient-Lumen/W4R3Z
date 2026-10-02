# Changelog

## rev0003 — Small Circles, One Home — 2026-08-13

- Reviewed the user-supplied Milehigh `IoToxmutorr` rev0002 branch as source, design, benchmark, fuzz, and test evidence.
- Preserved the original Milehigh documents and text reports under datacube history, including the source archive SHA-256.
- Kept **IoTox** as the product name and accepted ADR 0008: `iotox::mutorr` is an optional namespace replication layer, not a prerequisite for ordinary device command/control.
- Integrated C++20 256-bit identifiers, deterministic namespace `Cube` planning, four-neighbor small circles, rendezvous custodians, and fixed linked mutable heads.
- Demonstrated thirty members with sixty application edges instead of 435 full-mesh edges and a computed eight-hop diameter.
- Integrated the allocation-free custodian-selection hot path, native `iotox_bench`, `iotox cube-demo`, mutable-head fuzz target, corpus, and combined tests.
- Added provisional `MUTORR_HEAD`, `MUTORR_INVENTORY`, `MUTORR_WANT`, and `MUTORR_OBJECT_OFFER` lossless-frame message types.
- Hardened Cube construction to reject the reserved all-zero member identity.
- Fixed a toxcore owner-thread startup publication race found by the Clang matrix: `start()` now reports success only after `running()` and immediate public operations are valid; the integration test checks that invariant.
- Kept the current rendezvous mixer explicitly research-only and documented identity-grinding risk.
- Kept the current head wire record provisional and opened the previous-root versus previous-head-digest decision.
- Made namespace membership an authorization-ledger input; Tox friendship and connectivity do not create Cube membership.
- Distinguished custody, readability, writing, actuation, and administration as separate capabilities.
- Preserved the RecallRoot-v1 permanent memory-root decision, no-vendor-reassignment decision, Tox-primary direction, and fail-closed future routes.
- Added `docs/what-iotox-is-becoming.md` and a detailed Milehigh branch review.
- Reworked architecture, vision, roadmap, protocol, threat model, network plan, testing plan, and open questions around one combined owner-reentry/device-command/optional-replication direction.
- Recorded that every datacube should remain buildable and salvageable even if IoTox stays a side project or stops before the full product.

## rev0002 — Home From Memory — 2026-08-13

- Accepted a permanent printed and memorizable master credential as a defining IoTox feature: from memory, an owner can reproduce the same recall root and re-enter the owner side of the network.
- Froze `iotox-recall-root-v1`: eight uniformly generated EFF long-list words, canonical lowercase ASCII, Argon2id version 19, 65,536 KiB, three iterations, four lanes/threads, fixed salt `IoToxRecallRoot1`, and 32-byte output.
- Made the security trade explicit: the fixed public contract permits unlimited offline guessing, so generated phrase strength is structural rather than optional.
- Pinned the 7,776-entry EFF long word list, its SHA-256 digest, attribution, and CC BY 3.0 legal text.
- Added C++20 `RecallPhrase`, `RecallWordList`, `RecoveryRoot`, and runtime Argon2 ABI adapter types with explicit secret-buffer wiping where the research boundary controls storage.
- Added an exact C++ Argon2 ABI mock that rejects any drift in the frozen derivation context.
- Added a real `libargon2.so.1` known-answer test and machine-readable `recovery-contract` command.
- Deliberately did not add a CLI path that accepts a real recall phrase through process arguments.
- Accepted that IoTox will possess no vendor key capable of resetting or reassigning customer devices.
- Kept c-toxcore as the primary peer transport and recorded an intent to contribute bootstrap/relay capacity, reproducible server tooling, testing, documentation, and upstream fixes.
- Confirmed that Tox friendship is transport state, while ownership, roles, capabilities, epochs, delegation, and revocation live in an independent device authorization ledger.
- Preserved Tox/native, Tox/Tor, and Tox/I2P as one transport family with explicit routes; direct Tor/I2P transports remain separate future work.
- Changed Tox/native status from the overly broad `implemented` label to `adapter-verified` until real c-toxcore and network fixtures pass.
- Expanded vision, ownership/recovery, threat-model, network-stewardship, open-question, roadmap, and Argon2 research documentation.
- Preserved the rev0001 reports and convenience binaries under `artifacts/history/rev0001/`.

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
