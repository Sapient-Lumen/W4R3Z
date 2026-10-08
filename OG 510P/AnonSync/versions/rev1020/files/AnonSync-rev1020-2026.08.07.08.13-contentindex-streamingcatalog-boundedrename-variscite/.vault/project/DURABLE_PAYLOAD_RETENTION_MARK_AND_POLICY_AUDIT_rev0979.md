# Durable payload-retention mark and conservative policy audit — rev0979

## Mission boundary

AnonSync exists to replace Resilio Sync with one practical C++ folder-sync
product. A bounded append-only payload store is part of that product obligation:
operators need predictable storage, retained versions need understandable loss
semantics, and synchronization must not fail merely because old immutable bytes
accumulate forever.

Deletion authority is unusually dangerous. A payload that appears unreferenced
at one instant may still be named by causal history, inactive evidence, an
explicit retention pin, a staged transfer, a live sender descriptor, another
same-process owner, or a cooperating process that opened the exact inode. The
correct next step after rev0978 is therefore not unlink. It is one durable,
identity-bound historical record of the deletion-free candidate cutpoint and
explicit conservative policy that produced it.

Rev0979 implements that mark. Publication does not add a second complete
payload scan or hash pass beyond the existing writer-fenced retention
observation; that observation still hashes payloads whenever exact process or
durable verification evidence cannot be reused. The revision does not collect,
quarantine, rename, or unlink a payload. It does not claim that the supplied
wall clock is trusted, that grace elapsed, that quota pressure exists, or that
every transient product lifetime has a durable root.

## Defect 1: the restart-stable candidate witness was not persisted

Rev0978 computed a page-invariant candidate witness while retaining the exact
store-global writer fence. The witness survived pagination differences but was
returned only to the caller. After process restart, an operator or future
collector could recompute a new plan, but there was no durable answer to:

- which exact operation, evidence, explicit-pin, visible-state, payload, and
  transient-namespace cutpoints were marked;
- which same-lineage replica-owner generation produced those digests;
- which complete unreferenced candidate-set digest and cardinality were seen;
- which count, byte, collection, and grace frontiers the owner intended; or
- whether a later record was a replacement of earlier usable evidence.

A restart-stable candidate digest without a durable owner was therefore a
necessary observation primitive, not a retention-policy state machine.

## Fixed-width record

The payload-store owner now recognizes exactly one internal basename:

```text
.anonsync-payload-retention-mark-v1
```

The record is fixed-width, big-endian, and checksum-framed. It contains:

- the SHA-256 of the immutable expected payload-store identity;
- the exact eleven-field private single-link POSIX observation of the locked
  identity-marker inode;
- a nonzero replacement generation that advances only across a usable
  predecessor;
- the supplied nonzero mark time and bounded grace interval;
- maximum candidate count and bytes;
- maximum future collection count and bytes;
- the source replica-state generation, monotonic within one retained SQLite
  database lineage;
- exact operation-set, inactive-evidence-set, explicit-pin-set, visible-state,
  payload-snapshot, and transient-namespace digests;
- the complete unreferenced candidate-set digest;
- the page-invariant durable candidate-witness digest; and
- exact unreferenced candidate count and bytes.

The trailing lowercase SHA-256 covers the magic and complete body. Parsing
requires the exact v1 byte count, canonical lowercase digests, a private
single-link identity observation, nonzero generations and time, a grace horizon
of at most ten years, overflow-safe grace arithmetic, policy frontiers within
the configured payload-store limits, a nonempty candidate set, and collection
frontiers no larger than the observed candidates.

The record has no `reclaimable`, `eligible`, `quarantined`, or `unlink` field.
A structurally usable record is historical evidence, not current collection
authority.

## Exact writer-fenced publication handoff

`SyncReplicaFolderScanOwner::mark_payload_retention_or_throw()` accepts:

- one exact current v4 retention source cutpoint;
- the source replica-state generation, monotonic within one retained SQLite
  database lineage;
- the complete durable candidate-witness digest;
- one supplied mark time; and
- the bounded conservative policy.

