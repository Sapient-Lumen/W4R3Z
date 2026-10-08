# Rev1003 bounded same-path predecessor projection and terminal-verification audit

## Product question

Rev1002 bounded copying from a matched local chunk, but the receiver still built
one same-path predecessor manifest by hashing the complete predecessor in a
single reconciliation apply. For the first supported Linux workflow, that
source can be a multi-terabyte media file. A small edit could therefore avoid
most network transfer while still hiding a complete multi-terabyte local read
inside one owner turn.

Rev1003 bounds that predecessor projection to **32 MiB per apply**, reuses
completed adaptive chunks before the whole predecessor manifest is complete,
and keeps final whole-target SHA-256 as publication authority. It does not
pretend that the separate terminal whole-target verification pass is bounded.

## Retained design

### One bounded same-path source step per apply

`SyncReplicaReconciliationService::apply_response_or_throw` may advance at most
one same-path predecessor projection step in one invocation. The shipping
frontier is 32 MiB. A constructor parameter exists only so tests can lower the
frontier; callers cannot raise it above the shipping maximum.

The projection is process-local acceleration. Each step reopens the exact
immutable predecessor through targeted payload access and re-proves the retained
POSIX observation. The payload-store projection owns the rolling chunker,
whole-source SHA-256, completed chunk digests, exact next offset, and parameters.
Any read, arithmetic, integrity, or observation failure clears its private
progress.

Rev1003 also clears the enclosing reconciliation index when a lower same-path or
cross-file projection fails. Before this correction, the lower payload-store
owner deliberately discarded its private projection while the service could
retain offsets and digest-order entries derived from that discarded state. A
later apply could then observe an inactive lower projection beside a nonempty
outer index. The two projection paths now fail at one shared cutpoint.

### Partial chunks are acceleration, never admission authority

A nonterminal step exposes only fully completed adaptive chunks. Rev1003
incrementally appends their exact source offsets and inserts their indices into
canonical SHA-256, size, and source-index order. The same helper now serves both
same-path and cross-file projections, removing two subtly different index
implementations.

Completed predecessor chunks can be matched and copied before the source whole
SHA-256 is known. That is safe acceleration because every copied range is still:

1. selected from a chunk with exact SHA-256 and size;
2. reopened through the immutable payload-store authority;
3. re-proved against the exact source observation;
4. range-hashed before crash-safe prefix staging; and
5. subjected to exact final whole-target SHA-256 before payload publication.

Only completion of the source projection, including exact whole-source SHA-256,
creates the retained complete predecessor manifest and its final index. The
existing `delta_predecessor_manifest_scans` counter therefore counts only a
complete exact manifest. `delta_predecessor_manifest_hashed_bytes` reports the
actual bounded predecessor bytes read by the current apply, including an
incomplete step.

### Bounded memory shape

The incomplete projection retains one rolling hash/chunker state, at most 8,192
completed chunk records, one digest-order index, and one cumulative-offset
vector. It never retains source-file-sized bytes. The incremental insertion is
not claimed to be asymptotically optimal—it can perform quadratic small-vector
moves across at most 8,192 entries—but it removes a second full index-building
implementation and keeps the hard memory frontier explicit.

The incomplete projection is not restart-durable. Reconstructing the service may
rehash an unfinished predecessor prefix. The durable staged target prefix still
preserves already accepted target progress, and a complete predecessor manifest
remains process-local acceleration rather than durable authority.

## Runtime evidence

The focused regression uses a deterministic **48 MiB** predecessor and inserts
256 KiB near the beginning. With the shipping 32 MiB predecessor frontier it
proves:

- exactly two predecessor projection steps are required;
- no apply hashes more than 32 MiB of the predecessor;
- the first step is incomplete;
- completed chunks from that incomplete step are reused before the whole source
  manifest exists;
- aggregate predecessor bytes hashed equal the exact 48 MiB source size;
- one complete predecessor manifest and one final digest index are retained;
- network bytes remain materially below the target size; and
- final payload bytes and causal evidence converge exactly.

The reviewed focused reconciliation-service executable passes **189 checks**
before release sealing.

## Adjacent terminal-verification audit

