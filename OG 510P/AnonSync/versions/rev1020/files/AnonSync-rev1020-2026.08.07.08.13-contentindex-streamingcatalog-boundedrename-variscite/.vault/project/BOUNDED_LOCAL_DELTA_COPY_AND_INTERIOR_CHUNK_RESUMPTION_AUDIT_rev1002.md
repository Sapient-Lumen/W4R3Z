# Rev1002 bounded local delta-copy and interior-chunk resumption audit

## Product question

Rev1001 bounded receiver-side hashing of one plausible cross-file source, but
copying an already matched adaptive chunk could still run to the end of that
chunk in one reconciliation apply. At the exact four-terabyte payload ceiling,
a canonical adaptive chunk may reach **2 GiB**. One valid local match could
therefore monopolize the owner thread through hundreds of reads, hashes, staged
prefix commits, and durability effects.

Rev1002 bounds that local-copy effect without weakening whole-payload identity,
durable-prefix authority, or final causal admission. The correction applies to
both same-path predecessor reuse and current-visible cross-file reuse.

## Retained design

### One shared 32 MiB source-read frontier

`SyncReplicaReconciliationService::apply_response_or_throw` begins with one
32 MiB local-reuse budget. Every byte actually read from an immutable local
candidate is charged against that shared budget, regardless of candidate path
or response range. The budget is not reset for another candidate, operation, or
wire range in the same apply invocation.

The frontier charges source reads rather than only newly accepted staging bytes.
That distinction matters when the payload-store owner observes a longer already
durable prefix: consumed local I/O cannot disappear from scheduling evidence.

Exhaustion suppresses further local candidate reads for that apply. The receiver
still consumes the remainder of the already authenticated, bounded response
frame. If the target remains incomplete, it returns `PayloadProgress` with the
exact durable prefix and admits no operation metadata.

### Interior adaptive-chunk continuation

The old copy path entered reuse only at an exact chunk boundary. Rev1002 locates
the chunk containing the current durable prefix, then derives the source offset
as the matched candidate chunk beginning plus the exact intra-chunk displacement.

A later apply may therefore reopen the candidate and continue from the middle of
one matched chunk, including after reconstruction of the reconciliation service.
The durable staged prefix is restart authority; cached manifests and indices are
acceleration only. Every bounded copy range still:

1. reopens the exact immutable candidate through targeted payload access;
2. re-proves the retained eleven-field POSIX observation;
3. reads and SHA-256-attests one exact source range;
4. stages it through the crash-safe contiguous-prefix owner; and
5. requires final whole-target SHA-256 before payload publication.

### Product-owned four-MiB range

A separate four-MiB range ceiling bounds the one owned local source string. It is
intentionally independent of the peer's negotiated wire range. Tiny frames must
not multiply one 32 MiB budget into millions of descriptor reopens, range hashes,
fsyncs, and rename effects.

The apply memory shape therefore adds at most one bounded four-MiB local range
beside the already bounded response frame and staging machinery. No
adaptive-chunk-sized buffer is allocated or retained.

### Preserve preframed wire bytes

A local copy can advance the durable prefix into a later range that the peer had
already framed before apply began. Stopping the wire loop at that point would
throw away authenticated data and could waste many MiB each turn.

Rev1002 instead classifies every later range against the current durable prefix:

- a fully covered range is accounted as already durable and is not restaged;
- a partially covered range drops only the exact committed prefix;
- the advancing suffix is SHA-256 hashed without copying the response frame and
  is staged at the exact durable offset; and
- a gap remains terminal.

The protocol remains generation 7 because this is receiver-local scheduling and
staging behavior. No new wire field or durable journal is introduced.

### Truthful accounting

Service results, TLS aggregation, `anonsync_sync`, and `anonsync_replica` report:

- local candidate read ranges and bytes;
- the largest one local read range;
- local-reuse budget exhaustions;
- interior-chunk resumptions;
- authenticated wire ranges and bytes already durable; and
- the partial-overlap subset whose suffix was retained.

These counters are operator evidence only. They do not become payload, causal,
or admission authority.

## Runtime evidence

The dedicated regression builds a deterministic 24 MiB predecessor, inserts
256 KiB near its beginning, and proves the canonical manifests contain a shared
adaptive chunk larger than the configured one-MiB test frontier. The source
preframes three 768 KiB ranges per response. A one-MiB local copy therefore
crosses a wire boundary and ends inside a later range.

Across bounded authenticated turns the test proves:

- no apply reads more than one MiB from local candidates;
- the largest local range is one MiB and therefore larger than a wire range;
- exhaustion publishes an exact durable `PayloadProgress` continuation;
- the service is destroyed and reconstructed after the first exhaustion;
- a later service resumes inside the same adaptive chunk;
- fully covered wire ranges are accounted rather than reread;
- a partial overlap is trimmed and its advancing suffix is staged;
- received wire bytes equal staged bytes plus already-durable wire bytes;
- staged bytes plus locally reused bytes equal the exact target size;
- network bytes remain below the target size; and
- exact payload bytes and causal evidence converge.