Malformed policy and candidate count/byte frontiers above the exact configured
store capacity are rejected before paying for a complete payload observation.
The store-aware validator is shared with record serialization, so the early
owner check and durable codec cannot drift into different capacity contracts.
A focused regression holds an independently opened exclusive lock on the exact
identity inode while submitting both impossible frontiers; receiving the
capacity diagnostics proves rejection occurred before writer-fence acquisition,
and a following snapshot proves no mark or payload/transient namespace state
changed. The owner then reuses the existing retention planner with a one-entry
presentation page. The page limit does not narrow the mark: the candidate-set
and durable-witness digests still cover the complete physical namespace.

The same `SyncReplicaFilePayloadStoreSnapshot` that recomputes the witness holds
the exact store-global exclusive identity lease. Publication accepts only that
snapshot issued by the exact retained store owner, including its verification
cache, integrity epoch, rooted authority, folder identity, limits, and live
capability registration. It does not reacquire a weaker owner, drop the writer
fence, or perform a second complete payload-root scan.

The payload-store owner overwrites caller-supplied identity and generation
fields. It observes the current record beneath the retained fence, increments a
usable predecessor generation, or conservatively starts at generation one when
the predecessor is absent or unusable. It then performs an atomic create or
exact-metadata conditional replacement, reopens and parses the committed file,
compares the complete record and checksum digest, and re-proves the retained
writer fence and rooted identity before returning.

An exception after atomic publication is handled conservatively. The owner
reopens the destination; if the exact requested record committed, that exact
publication is returned. Otherwise the original exception is preserved. The
reconciliation observation is explicitly best effort: its own open, parse,
allocation, or rooted-reproof failure cannot mask the primary publication
failure. No payload name is renamed or unlinked in either path.

## Same-lineage causal ABA fence and rollback boundary

Content digests alone cannot bind elapsed grace. An explicit historical pin can
be removed and later restored, returning the operation, evidence, pin, visible,
payload, transient, candidate, and durable-witness digests to their earlier
values. Inheriting the old mark across that interval would let a changed causal
world reuse old grace.

The durable mark therefore binds the SQLite owner's `state_generation`. That
value is monotonic across ordinary mutations in one retained replica-database
lineage. The request must match that generation before payload observation and
immediately before publication. After the mark commits, the folder owner takes
a fresh SQLite snapshot and compares the generation and all source digests
again. Source drift becomes the typed stage `retention_mark_publication`.

A mark may have committed before that final typed failure. This is intentional
crash semantics, not success: the committed record names the older forward
lineage and is conservative stale evidence. A future collector must require
current generation and digest equality; it may never infer freshness merely
because the method once returned or because the content digests later match.

`state_generation` is not an external anti-rollback counter. Replacing the
replica database with an exact older image can recreate its generation and all
source digests. The product-bound payload identity prevents cross-deployment
recomposition, but it does not prove that the paired SQLite database stayed on
its newest lineage. Rev0979 is safe because a mark grants no collection
authority. A future collector must additionally bind an externally anchored
replica-database incarnation or recovery epoch, or invalidate every previous
mark age whenever database replacement or rollback is possible.

The mark's own replacement generation is continuity evidence only while the
predecessor record remains structurally usable. Clean absence or unusable
evidence starts again at generation one. It therefore cannot prove freshness,
elapsed grace, or total ordering across record loss, damage, or replacement.

## Metadata cannot invalidate its own witness

The retention mark is recognized internal metadata. It is excluded from:

- physical payload entry count and indexed bytes;
- transient entry, byte, and reserved-byte accounting;
- the canonical payload snapshot digest; and
- the canonical transient-namespace digest.

This is not an accounting exemption for arbitrary files. The basename is fixed,
private, descriptor-opened without symlink following, observed before and during
namespace traversal, and re-proved by exact inode metadata. Fresh product-bound
bootstrap refuses to adopt a pre-existing mark. A malformed, torn, wrong-size,
or stale-identity file is present-but-unusable and can only be replaced through
the same retained writer-fenced publication path.

Excluding the record from the candidate witness is necessary: publishing a mark
must not change the physical candidate cutpoint that the mark records. The
record remains independently visible through the snapshot metadata API.

## Observation-known refactor

The first implementation exposed only `retention_mark_present()` and
`retention_mark_usable()`. That made two different states look identical:

- a synchronized writable scan that read a damaged or stale record; and
- `ReadOnlyInspect`, which deliberately remained byte-cold and did not parse the
  record at all.

