# AnonSync rev0954 revision notes

## Mission

AnonSync remains one practical C++ replacement for the personal Resilio Sync
workflow: continuous authenticated folder convergence over direct TCP, Tor, and
I2P, with ordinary setup, restart, recovery, and bounded resource behavior.
Rev0954 removes avoidable restart I/O from the shipping private payload store and
audits the inherited rev0953 settlement boundary. It does not add another sync
engine, policy daemon, or source of synchronization truth.

## Product correction: durable payload verification checkpoint

Before rev0954, a process could reuse exact payload observations only until it
exited. Every fresh process still enumerated, opened, and SHA-256 hashed every
retained payload byte before ordinary work. At the production 64 GiB indexed-byte
default, an unchanged restart could therefore read tens of gigabytes even though
no payload had changed.

The payload store now owns one checksum-sealed fixed-width v1 checkpoint at
`.anonsync-payload-verification-index-v1`. It binds the exact store-identity
marker and records sorted digest-named payload metadata: device, inode, type/mode,
link count, owner/group, size, mtime, and ctime including nanoseconds. A fresh
process may reuse an entry only after it independently enumerates and rooted-opens
the digest basename under the ordinary shared store lease and observes every
recorded field exactly. Missing, malformed, oversized, checksum-invalid,
identity-mismatched, or metadata-stale entries grant no reuse; the complete file
is streamed through SHA-256 and checked against its basename.

The full namespace scanner remains authority. It still enumerates every entry,
checks namespace shape and all capacity ceilings, opens/stats every admitted
object, and performs complete hashing for every observation not exactly covered
by process-local or durable metadata. `ReadOnlyInspect` is intentionally cold and
ignores both accelerators. Hashed/reused work counters, including separate
process and durable origins, never enter the canonical snapshot digest.

## Crash ordering and bounded publication

Ordinary snapshots remain shared observations and never write. Only after a
complete shared snapshot has been returned and its lease released may a
best-effort refresh take a fail-fast exclusive lease, re-scan the exact namespace,
and atomically create or expected-metadata replace the checkpoint. Mutation
batches and completed range receivers already own exclusive authority and a
complete exact index, so they may publish without an additional namespace scan.
Post-rename descriptor metadata is retained so a POSIX rename ctime transition
does not force an unnecessary restart hash.

Checkpoint writes are geometric rather than per payload: thresholds are clamped
to 256–4,096 added entries and 64 MiB–1 GiB added bytes, with one graceful final
attempt. The fixed-width encoded size is checked against the existing transient
writer budget before the O(namespace) index is constructed or serialized.
Publication failure, contention, ENOSPC, stale expected metadata, or allocation
failure can only lose acceleration; it cannot change the already-proved payload
snapshot or a completed payload publication.

## Audit/refactor: retain negative checkpoint-capacity evidence

A focused capacity audit found a repeatable waste path. When the transient budget
could not fit even one checkpoint-writer residue, a restart snapshot performed
its authoritative full namespace scan, then the optional refresh performed a
second complete scan merely to rediscover that publication was impossible.
Graceful teardown could repeat the same doomed scan, and later snapshots could do
so again.

The process-local checkpoint scheduler now retains the exact result of the
complete scan's fixed-width capacity preflight. A known-unavailable observation
suppresses the optional refresh and graceful retry until a later complete scan
replaces that evidence or a payload mutation invalidates it. The snapshot exposes
`verification_checkpoint_deferred_by_transient_capacity()` as noncanonical work
diagnostics. A 128-byte transient-budget regression proves cold authoritative
hashing, repeated process-local reuse, persistent deferral, and absence of the
checkpoint file. This is scheduling evidence only: another process may free
capacity after the observation, in which case this process merely misses an
acceleration opportunity until its next complete scan.

## Audit/refactor: checkpoint process-cache re-verification immediately