The focused reconciliation-service executable passes **185 checks** on the
reviewed source before release sealing.

## Adjacent audit and refactor findings

The first bounded implementation tied local copy granularity to
`max_single_payload_bytes`. Total bytes were bounded, but a hostile or merely
tiny wire range could still multiply local descriptor, hashing, durability, and
rename effects. The retained four-MiB range is product-owned.

The next implementation stopped the payload loop when the local budget was
exhausted. That preserved the local-I/O frontier but discarded later ranges
already present in the authenticated response. The retained implementation
continues the wire loop and stages only the advancing suffix.

Suffix hashing initially reached `anonsync_sha256_digest` only through the
payload-store target's private implementation dependency. The reconciliation
service now declares its own private SHA-256 link, so its direct executable
dependency cannot disappear when the payload-store boundary is refactored.

The complete registry then caught two stale inherited lexical oracles. The
content-defined-delta audit still required the former exact-boundary copy
spelling, and the multi-range audit still treated every durable-prefix overlap
as terminal. They now bind the shared shifted/interior-resumable copy boundary
and the stricter three-way wire classification: complete replay is skipped, an
advancing suffix is preserved, and a gap still fails closed. Runtime and
protocol tests remain the semantic authority; these edits only prevent source
shape checks from rejecting the intended implementation.

A divergent unsealed rev1002 prototype and its competing build were stopped and
removed from validation authority. Three source files containing its useful
reference design were preserved in an explicitly non-authoritative external tar
before deletion. Only the active source rooted by the rev1002 authority marker
may supply release results.

## Explicit nonclaims and next risk

Rev1002 is not a global per-turn local-I/O bound. In particular:

- same-path predecessor manifest construction can still hash a complete very
  large predecessor in one apply;
- completion of a staged target still performs complete whole-payload
  verification in one owner call;
- cross-file candidate projection has its own independent 32 MiB budget;
- wire decoding, SQLite work, filesystem durability, and kernel page-cache
  behavior are separate effects;
- unfinished candidate manifests are not restart-durable; and
- there is no durable/global chunk index or target-scale sparse multi-terabyte
  soak result yet.

The next delta-latency work should bound same-path predecessor-manifest scanning
and terminal whole-target verification, then measure sparse multi-terabyte RSS,
page cache, local I/O, disk amplification, restart, ENOSPC, and route behavior.
Product work still includes identity-preserving rename/move, complete directory
semantics, selective-sync placeholders and eviction, ordinary conflict
presentation, Android adapters, and live public Tor/I2P qualification.

## Release cutpoint

Validation: `Exact rev1002 source passed a fresh GCC 14.2 Debug graph (551/551 configured build edges) and a no-work bundled-SQLite re-attestation; all 285/285 registered tests were accounted for, including both final documentation-sensitive audits, and an independent 47/47 product replay passed. Focused GCC proofs passed 677 payload-store, 185 reconciliation-service, 536 folder-owner, 397 SQLite-owner, and 2,044 TLS-transport checks. Source audits passed 31/31 bounded local reuse, 32/32 bounded resumable cross-file projection, 31/31 content-defined delta, 27/27 multi-range window, 27/27 manifest reference, and 538/538 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product dependency graph completed 262/262 edges and reached a no-work re-attestation; all 47/47 product tests were accounted for with leak detection and halt-on-error. Focused sanitizer proofs passed 677 payload-store, 185 reconciliation-service, and 536 folder-owner checks; the folder-owner proof completed in 30.21 seconds at 1,694,316 KiB peak RSS, the reconciliation-service proof in 21.07 seconds at 778,188 KiB, and the payload-store proof in 9.47 seconds at 519,228 KiB. Aggregate final-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev1001 parent SHA-256 matched f5f7313ecd228074cd040cf432305626aa2654e4d936c125ec4daa26098b2de4 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 17/17 changed wrapper paths, all 16/16 changed project paths, all 13/13 changed active paths, and the complete 613-file active projection byte-for-byte and mode-for-mode. The final active implementation projection contains 613 files / 28,332,387 bytes with SHA-256 adcc77e2efda814bfb8d69cfd03ee289ba7077085cd3fa6a6c44e45d90cd4374. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excluded remount-vanished scratch worktrees, the divergent unsealed local-copy prototype, an interrupted aggregate sanitizer shard, the pre-build missing-target invocation, superseded lexical-audit failures, and generated Python bytecode removed before projection sealing.`

Archive: `AnonSync-rev1002-2026.08.05.11.19-localcopyfrontier-interiorresume-wireoverlap-sinhalite.zip`

Codename: `sinhalite`