Rev0979 adds `retention_mark_observation_known()`. Writable synchronized scans
report it true for both clean absence and an observed present record.
`ReadOnlyInspect` reports namespace presence but observation-known false. This
keeps forensic inspection byte-cold without describing uninspected bytes as
known-invalid evidence.

## Policy boundary

The persisted policy is deliberately conservative and incomplete. It records:

- a minimum grace duration;
- the maximum candidate count and bytes the owner was willing to mark; and
- maximum count and bytes that a later collection attempt may consider.

Those fields limit later authority; they do not create it. Rev0979 does not:

- choose candidates by individual age;
- define a trusted real-time clock or clock-rollback behavior;
- measure share quota, free space, or ENOSPC pressure;
- determine user-visible version loss;
- define minimum retained versions per path;
- bind copied outbound buffers or every active receiver/publication lifetime;
- stage collection-specific quarantine;
- rehash candidate bytes after restart; or
- rename or unlink any payload.

The supplied Unix time is operator evidence only. A later collector must define
its trusted clock source, reject backward or implausible time movement, reacquire
the global writer fence, completely reobserve all durable and process-local
roots, acquire exact-inode exclusive leases, prove current bytes, and apply a
separate collection quarantine/restart protocol before unlink.

## Compatibility boundary

Rev0978 and earlier complete payload-store scans do not recognize the new
internal basename and therefore fail closed after a rev0979 mark exists. They do
not reinterpret the record as payload or collection authority. Rev0979 does not
raise the immutable payload-store identity generation because the safety
property is fail-closed availability, not split mutation authority. Downgrade
operation after mark publication is not promised; an eventual release that
requires mixed-reader availability should introduce an explicit reader-floor
migration rather than silently weakening namespace policy.

## Contamination and reconstruction audit

During implementation, a separate unsealed rev0979 process modified the first
shared worktree with a divergent retention-intent design and speculative query
fields. Its header, implementation, and test were internally inconsistent. The
process was stopped, its exact files and patch were retained as read-only
forensic evidence outside the release tree, and no result from that worktree is
release authority.

The accepted implementation was reconstructed from the exact sealed rev0978
archive in an isolated directory. Only deliberately reviewed changes were
reapplied. The standalone codec was compiled and tested before payload-store
integration, then the store and folder-owner paths were validated together.

## Validation

Exact rev0979 C++ source passed a clean GCC 14.2 Debug graph (532/532 configured build edges), 258/258 preseal registered runtime tests, and an independent 40/40 GCC product replay in 114.17 seconds. The finalized registered structural authority audit passed 362/362 checks, accounting for all 259/259 registered tests across the unchanged C++ bytes and final release prose. Focused exact-source suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 30 retention-mark, 640 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 320 SQLite-owner, 463 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 158 local-control, 87/87 observer, and 6/6 observer-race checks. A clean Clang 17 Debug product dependency graph completed 243/243 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 40/40 product tests passed serially in 155.48 seconds with leak detection and halt-on-error. Focused sanitizer proof passed the 640-check payload-store suite in 11.33 seconds at 514,824 KiB peak RSS, the 463-check folder-owner suite in 37.23 seconds at 1,467,772 KiB peak RSS, and the 158-check local-control suite in 0.68 seconds at 113,860 KiB peak RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0978 parent SHA-256 matched 5d8c9bc1470f3c7bcd38ed039dc69d766bc1ff9fdddba1ee4ef9de49a045d734 and passed 41/41 wrapper-aware package checks. Validation excluded source-divergent retention prototypes, shared-cache and in-tree build contamination, self-restarting mutable-source launchers, interrupted rev0979-named sanitizer processes, and every result not bound to the byte-reconciled clean source. The binary-aware source patch reconstructed all 13/13 changed active files and the complete 573-file projection byte-for-byte and by mode. The final active implementation projection contains 573 files / 26,681,569 bytes with SHA-256 7ef1c72b253f25a8e8fb1154aafbc4ce0220891b4de7eebef6ce139eb76e7f7b.

## Next safe edge

The next useful slice is not unlink. It should expose one owner-only mark
operation and status view only after defining a trusted time source and
operator-visible policy semantics. A later collection attempt must consume the
record as stale-until-reproved evidence, reacquire the writer and inode fences,
completely reobserve causal and transient roots, rehash bytes, move candidates
to collection-specific quarantine, survive restart, and only then unlink under
an explicit user-restorable loss policy.
