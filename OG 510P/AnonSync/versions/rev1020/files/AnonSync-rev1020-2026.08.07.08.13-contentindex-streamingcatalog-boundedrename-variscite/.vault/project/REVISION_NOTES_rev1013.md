# Revision notes — rev1013

## One fixed digest across source-manifest lifetime

Rev1013 replaces the heap-backed SHA-256 string in the generation-9
`SyncReplicaReconciliationDeltaChunk` with one 32-byte, standard-layout,
trivially copyable `Sha256DigestValue`. Protocol, compact-cache, and durable
checkpoint chunk records are all exactly 40 bytes.

At the 8,192-chunk frontier, parser-shaped construction, compact construction,
compact copy, and compact-to-wire materialization each require one exact
327,680-byte vector allocation. Materialization no longer creates 8,192
65-byte digest allocations. Relative to rev1012's measured transient shape, the
cache-cold publication boundary removes 8,192 allocator calls and 532,480
requested bytes.

## Canonicality and compatibility

Canonical lowercase hexadecimal text is decoded before a value is published;
failed assignment preserves the previous value. The protocol remains generation
9 and emits the same 64-character digest fields. Exact rev1012 request and
response fixture hashes are retained in the protocol regression.

The source-manifest checkpoint remains v2 and reproduces the exact sealed
rev1010 active, complete, and maximum byte images. Its private duplicate
hex/binary codec was removed in favor of the same shared fixed value.

## Explicit limits

This is a bounded allocation and representation correction, not constant-memory
multi-terabyte synchronization. One maximum sequence is still 327,680 bytes;
a cold 4 TiB source still costs 131,072 32 MiB pulses and may replay one 1 GiB
checkpoint interval. Whole-process RSS, page-cache pressure, allocator
fragmentation, concurrent shares, complete scans, route latency, and ENOSPC
remain measurement gates.

The revision does not add a global chunk index, rename/move identity,
directories, conflict UI, placeholders, automatic selective-sync eviction,
retention collection, Android support, or live public Tor/I2P qualification.

## Validation and release identity

Exact rev1013 source passed a fresh GCC 14.2 Debug graph (567/567 configured build edges across bounded resumptions) and a no-work bundled-SQLite re-attestation; all 301/301 registered tests and an independent 53/53 product accounting passed. Focused GCC proofs passed 22 compact-manifest, 30 checkpoint-codec, 45 content-defined-chunker, 43 true-process restart, 5,004 reconciliation-protocol, 25 memory-shape, 10 source-frame-memory, 20 terminal-state, 737 payload-store, 397 SQLite-owner, 536 folder-owner, 114 sync-once, 2,047 TLS, and 211 reconciliation-service checks. A fresh Clang 17 ASan/UBSan product graph completed 278/278 edges and all 53/53 product tests passed with leak detection and halt-on-error; the additional payload-store sanitizer proof passed 737 checks. Source audits passed 30/30 fixed-binary-manifest, 29/29 compact-cache, 22/22 checkpoint-memory, 27/27 manifest-reference, and 635/635 structural-authority checks; the exact rev1012 parent passed 41/41 wrapper-aware package checks. Aggregate terminal-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The overwritten first authority, divergent controller branches, discarded caches, interrupted early registry, and pre-correction lexical-audit failure are excluded.

Archive: `AnonSync-rev1013-2026.08.06.16.45-fixedbinarymanifest-sharedcodec-singleallocation-scheelite.zip`

Codename: `scheelite`
