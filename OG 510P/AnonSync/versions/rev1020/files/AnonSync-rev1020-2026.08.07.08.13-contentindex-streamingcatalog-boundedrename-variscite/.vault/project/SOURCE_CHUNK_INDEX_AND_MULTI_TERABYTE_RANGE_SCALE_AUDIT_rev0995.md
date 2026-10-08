# Source chunk index and multi-terabyte range-scale audit — rev0995

## Product reason

AnonSync's first supported workload is a Linux/headless multi-terabyte media
tree. Content-defined shifted reuse is necessary for that workload, but its
source-side implementation must also avoid repeating bounded work once for every
wire range of one very large file.

Rev0994 retained the source content-defined manifest across an authenticated
serve session, yet each ranged response reconstructed the complete cumulative
chunk-offset vector from that manifest. The operation was bounded in isolation,
but multiplied by the number of 4 MiB wire ranges.

## Exact maximum-shape multiplier

At the current exact 4 TiB payload frontier and default 4 MiB wire range:

- range turns: 1,048,576;
- maximum content-defined chunks: 8,192;
- redundant cumulative prefix additions: 8,589,934,592;
- temporary offset-vector element traffic: 68,727,865,344 bytes;
- equivalent element traffic: 64.0078125 GiB before allocator/container overhead.

This is not a claim that 64 GiB was simultaneously resident. It is exact
avoidable allocation-and-initialization traffic over one uninterrupted maximum-
extent transfer.

## Retained correction

`SyncReplicaReconciliationServeSession` now owns one cohesive bounded source
cache. The cache binds:

- exact payload SHA-256 and size;
- exact rooted descriptor observation metadata;
- the canonical content-defined manifest;
- the exact manifest digest; and
- the cumulative chunk-offset vector derived from that manifest.

A source change resets that object as one unit. A cold manifestation builds the
cumulative index once. Valid later range requests reuse it. Parallel optional and
scalar cache members were removed so manifest identity, descriptor observation,
digest, and offsets cannot acquire different lifetimes.

The index remains bounded by the existing 8,192-chunk manifest frontier. The
change does not introduce payload-size-proportional storage.

## Failure ordering

A continuation's cached manifest digest is checked against the current exact
source cache before source chunk lookup and before `copy_range_or_throw`. A stale
or forged reference therefore cannot consume chunk-index lookup work or payload
range-copy work after the current rooted payload has been opened and re-proved.

The negative regression records the counters immediately around that rejection.
It proves the unusable reference does not advance index-reuse or lookup evidence
and cannot mutate receiver state.

## Operator-visible accounting

The source session, TLS result, and shipping JSON now expose independent counts
for:

- content-defined chunk-index builds;
- content-defined chunk-index reuses; and
- content-defined chunk-index lookups.

The focused source and authenticated TLS regressions prove one cold build and
many exact later lookups. The shifted-predecessor regression proves the count is
one build for the complete ranged successor, not one build per range.

## Adjacent audit/refactor

Two older lexical audit oracles still named rev0994's parallel source-cache
members and one cache-state phrase. They were corrected to inspect the cohesive
cache and current receiver-cache terminology. The change does not weaken their
request-scoped source-authority or manifest-reference requirements.

A divergent unsealed rev0995 prototype implementing compact binary manifests was
found in a separate worktree. It is not part of this revision, was not merged,
and supplies no validation authority.

## Remaining scale frontier

Rev0995 removes the repeated cumulative-index build. It does **not** remove the
larger one-range-per-request/response transport multiplier. A 4 TiB file at a
4 MiB wire range still requires 1,048,576 serialized request/response turns even
when every manifest and index cache is hot.

The next product slice should add one bounded multi-range or byte-window frame:

- one request names an exact continuation and a bounded byte budget;
- one response carries several canonical chunk-confined ranges up to that budget;
- every range keeps its existing digest, chunk-boundary, durable-prefix, and
  final whole-file verification rules;
- framing remains bounded independently of file size; and
- restart resumes from the already durable prefix rather than remembered network
  state.

Only measurement can choose the useful window size and determine whether TLS
framing, hashing, disk I/O, or predecessor discovery becomes the next limit.

## Nonclaims

Rev0995 does not claim a completed multi-terabyte transfer, target-scale peak RSS,
constant transfer time, cross-file chunk discovery, multilevel delta,
compression, Android support, rename/move identity, directory semantics,
placeholder selective sync, quota safety, or ENOSPC qualification.

## Validation

Exact rev0995 source passed a fresh 545-edge GCC 14.2 Debug graph and a no-work bundled-SQLite re-attestation; all 274/274 registered tests were accounted for across bounded terminal shards and an independent 44/44 product replay passed. Focused GCC proofs passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 650 payload-store, 39 content-defined-chunker, 98 network-model plus 41 generated-operation, 361 SQLite-owner, 536 folder-owner, 110 sync-once, 4,956 reconciliation-protocol, 115 reconciliation-service, and 2,044 TLS-transport checks. Source audits passed 18/18 source-chunk-index, 31/31 content-defined-delta, 27/27 manifest-reference, 33/33 targeted-source-access, 52/52 selective-sync, and 463/463 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 256/256 edges; all 44/44 product tests passed with leak detection and halt-on-error, and focused sanitizer proofs passed 650 payload-store, 39 content-defined-chunker, 4,956 reconciliation-protocol, 115 reconciliation-service, and 2,044 TLS-transport checks. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0994 parent SHA-256 matched cce60aea2ce146228f5163720b74b1ec666b3e56e204c5f155108d22f91ecd9a and passed 41/41 wrapper-aware package checks. The active implementation projection contains 602 files / 27,851,618 bytes with SHA-256 98fd496d786433027529c2628adc2a0f1e12c029300cb1084bd55804c965d7c1. Final directory, ZIP, CRC, path-policy, no-symlink, and clean-extraction equality checks remain mandatory publication gates.

## Archive

AnonSync-rev0995-2026.08.04.19.00-sourceindex-millionrange-framingfrontier-indicolite.zip
indicolite