When the durable staged prefix reaches the target size,
`SyncReplicaFilePayloadStore::stage_payload_prefix_or_throw` still calls
`stream_hash_regular_file_or_throw` over the complete staged target before
publication. This exact whole-target SHA-256 is the correct authority, but it is
an unbounded owner-turn local read. Rev1003 deliberately leaves it intact.

A rejected unsealed prototype encoded raw resumable SHA-256 internal state in a
mutable staged-prefix pathname and attempted to use that state toward terminal
publication. That design was not retained. A parseable pathname-carried hash
state is neither independently checksum-framed nor bound to the exact store
identity, inode observation, durable prefix generation, and crash transition.
It could turn stale or forged acceleration into publication authority, and it
provided no clean migration or verification-only continuation for existing
complete prefixes.

A safe terminal continuation must instead define a separately integrity-framed,
store-identity- and inode-bound verification record; exact crash transitions;
legacy-prefix behavior; failure invalidation; and an explicit distinction
between staging progress and verification progress. It must preserve the final
whole-target digest check rather than replacing it with trusted partial state.
Until that design is proved, the complete terminal rehash is safer than the
rejected shortcut.

## Explicit nonclaims and next risk

Rev1003 does not provide a global bound on all local I/O in an apply. In
particular:

- terminal staged-target verification still reads the complete target in one
  owner call;
- source-side target-manifest construction can still require a complete source
  read;
- incomplete predecessor projection is process-local and can reread after
  restart;
- same-path and cross-file projection each have their own scheduling frontier;
- there is no durable/global chunk index or target-scale multi-terabyte soak;
- page-cache residency, filesystem readahead, durability latency, and ENOSPC are
  separate effects; and
- this revision does not add rename/move identity, directory semantics,
  placeholders, automatic selective eviction, Android support, or polished
  conflict handling.

The next large-file slice should design the integrity-bound terminal
verification continuation, then measure sparse multi-terabyte byte I/O, wall
latency, page-cache/RSS, restart amplification, disk amplification, and
controlled ENOSPC. Those measurements should decide whether a durable bounded
chunk index is justified. Product priority must then return to
identity-preserving rename/move and complete directory semantics.

## Release cutpoint

Validation: `Exact rev1003 source passed a fresh GCC 14.2 Debug graph: 262/262 product-dependency edges plus 290/290 remaining all-target edges (552/552 total), followed by bundled-SQLite re-attestation; all 286/286 registered tests and an independent 47/47 product replay passed. Focused GCC proofs passed 677 payload-store, 189 reconciliation-service, 536 folder-owner, 397 SQLite-owner, and 2,044 TLS-transport checks. Source audits passed 22/22 bounded predecessor projection, 32/32 bounded cross-file projection, 31/31 bounded local reuse, 31/31 content-defined delta, 27/27 multi-range window, 27/27 manifest reference, 21/21 bounded-history access, and 548/548 structural authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 262/262 edges and all 47/47 product tests passed with leak detection and halt-on-error; focused sanitizer proofs passed 677 payload-store, 189 reconciliation-service, and 536 folder-owner checks, with peak RSS 519,504 KiB, 791,616 KiB, and 1,704,200 KiB respectively. Aggregate final-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev1002 parent SHA-256 matched e547cbe11ae3bae98f15946a38f30dd64881510987edac35a6c490a64220bf03 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 14/14 changed wrapper paths, all 13/13 changed project paths, all 10/10 changed active paths, and the complete 614-file active projection byte-for-byte and mode-for-mode. The final active implementation projection contains 614 files / 28,363,976 bytes with SHA-256 16eeae537cb0683f6a51aa044b9c9aea9a44f93ced30530664b5de55cb580aa8. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excluded the remount-vanished initial worktree and build, the rejected raw pathname-carried SHA-state prototype, the stale non-authoritative /home/oai/share validator and its build tree, the initial unbuilt focused-sanitizer target invocation, and the superseded rev0999 lexical oracle failure before its exact cutpoint-owned lifetime check was corrected.`

Archive: `AnonSync-rev1003-2026.08.05.12.35-boundedpredecessor-partialindex-terminalfence-phenakite.zip`

Codename: `phenakite`
