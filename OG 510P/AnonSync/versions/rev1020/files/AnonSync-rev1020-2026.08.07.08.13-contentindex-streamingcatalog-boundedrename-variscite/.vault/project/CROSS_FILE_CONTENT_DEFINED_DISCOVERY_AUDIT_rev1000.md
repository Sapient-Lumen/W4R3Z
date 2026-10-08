# Cross-file content-defined discovery audit — rev1000

## Product reason

The first supported workflow is Linux/headless synchronization of selective
media trees measured in terabytes. Delta transfer is mandatory. Rev0994 can
reuse content-defined chunks from a same-path causal predecessor, but a user
rename, organizer move, duplicate import, or application-generated replacement
at another path has no predecessor edge. The receiver can already possess most
of the target bytes under another current filename and still retransmit them.
That is a material Resilio-replacement gap for large media libraries.

Rev1000 adds one bounded receiver-side discovery path over the existing current
visible SQLite projection. It does not add a second synchronization engine,
change protocol generation 7, or turn a chunk match into publication authority.
The existing payload-before-operation order, durable prefix, exact chunk digest,
whole-payload SHA-256, and terminal causal admission remain authoritative.

## Current-visible candidate page

`SyncReplicaSqliteOwner::visible_file_candidate_page_or_throw` walks current
primary visible values in canonical path order. Its hard product frontier is:

- at most 64 visible paths per page;
- at most 4 MiB of canonical operation bytes per page; and
- one SQL lookahead row beyond the path frontier.

Callers cannot raise those ceilings. A continuation path is accepted only with
the exact visible-state digest from the preceding page and must still name one
current primary visible path. A stale digest returns `SourceChanged` before the
cursor or operation rows are decoded.

The query is a primary-key range over `sync_replica_visible`, joined to the one
named immutable operation row. It does not call `load_state_or_throw`, enumerate
all retained evidence, reconstruct a causal graph, or sort a complete visible
projection. Tombstone primaries consume the path and canonical-byte frontier but
are omitted from `file_operations`, so a deletion prefix cannot starve the
cursor.

This page is acceleration evidence only. It grants no payload-presence,
publication, conflict-resolution, retention, deletion, or rename authority.

## Bounded discovery state

The reconciliation receiver retains at most one candidate page and one selected
candidate manifest for the current target manifest. The page is moved into the
service and consumed across bounded apply turns rather than re-querying its tail
after every failed candidate. This removes an otherwise quadratic 64 + 63 + ...
page-tail rescan pattern while keeping the metadata owner bounded by the exact
4 MiB canonical frontier.

Per `apply_response_or_throw` invocation, discovery performs at most:

- one current-visible SQLite page read; and
- one complete candidate content-defined manifest projection.

Cheap exclusions may skip more than one page entry without hashing: the target
path itself, the exact target content identity, candidates outside one maximum
chunk of the target size, and candidates whose immutable payload is absent.
Only current visible File operations are considered. Superseded history is not
reconstructed or searched.

A complete candidate manifest is streaming and memory-bounded, but it may still
read the candidate's complete bytes. Thus one turn can perform large disk I/O
for a multi-terabyte candidate. Rev1000 bounds count and memory, not candidate
hash latency. A durable global chunk index or multilevel fingerprint remains a
future performance surface.

## One local copy boundary

The same-path predecessor path and the cross-file path now share
`reuse_local_candidate_chunks_or_throw`. That boundary:

- starts from the receiver's exact durable target prefix;
- requires a target content-defined chunk boundary;
- finds a source chunk by exact SHA-256 and size;
- reopens the exact immutable source operation for every bounded copied range;
- reads through the payload-store descriptor capability;
- stages through the existing durable target-prefix owner; and
- leaves final whole-payload SHA-256 verification and operation admission
  unchanged.

The refactor removes two almost-identical range-copy engines that could have
drifted in lease, reproof, staging, or counter behavior.

## Regression shape

The focused service regression constructs:

