# Rev1001 bounded resumable cross-file projection audit

## Product question

Rev1000 made cross-file content-defined discovery history-cold and metadata-
bounded, but each plausible source candidate was still hashed to completion in
one reconciliation turn. A wrong candidate in the intended multi-terabyte
Linux media workflow could therefore monopolize the owner thread for a complete
multi-terabyte read before ordinary network, watcher, control, and convergence
work resumed.

Rev1001 changes that latency boundary without weakening payload identity or
publication authority. It does **not** claim that cold discovery now reads fewer
total source bytes. It makes those bytes resumable and bounded per apply turn,
and it allows already completed chunks to produce useful delta progress before
the source's whole manifest is finished.

## Retained design

### One hard projection-hash frontier

`SyncReplicaReconciliationService::apply_response_or_throw` may advance at most
one cross-file source projection per invocation. The product constant is 32 MiB
and is independent of the negotiated four-MiB wire page. A nonterminal
projection step cannot consume more than that frontier.

This separation is deliberate. Wire response size bounds remote memory and
network framing. Local candidate projection is a receiver-side disk-I/O
scheduler. Coupling it to the wire page would add avoidable turns and could
prevent useful chunks from becoming available before the incoming transfer had
already fetched most of the target.

### Process-local move-only continuation

`SyncReplicaFilePayloadStoreContentDefinedProjection` is move-only and hides its
state behind a PImpl. It retains only:

- the exact source whole-payload identity expected by the operation;
- the exact payload size;
- the canonical eleven-field POSIX regular-file observation;
- the exact content-defined chunking parameters;
- resumable whole-file and current-chunk SHA-256 state;
- rolling-boundary state; and
- one bounded vector of completed chunk descriptors.

It retains no descriptor, payload-store lease, namespace capability, or durable
authority. Every later step must reopen the immutable payload through the
ordinary targeted-access owner and match the exact retained observation before
new bytes extend the continuation. A post-read `fstat` must still match. Any
read, arithmetic, allocation, digest, or observation failure clears the
process-local continuation before propagating the error.

### One canonical chunking implementation

The complete descriptor projection and the bounded continuation both use
`ContentDefinedDigestAccumulator`. Boundary selection, chunk segmentation,
whole SHA-256, per-chunk SHA-256, chunk-count limits, and final extent checks
therefore cannot drift into separate implementations.

### Partial chunks are acceleration evidence, not publication authority

As soon as one source chunk is complete, the service adds it to the bounded
source index and may reuse it against the current target frontier. The source
file does not need to be hashed to completion first.

That is safe only because the existing payload-store copy boundary independently
reopens the exact source observation, reads the selected range, hashes the range,
and compares its SHA-256 and size. Reused bytes still enter the existing durable
staging path. The final target whole-payload SHA-256 and ordinary terminal causal
admission remain the only publication authority.

A complete reusable source manifest is retained only after the bounded
projection reaches the exact source extent and its whole SHA-256 matches the
operation identity.

### Late local availability restarts an exhausted search

A current visible candidate can be known causally while its immutable payload is
not locally available. The payload store already owns one process-local,
non-wrapping availability generation that advances only when a new durable
payload identity becomes available. Rev1001 binds the beginning of a candidate
sweep to that generation. If a later insertion advances it, an exhausted search
restarts without requiring a visible-state change.

The generation is acceleration state, not durable evidence. Restarting the
process discards it and the partial source projection; exact payload and causal
authority remain durable elsewhere.

## Memory and latency boundary

For one active cross-file candidate, retained memory is bounded by:

- one move-only projection state;
- one digest per completed content-defined chunk, already bounded by the
  manifest's maximum chunk count;
- one sorted vector of chunk indices;
- one prefix-offset vector; and
- the already bounded current-visible candidate page.

A projection step uses the existing fixed streaming buffer and at most 32 MiB of
source hashing per apply invocation. No candidate-sized string or complete
source byte image is retained.

The bound is on **candidate projection hashing per apply turn**, not every form
of local I/O. At the four-terabyte product ceiling, content-defined chunks can
scale to very large extents; copying one already matched local chunk is still an
ordinary exact-range effect and is not yet resumable under this 32 MiB frontier.
That is an explicit next delta-latency edge rather than a hidden claim.

