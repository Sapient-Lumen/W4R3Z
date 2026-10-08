# Compact source-manifest cache and cumulative-index audit — rev1012

## Product reason

AnonSync's first supported workflow is Linux/headless synchronization of media
trees measured in terabytes. Rev1011 removed per-chunk heap allocation from the
restart checkpoint, but the ordinary completed source cache still retained the
same bounded chunk sequence twice:

- a generation-9 protocol manifest whose 8,192 SHA-256 strings each owned a
  separate allocation; and
- an independent 8,193-entry cumulative-offset vector.

The protocol manifest is necessary only when a cache-cold peer must receive it.
Keeping that wire-oriented representation resident between requests made the
one-source cache needlessly expensive.

The focused maximum-shape allocation probe binds the retained representation:

| one 8,192-chunk source-cache shape | allocations | requested bytes |
|---|---:|---:|
| rev1011 string manifest plus offset vector | 8,194 | 925,704 |
| rev1012 compact cumulative records | 1 | 327,680 |

The rev1011 shape consists of one 327,680-byte manifest vector, 8,192 digest
allocations totaling 532,480 bytes, and one 65,544-byte offset vector. Rev1012
removes 8,193 allocator requests and 598,024 requested bytes from the retained
cache. These are allocator-boundary measurements and exact representation
accounting, not whole-process RSS. Allocator metadata, fragmentation, page
cache, open descriptors, protocol responses, SQLite, and unrelated service
state are outside those numbers.

## One fixed-width cumulative sequence

`SyncReplicaReconciliationCompactManifestChunk` contains exactly:

- one 64-bit exclusive cumulative end offset; and
- one fixed 32-byte SHA-256 value.

A compile-time 40-byte size fence and the runtime maximum-shape probe bind the
layout. One vector therefore answers both questions previously owned by two
containers:

1. which chunk contains an arbitrary byte offset; and
2. what exact size and digest identify that chunk.

The lookup uses the first cumulative end strictly greater than the requested
offset. Exact boundary offsets select the following chunk. The retained
sequence validates canonical content-defined parameters, positive bounded chunk
extents, exact total coverage, and canonical lowercase SHA-256 before becoming
cache acceleration.

## Wire compatibility and publication boundary

This revision does not introduce a new reconciliation generation or storage
format. Generation 9 still carries the same
`SyncReplicaReconciliationDeltaManifest` with 64-character lowercase digest
strings and per-chunk extents. The canonical manifest digest is unchanged.

The service now materializes that released protocol object only on the first
range of a cache-cold response. The temporary is moved into the response; it is
not copied from persistent cache state. Later ranges and continuation responses
carry only the existing constant-size manifest digest.

The focused proof shows maximum wire materialization still requires one
327,680-byte protocol vector plus 8,192 digest allocations, for 8,193
allocations and 860,160 requested bytes. That transient cost remains because the
wire object still owns strings. It no longer remains resident between peer
turns. Runtime reconciliation tests preserve the exact generation-9 framing,
manifest digest, range ownership, cache reference, restart, and source-local
scheduler behavior.

## Adjacent validator refactor

The first compact-cache allocation proof observed an unrelated 65-byte request.
Successful content-defined parameter validation eagerly copied its long label
into `std::string` even when every parameter was valid. Diagnostic construction
now occurs only on an error path. The semantic checks and diagnostics are
unchanged, but the success path is allocation-free. This is required for the
one-allocation cache-construction boundary and benefits every valid chunker
parameter check.
A second hot-path review found that the service had begun concatenating a fresh
diagnostic label at every compact chunk lookup. Valid numeric lookups now borrow
the existing owner label. The maximum 8,192-chunk offset/end/size sweep is
executable and requires zero allocations.

## Authority and failure boundary

The compact sequence is process-local acceleration only. It does not grant
causal, payload-byte, transfer, filesystem, or persistence authority. Every
source use still:

- binds an exact retained file operation;
- targeted-opens the digest-named private payload;
- re-proves its exact extent and POSIX inode observation;
- obeys the existing global-store and payload-inode lease ordering; and
- computes or verifies the canonical complete manifest digest.

Malformed or stale durable checkpoints remain optional acceleration and fall
back to ordinary projection. The compact cache is revoked on exact digest,
extent, parameters, or inode-observation drift.

## Honest scale boundary

Rev1012 reduces one completed source cache from roughly 904 KiB of allocator
requests to 320 KiB, but it remains O(chunk count). It does **not** solve:

- 131,072 bounded 32 MiB hash pulses for a cold 4 TiB source;
- up to one 1 GiB restart replay interval;
- the temporary 860,160-byte cache-cold wire manifest;
- complete-checkpoint restore's transient protocol strings;
- whole-process RSS, allocator fragmentation, page-cache pressure, checkpoint
  write amplification, final complete scans, route latency, or controlled
  ENOSPC behavior at multi-terabyte scale;
- a global, multi-file, multi-share, or durable chunk database;
- identity-preserving rename/move, complete directory and empty-directory
  semantics, portable metadata, conflict UX, selective placeholders and
  automatic eviction, best-effort retention collection, Android lifecycle and
  scoped-storage adapters, or live public Tor/I2P qualification.

The next scale gate remains a sparse synthetic multi-terabyte run measuring the
whole shipping process. If the remaining 327,680-byte sequence or the transient
wire object is material at measured share counts, the next design should page or
persist the exact bounded sequence rather than adding an unmeasured global
index. Otherwise product priority should return to rename/move identity,
directory semantics, conflict handling, and selective-sync operator surfaces.

## Validation and release identity

Exact rev1012 source passed a fresh GCC 14.2 Debug graph (567/567 configured build edges) and no-work bundled-SQLite re-attestation; all 300/300 registered tests and an independent 53/53 product replay passed. Focused GCC proofs passed 20 compact-manifest, 30 checkpoint-codec, 45 content-defined-chunker, 43 true-process restart, 5,001 reconciliation-protocol, 25 memory-shape, 20 terminal-state, 737 payload-store, 397 SQLite-owner, 536 folder-owner, 114 sync-once, 2,047 TLS, and 211 reconciliation-service checks. A fresh Clang 17 ASan/UBSan product graph completed 278/278 edges and all 53/53 product tests passed serially with leak detection and halt-on-error. Source audits passed 29/29 compact-cache, 36/36 retained-checkpoint, and 625/625 structural-authority checks; the exact rev1011 parent passed 41/41 wrapper-aware package checks. Aggregate terminal-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. Superseded pre-hotfix builds, the interrupted early registry, and pre-correction lexical-audit failures are excluded.

Archive: `AnonSync-rev1012-2026.08.06.14.42-compactmanifest-cumulativeindex-wirematerialization-dumortierite.zip`

Codename: `dumortierite`