- one unrelated current 48 MiB media file;
- one current 48 MiB source file under a different path;
- one 48 MiB target with a 256 KiB insertion near the front and a distant byte
  edit; and
- 4 MiB network windows.

It independently projects the three manifests, proves the unrelated file has no
target chunks, and proves the renamed source retains at least four matching
chunks and 16 MiB of reusable content. The transfer then proves:

- no same-path predecessor exists or is consulted;
- one two-path current-visible SQL page is retained across turns;
- exactly two candidate manifests are hashed, at most one per turn;
- one candidate is selected and its index is reused;
- a substantial target suffix is staged from local immutable bytes;
- network bytes are materially below the target extent;
- exact final target bytes and target operation converge; and
- candidate discovery performs zero evidence-page reads.

The owner regression separately proves tombstone continuation, exact cursor
validation, stale-digest early return, hard page ceilings, and absence of
complete operation or visible-projection reads.

## Memory boundary

The added live state is bounded by:

- one page of at most 64 `SyncReplicaOperation` values and 4 MiB of canonical
  bytes;
- one candidate manifest of at most 8,192 chunk records;
- one cumulative-offset vector and one digest-order index for that manifest;
- the already retained target manifest and range buffers.

No new structure grows with tree path count, retained-history count, payload
extent, or number of payload objects. The candidate manifest vectors grow with
the existing fixed 8,192-chunk protocol frontier, not file bytes.

## Nonclaims

Rev1000 does not provide:

- a durable or global cross-file chunk index;
- a content-addressed search across every retained payload;
- more than current-visible candidate discovery;
- bounded candidate-hash byte latency;
- automatic retry when a previously absent candidate payload appears after an
  exhausted same-process search without visible-state change;
- identity-preserving rename or move;
- directory or empty-directory semantics;
- selective-sync placeholders or polished UI;
- quota, ENOSPC, retention collection, or garbage collection;
- Android storage/lifecycle support; or
- measured public-route or multi-terabyte throughput qualification.

Exact-content duplicates already share the payload store's content identity;
this slice primarily accelerates renamed or duplicated files whose content has
also shifted or changed.

## Validation

Exact rev1000 source passed a fresh GCC 14.2 Debug graph (551/551 configured build edges) and a no-work bundled-SQLite re-attestation; all 283/283 registered tests were accounted for, including the two final documentation-sensitive source audits, and an independent 47/47 product replay passed. Focused GCC proofs passed 397 SQLite-owner, 144 reconciliation-service, 536 folder-owner, and 2,044 TLS-transport checks. Source audits passed 22/22 cross-file discovery, 31/31 content-defined delta, 27/27 manifest-reference, and 511/511 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product dependency graph completed 262/262 edges and reached a no-work re-attestation; all 47/47 product tests passed with leak detection and halt-on-error. Focused sanitizer proofs passed 397 SQLite-owner, 144 reconciliation-service, and 536 folder-owner checks; the folder-owner proof completed in 29.87 seconds at 1,690,840 KiB peak RSS, the reconciliation-service proof in 30.17 seconds at 774,444 KiB, and the SQLite-owner proof in 11.38 seconds at 777,440 KiB. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0999 parent SHA-256 matched 7b897c44e66870dd55e5df707d5d5e5180f60edbbe2baf4af431b861490cd3e0 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 20/20 changed wrapper paths, all 19/19 changed project paths, all 16/16 changed active paths, and the complete 611-file active projection byte-for-byte and mode-for-mode. The final active implementation projection contains 611 files / 28,197,616 bytes with SHA-256 9653cca2703de4448b510a49c8321d95c72354716de08152bedaec8185197c05. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excluded remount-vanished worktrees and caches, timestamp-only CMake regeneration attempts, interrupted aggregate real-process harnesses, a divergent indexed cross-file prototype and its validators, unrelated build lanes, and a redundant terminated sanitizer rerun.

## Archive

`AnonSync-rev1000-2026.08.05.06.02-crossfilechunks-visiblepage-singlehash-hackmanite.zip`

Codename: `hackmanite`