## Runtime evidence

The payload-store regression advances one projection in five-byte steps through
independently reopened descriptors. It proves the exact per-step frontier,
canonical metadata continuity, cumulative offset and chunk accounting, final
manifest equality with the complete implementation, zero-budget rejection, and
unchanged caller descriptor position. It also proves the local availability
generation advances for new durable identities but not idempotent replays.

The reconciliation regression uses two 48 MiB current-visible candidates:

1. one available unrelated decoy;
2. one matching renamed source whose payload is initially absent.

With a four-MiB wire page and a 32 MiB local projection frontier, the first sweep
skips the absent source and scans the decoy in two bounded turns. Publishing the
matching payload without changing the visible-state digest advances the local
availability generation and restarts the exhausted search. The matching source
is scanned in two bounded turns; completed chunks are reused before its whole
manifest completes; network bytes are materially lower than the target size;
and final payload bytes and causal admission remain exact.

The shipping TLS result and both CLI JSON renderers expose:

- unavailable cross-file candidates;
- availability-generation restarts; and
- bounded manifest projection steps.

## Audit and refactor findings

The first implementation accidentally coupled the local projection budget to
the negotiated wire page. That was removed. The retained 32 MiB frontier is a
product-owned local scheduling constant.

The first runtime oracle also mixed cumulative counters with the current turn's
result. The retained regression distinguishes them and proves the exact ordering:
the absent candidate is skipped before the decoy's two projection steps.

A concurrent writer changed reviewed source files during the first build. That
worktree and its build outputs were excluded. The retained source authority was
moved to a nonce path, rehashed around focused builds, and validated without a
remaining writer touching the authority.

## Explicit nonclaims

Rev1001 does not add:

- a durable or global chunk index;
- fewer total cold bytes for a failed candidate sweep;
- restart persistence for an unfinished source projection;
- a global per-turn cap on matching local chunk-copy I/O;
- multilevel fingerprints for earlier matches in very large adaptive chunks;
- identity-preserving rename or move;
- Android storage and lifecycle support;
- placeholders or polished selective-sync controls;
- target-scale multi-terabyte RSS, disk-amplification, ENOSPC, or route-throughput
  qualification.

Those omissions are product work, not reasons to weaken the bounded authority
implemented here.

## Release cutpoint

Validation: `Exact rev1001 source passed a fresh GCC 14.2 Debug graph (551/551 configured build edges) and a no-work bundled-SQLite re-attestation; all 284/284 registered tests were accounted for, including both final documentation-sensitive audits, and an independent 47/47 product replay passed. Focused GCC proofs passed 677 payload-store, 158 reconciliation-service, 536 folder-owner, 397 SQLite-owner, and 2,044 TLS-transport checks. Source audits passed 32/32 bounded resumable projection, 22/22 inherited cross-file discovery, 31/31 content-defined delta, 27/27 manifest reference, and 521/521 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product dependency graph completed 262/262 edges and reached a no-work re-attestation; all 47/47 product tests were accounted for with leak detection and halt-on-error. Focused sanitizer proofs passed 677 payload-store, 158 reconciliation-service, and 536 folder-owner checks; the folder-owner proof completed in 32.10 seconds at 1,684,368 KiB peak RSS. Aggregate final-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev1000 parent SHA-256 matched c68736ec03cd91298180b689a5c85228cdced06679e3b1fc836949017fd6d8c3 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 21/21 changed wrapper paths, all 20/20 changed project paths, all 17/17 changed active paths, and the complete 612-file active projection byte-for-byte and mode-for-mode. The final active implementation projection contains 612 files / 28,276,868 bytes with SHA-256 9e3197543e4f453cd5bd17897304ab44c3733e08e510a496b391d56383ee3b9e. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excluded remount-vanished worktrees and caches, the divergent availability-only release branch, interrupted aggregate CTest wrappers, superseded lexical-audit failures, and generated Python bytecode removed before projection sealing.`

Archive: `AnonSync-rev1001-2026.08.05.08.49-boundedprojection-lateavailability-singleindex-chrysoprase.zip`

Codename: `chrysoprase`
