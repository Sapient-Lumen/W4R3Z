# Revision notes — rev1012

## Compact ordinary source-manifest cache

Rev1012 removes the heap-backed generation-9 manifest and separate cumulative
offset vector from the one completed source manifest retained by the shipping
reconciliation service. Each cached chunk is now one 40-byte record containing
its exclusive cumulative end offset and fixed 32-byte SHA-256 value.

At the 8,192-chunk frontier, the focused allocation probe measures the rev1011
manifest-plus-offset shape at 8,194 allocations / 925,704 requested bytes. The
rev1012 cache requires one 327,680-byte vector allocation. The retained
representation therefore removes 8,193 allocator requests and 598,024 requested
bytes without changing source authority or wire semantics.

## Exact wire materialization

Generation 9 is unchanged. A cache-cold first range materializes the ordinary
string-backed protocol manifest from the compact sequence and moves that
temporary into the response. Later ranges and later continuation requests keep
using the existing manifest-digest reference. Maximum materialization remains
8,193 allocations / 860,160 requested bytes and is explicitly transient rather
than process-retained.

Complete durable checkpoint restoration and fresh source projection both
validate the ordinary manifest, compute the same canonical digest, and retain
only the compact cache afterward. Exact digest, extent, chunking parameters, or
POSIX inode-observation drift still revokes the cache.

## Allocation-cold parameter validation

The maximum-shape proof found that valid content-defined parameter validation
allocated one long diagnostic label on every success. Diagnostic strings are
now built only when validation fails. Valid semantics and failure text remain
unchanged.
The service range path also stopped rebuilding a diagnostic label for every
compact offset/end lookup. Numeric lookup now borrows the retained owner label;
the maximum 8,192-chunk sweep performs zero allocations.

## Explicit limits

The source cache remains one O(chunk count), one-source process-local
acceleration. Rev1012 does not remove cold 4 TiB hashing, the 1 GiB restart
replay interval, cache-cold protocol materialization, page-cache pressure, or
complete-scan cost. It does not create a global chunk index or solve Android,
rename/move identity, complete directories, conflicts, placeholders, automatic
eviction, retention collection, quota/ENOSPC policy, or public Tor/I2P
qualification.

## Validation and release identity

Exact rev1012 source passed a fresh GCC 14.2 Debug graph (567/567 configured build edges) and no-work bundled-SQLite re-attestation; all 300/300 registered tests and an independent 53/53 product replay passed. Focused GCC proofs passed 20 compact-manifest, 30 checkpoint-codec, 45 content-defined-chunker, 43 true-process restart, 5,001 reconciliation-protocol, 25 memory-shape, 20 terminal-state, 737 payload-store, 397 SQLite-owner, 536 folder-owner, 114 sync-once, 2,047 TLS, and 211 reconciliation-service checks. A fresh Clang 17 ASan/UBSan product graph completed 278/278 edges and all 53/53 product tests passed serially with leak detection and halt-on-error. Source audits passed 29/29 compact-cache, 36/36 retained-checkpoint, and 625/625 structural-authority checks; the exact rev1011 parent passed 41/41 wrapper-aware package checks. Aggregate terminal-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. Superseded pre-hotfix builds, the interrupted early registry, and pre-correction lexical-audit failures are excluded.

Archive: `AnonSync-rev1012-2026.08.06.14.42-compactmanifest-cumulativeindex-wirematerialization-dumortierite.zip`

Codename: `dumortierite`