A second restart-cost audit found a narrower but avoidable repeat-read path.
Once a process had consumed an exact durable checkpoint, later snapshots could
reuse the process-local generation without rereading the potentially large
checkpoint file. If one payload's live metadata then changed while its bytes
remained exact, that same process correctly rehashed the cache miss and
published a replacement in-memory generation—but it did not mark the durable
checkpoint stale. The next process therefore repeated a full byte proof that
its predecessor had already completed successfully.

The checkpoint observation owner now forces one best-effort refresh whenever a
process-cache-backed complete scan hashes any payload, or when exact namespace
entry count or indexed-byte totals differ from the last durable baseline. The
refresh remains outside the authoritative shared observation, re-scans under an
exclusive lease, repeats the transient-capacity preflight, and may fail without
changing the returned payload snapshot. A restart regression rewrites one
payload in place with identical bytes, proves the retained owner hashes it once,
then proves a fresh owner obtains durable reuse without hashing it again.

## Audit/refactor: prove cache ownership before scheduler reads

The verification generation and checkpoint scheduler are intentionally
unsynchronized because every store and detached mutation batch is bound to the
process/thread incarnation captured by its rooted directory authority. A teardown
review found that three best-effort paths violated the documented ordering: they
read scheduler state or the shared-cache owner count before proving the calling
thread. Correct callers were unaffected, but concurrent foreign-thread misuse
could enter an ordinary C++ data race before the authority's eventual fail-stop
lifetime check.

The internal directory-authority bridge now exposes a cheap owner-only proof that
checks process/thread incarnation without reopening or statting the filesystem.
Checkpoint refresh, graceful store teardown, and detached batch teardown perform
that proof before any cache generation, scheduler, or `shared_ptr` owner-count
inspection. Full rooted and lease proofs remain mandatory before filesystem
publication. Clean no-op teardown therefore preserves the inexpensive path while
the deliberately mutex-free cache no longer precedes its thread-affinity fence.
The structural audit binds the declaration, implementation, and all three call
orderings.

## Integration correction: staged-prefix namespace vocabulary

The first checkpoint implementation updated the complete payload scanner but
missed the receiver's lightweight staged-prefix namespace observer. Once the
internal checkpoint existed, ranged reconciliation could reject it as an
unexpected payload-root entry.

Both production `fdopendir` loops are now audited. The staged-prefix observer
pre-observes the exact checkpoint, recognizes it during complete lexical
enumeration, rejects appearance/disappearance/duplication or metadata drift, and
re-proves the pathname at its final traversal cutpoint without reading unrelated
payload bytes. A regression seeds a checkpoint, completes a bounded prefix
transfer, restarts, and proves exact reuse of both the seed and post-rename
received payload.

## Reconstruction audit: stale objects and settlement regression

The surviving unsealed work had been composed from independent branches. A
source-fresh rebuild exposed a constructor mismatch hidden by stale Ninja object
files: the mutation-batch state had gained process-versus-durable reuse counters,
but its production constructor call still supplied the old argument list. The
final source initializes, aggregates across cleanup rescans, and passes all four
origin counters; focused runtime tests bind the partition. Final validation uses
fresh build directories rather than trusting timestamp-retained objects.

Reconstructing rev0954 over the exact sealed rev0953 project exposed a more
serious branch regression. The unsealed checkpoint branch had silently removed
rev0953's equality check between the pass's published remote fairness cursor and
the final durable `sync-once` cutpoint, together with the regression test. That
would allow scheduling-only movement after pass return to be mislabeled as the
same settled observation. Rev0954 restores the sealed parent predicate, comment,
structural check, and `scheduling-only remote cursor movement settled` runtime
case before layering the checkpoint work.

## Build-graph correction: sanitizer final-link closure

The first source-fresh Clang ASan/UBSan product build found another composition
defect that ordinary GCC could not expose. The new verification-index test
linked the instrumented `anonsync_sha256_digest` static library, but the test
executable had been added only to the product target—not to the inherited
explicit sanitizer compile and final-link inventories. Its link therefore
failed on unresolved ASan/UBSan runtime symbols.

