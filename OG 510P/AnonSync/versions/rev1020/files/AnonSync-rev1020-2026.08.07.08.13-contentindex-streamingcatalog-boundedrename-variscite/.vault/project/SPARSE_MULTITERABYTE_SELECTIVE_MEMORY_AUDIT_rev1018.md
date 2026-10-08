# Sparse multi-terabyte selective-sync memory audit — rev1018

## Product question

The first supported workflow is Linux/headless synchronization of media trees
measured in terabytes. Selective synchronization and delta transfer are
mandatory. The immediate scale question is therefore not whether a synthetic
container can allocate several terabytes of dense payload bytes; it is whether
real retained share services can enumerate a large logical tree without making
memory proportional to logical file extent or accidentally opening excluded
payloads.

Rev1018 answers one bounded part of that question with two real
`anonsync_sync run` processes and an exact aggregate sparse logical extent of
4,399,120,252,928 bytes. This is greater than 4 TiB. It is a namespace and
process-memory gate, not a dense-media throughput claim.

## Fixture

Each of two independent shares contains 4,097 regular files. Every file has a
logical `st_size` of 512 MiB and is created with `ftruncate`, so the exact
logical extent per share is 2,199,560,126,464 bytes. The aggregate is
4,399,120,252,928 bytes. The regression requires the fixture's allocated data
blocks to remain below 64 MiB.

Each share uses a default `metadata_only` selective-sync policy plus one deeper
`materialize=needle/keep` rule. The descendant rule prevents pruning the root,
so the rooted scanner must classify all 4,097 root files. None of those files is
selected. The pass must therefore report:

- 4,097 metadata-only regular files per share;
- 2,199,560,126,464 logical metadata-only bytes per share;
- zero selected regular files;
- zero selected classified bytes;
- zero exact local file bytes;
- zero payload-mutation work bytes; and
- a complete end-of-namespace scan.

The 4,097-name shape crosses the retained 4,096-name component-batch frontier.
The diagnostic pass must use two directory enumeration passes and retain no
more than 4,096 selected component names at once.

## C++ correction and diagnostic boundary

`SyncReplicaFolderTraversalSummary` now carries
`metadata_only_regular_file_logical_bytes`. The value is checked arithmetic over
`st_size` from the same no-follow namespace observation that classified each
metadata-only regular file. It is deliberately not allocated blocks, exact retained payload bytes, or
bytes read and hashed. Files beneath a pruned
metadata-only directory are absent because the traversal never enumerates them.

`SyncReplicaFolderPassReport` now copies the exact local traversal's directory
enumeration count, largest selected component batch, and largest simultaneously
retained component count. `anonsync_folder run`, `anonsync_sync once`, and the
share-create initial pass render those values directly. Reporting does not
perform another traversal and does not infer a heap byte count from the number
of names.

The observer regression separately covers two individually classified sparse
metadata-only files whose logical sizes exceed 4 TiB together, one pruned sparse
subtree, one selected three-byte file, checked overflow, and the 4,096-name
batch frontier.

## Real service resource gate

The product regression starts two configured peer services with independent
manifests, databases, payload stores, folder roots, TLS identities, listeners,
and owner-only status sockets. Their outbound direct peers are intentionally
unreachable; the test measures local startup/repair and retained service state,
not payload transfer.

A 24-point `resources-watch` series samples both processes every 75 ms. It
requires stable PID/start-tick identity, the fixed schedule, the released
compact O(processes + samples) series shape, an aggregate sampled PSS below
1 GiB, and a summed Linux lifetime peak RSS below 1.5 GiB. The thresholds are
release tripwires, not expected operating targets. The focused GCC run observed
16,280 KiB aggregate peak sampled PSS and 60,796 KiB summed lifetime peak RSS.
Final release evidence records the clean authoritative rerun.

The services must become ready in the same processes, remain owner-control
responsive, stop cleanly, and leave the subsequent exact diagnostic pass with
the logical-byte, zero-payload-work, and 4,096-name batch evidence above.

## Adjacent audit and refactor

The working tree initially contained a divergent unsealed rev1018 CPU/I/O
prototype and validation prose not reconstructible from sealed rev1017. Those
surfaces were removed. The retained revision is exactly the sealed parent plus
the reviewed history-cold peer-service startup correction and this sparse
selective-memory gate. A persistent Git authority records both commits before
release evidence is generated.

The measurement also prevents a cosmetic duplicate high-water field. Rev1017
already reports Linux `ru_maxrss` as `peak_rss_kib`; rev1018 composes that
existing lifetime signal with sampled PSS rather than inventing another
near-synonym.

## What this proves

Rev1018 proves that, in this Linux cloudtainer and this exact fixture:

- logical file extent does not become retained payload memory for metadata-only
  selection;
- two real services can classify an aggregate sparse tree greater than 4 TiB;
- a 4,097-entry directory crosses the 4,096-name batch boundary without
  unbounded component retention;
- excluded regular files spend no selected byte or payload-mutation budget; and
- the observed two-process sampled PSS and lifetime peak RSS remain far below
  the release tripwires.

## Nonclaims and next product edge

Sparse files do not model dense-media I/O, page-cache residency, filesystem
allocation pressure, network throughput, delta-transfer throughput, or disk
amplification. A 4,097-file directory is not a million-file tree. Sampled PSS
can miss between-point transients, although Linux lifetime peak RSS covers the
largest resident high-water mark reported by the kernel. Neither signal
attributes allocator fragmentation or cgroup pressure.

This revision does not complete identity-preserving rename/move, directories or
empty directories, human conflict handling, placeholder selective sync,
automatic eviction, best-effort retention collection, quota/ENOSPC recovery,
Android lifecycle/storage integration, or live public Tor/I2P qualification.
Delta synchronization remains mandatory and already has bounded
content-defined reuse, but this sparse metadata gate does not qualify dense
transfer speed.

The next product edge should return to file semantics: identity-preserving
rename/move first, then complete directory and empty-directory behavior,
understandable conflicts, and controlled ENOSPC. Dense multi-terabyte and
million-file scale tests should grow alongside those semantics rather than
being replaced by this sparse proof.

## Validation

`Exact rev1018 source passed a fresh GCC 14.2 Debug graph (578/578 configured build edges), all 310/310 registered tests, and an independent 56/56 product replay. Focused GCC proofs passed 22 history-cold source-frame/startup checks, 26 real sparse multi-terabyte process checks, 90/90 folder-observer checks, 6/6 observer-race checks, and 557 folder-owner checks. Source audits passed 19/19 history-cold startup checks, 18/18 sparse multi-terabyte checks, and 690/690 structural authority checks. A fresh Clang 17 ASan/UBSan product graph completed 286/286 edges and all 56/56 product tests passed with leak detection and halt-on-error. The exact rev1017 parent SHA-256 matched and passed 41/41 wrapper-aware package checks. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The obsolete predictable-path validator, its kill guard, interrupted caches, and divergent branches are excluded.`

## Intended archive

`AnonSync-rev1018-2026.08.07.02.31-historycold-sparsefourterabyte-memoryproof-danburite.zip`