Both the verification-index library and test are now in the sanitizer compile
inventory, and the test is independently present in the final-link inventory.
The structural audit parses those exact CMake regions rather than relying on a
weak whole-file occurrence count. This keeps the explicit split honest: every
executable consuming instrumented static dependencies must itself link the
sanitizer runtimes.

## Parser/refactor boundary

The v1 binary format lives in a small linked leaf with an independent compiled
test. The parser proves exact length before reserve, supported generation,
trailing SHA-256 checksum, sorted unique lowercase digest identities, private
metadata, entry/byte ceilings, and overflow-safe fixed-width arithmetic. Hostile
test records are resealed after mutation so checksum failure cannot conceal a
semantic parser defect.

A descriptor-snapshot helper centralizes conversion of POSIX `stat` observations
to the canonical eleven-field metadata projection used by marker, payload,
process-cache, and durable-checkpoint paths. The large payload-store owner composes
that leaf rather than embedding a second binary parser.

## Exact nonclaims

This durable payload verification checkpoint is restart acceleration and is
not permanent corruption detection. Ordinary writes invalidate mtime/ctime, but
silent storage corruption or a privileged/same-UID actor outside the cooperative
lease model may preserve or reconstruct metadata. The checksum is not a MAC.
`ReadOnlyInspect` remains the byte-cold forensic path, and a bounded durable
rotating scrub is still required to re-read every retained payload over time.
Optional Linux fs-verity may eventually help on qualified filesystems, but it is
not portable and changes deployment semantics.

A late entry-count-only scrub experiment was rejected during release audit.
Hashing one payload per pass is not a meaningful bound when one payload may be
multi-gigabyte, and a process-local cursor would repeat a prefix after restart.
No scrub configuration or claim from that branch is shipped. The future owner
must have both byte and entry budgets, a durable continuation/epoch, and explicit
quarantine or failure semantics.

The payload store remains append-only without coordinated version retention,
restore, reachability pins, quarantine, or garbage collection. Changed large
files remain whole-payload identities. The synchronized folder scan still pays
repeated metadata-prefix work despite its fair cursor. Rename, ordinary conflict
and recovery UX, selective sync, many-share device ownership, cross-platform
qualification, and the first named Resilio uninstall workload remain open.

## Validation

The configured product lane contains 36 tests; the sealed evidence must record
an exact 36/36 result from the final frozen source.

Fresh GCC 14.2 Debug completed all 515 configured build steps. All 255 registered tests passed across deterministic 60/60, 60/60, 60/60, 60/60, and 15/15 shards; the explicit product lane passed 36/36 in 51.88 seconds. Focused executables passed 92 network-model checks with 41 generated operations, 30 POSIX-resolution checks, 21 verification-index checks, 213 payload-store checks, 296 SQLite-owner checks, 347 folder-owner checks, and 110 sync-once checks. The structural audit passed 87/87. A fresh Clang 17 ASan/UBSan product graph completed all 226 configured steps from an empty build directory after one external interruption and same-directory resume; all 36 product tests passed serially with leak detection in 132.44 seconds, and the same focused suites passed without a sanitizer diagnostic.

## Package

Declared publication name: `AnonSync-rev0954-2026.07.30.21.54-durablecheckpoint-restartreuse-scrubboundary-garnet.zip`

Parent: `AnonSync-rev0953-2026.07.30.18.29-targetedpayload-terminalcursor-crossowner-smokyquartz.zip`

Parent SHA-256: `a217c34f34c69d9c78fa72a7307df1ad57d932cc21a49d563c30f93072248409`

See `DURABLE_PAYLOAD_VERIFICATION_CHECKPOINT_AUDIT_rev0954.md`,
`TERMINAL_CROSS_OWNER_SETTLEMENT_FENCE_AUDIT_rev0953.md`, and
`REVISION_EVIDENCE/rev0954/`.
