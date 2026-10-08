# AnonSync rev1020

AnonSync exists to **replace Resilio Sync with an open C++ implementation**.
Period. The product target is practical peer-to-peer folder synchronization:
continuous multi-device convergence, large-file transfer and resume, offline
recovery, selective synchronization, access control, discovery/connectivity,
service lifecycle, and usable diagnostics. Direct IP, Tor, and I2P are first-
class routes to the same authenticated peer and folder protocol.

This is a replacement-product goal, not a claim of proprietary Resilio wire
compatibility. A user should eventually be able to remove Resilio Sync, install
AnonSync, configure folders and peers, and retain the expected synchronization
workflow while gaining Tor and I2P operation. Exact-history, crash-consistency,
bounded-work, and capability rules are engineering discipline in service of that
product. They are not the mission.

The authoritative restart page is the release-root `BOOTSTRAPROSE.md`. This
hidden README preserves implementation history; it does not define another
product direction.



## Rev1020: content-indexed rename planning and streaming catalog proof

Rev1020 bounds the ordinary one-file planning path introduced by rev1019 for
large media trees and million-path namespaces. A newly observed file no longer
starts rename discovery by materializing the complete folder catalog and
restoring the complete retained replica model. The folder owner now combines
one targeted catalog path cutpoint, one bounded catalog content cutpoint, one
targeted replica path cutpoint, and one bounded current-visible content
cutpoint. Each exact-content query is forced through a startup-attested named
index and returns at most two rows, distinguishing absence, one exact active
File, and ambiguity.

The replica database advances from schema v8 to v9 and the folder catalog from
schema v6 to v7. Both exact migrations rebuild normalized file-content
projections inside the existing writer transaction, advance one generation,
and preserve causal evidence, lineage, selection policy, outbox state,
retention pins, and current values. A forged normalized row is re-bound to its
immutable operation or catalog value and fails closed. The catalog migration
also corrects an intermediate-schema defect found during the audit: v5-to-v6
now creates the exact released selective-sync v6 metadata surface before the
v6-to-v7 index migration.

Two-head displayed-candidate adoption remains available without restoring
unrelated history. The path-local cutpoint retains at most two exact active
conflict operations and reuses a requested operation already owned by that
view, avoiding a second decode and envelope copy. Duplicate current content or
multiple absent catalog candidates still falls back to ordinary create/delete;
content alone does not manufacture identity.

Catalog publication now recomputes canonical current and staged proofs as
ordered streams. Single-path and rename-pair commits retain only their exact
changed rows plus one streamed row at a time, removing O(path count) catalog
vectors. The global digest still costs O(N) SQLite I/O before and after a
catalog mutation. An actual identity-preserving rename also retains one
O(N-visible) streamed current-visible corruption fence before replica
publication, with memory bounded by one path's conflict width. Ordinary
one-file planning is therefore path/content-indexed and history-cold, while
publication still pays explicit global integrity I/O. This is O(1) row memory,
not a dense million-file throughput measurement.

The wire protocol, payload format, delta algorithm, selective-sync policy, and
causal rename shape are unchanged. Rev1020 remains regular-file work. Directory
and subtree moves, complete and empty-directory semantics, portable metadata,
conflict-copy UX, retention collection, quota/ENOSPC recovery, Android adapters,
and live public Tor/I2P qualification remain open.

### Rev1020 validation

Exact rev1020 source passed a fresh GCC 14.2 Debug graph (573/573 configured build edges), all 312/312 registered tests, and an independent 56/56 product replay. Focused GCC suites passed network model 104/104 with 41 generated operations, SQLite owner 433/433, folder owner 562/562, and sync-once 114/114. Source audits passed bounded rename 23/23, identity-preserving rename 31/31, selective sync 52/52, targeted local publication 30/30, SQLite owner 43/43, and structural authority 705/705. The exact Clang 17 ASan/UBSan product graph completed 284/284 edges and reached a no-work state; all 56/56 product tests passed with leak detection and halt-on-error. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev1019 parent SHA-256 matched 6598db7b72152953b02539f16338dbf04bea358b0318d26b5723bb641140829c and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 17/17 changed files. The active implementation projection contains 650 files / 29,625,955 bytes with SHA-256 3874720c5071b841920e6a3c3dadc71f8554c519a792b0eed89bebb78f4af833. Final wrapper-directory verification passed 32/32 checks, ZIP verification and CRC passed 41/41 checks, and clean extraction matched every path, byte, type, and mode.

Archive: `AnonSync-rev1020-2026.08.07.08.13-contentindex-streamingcatalog-boundedrename-variscite.zip`

Codename: `variscite`

See `BOUNDED_RENAME_CONTENT_INDEX_AND_STREAMING_CATALOG_AUDIT_rev1020.md` and
`REVISION_NOTES_rev1020.md`.


## Rev1019: conservative identity-preserving regular-file rename/move

Rev1019 returns product priority to ordinary file semantics. When one
materialized cataloged source File disappears and an exact-content destination
appears, the folder owner can publish one canonical causal continuation:
destination File followed immediately by source Tombstone under the same actor.
The replica pair commits in one `BEGIN IMMEDIATE` transaction and one state
generation; the catalog pair commits in one catalog transaction and one catalog
generation. The existing immutable payload object is reused. A direct exact-content one-path scan (including the rename and later
no-op path) reopens the selected digest through bounded targeted payload access,
so it does not reread a multi-terabyte descriptor merely to rediscover an already
retained object. The targeted owner and exact-inode lease remain live through
replica and catalog publication. This path does not claim complete payload-root
health or capacity authority; the ordinary convergence snapshot retains that
role.

The model reconstructs that identity after restart from ordinary operations.
There is no rename-only wire message, durable inode number, watcher cookie, or
process-local flag. Peers that already retain the exact digest can reuse the
payload through existing content-addressed and delta paths. The final SQLite
uniqueness pass also recomputes the complete current-visible projection witness
one bounded path at a time; a missing duplicate row therefore fails closed
instead of manufacturing rename uniqueness from damaged index state.

Identity is deliberately conservative. If two absent cataloged names share the
same exact content, or another same-content File remains visible anywhere,
rename planning stops before payload or replica effects and ordinary
create/delete convergence takes over. Exact-content copy plus deletion remains
observationally indistinguishable from a rename, so this is causal identity
continuity rather than proof of `rename(2)`.

Replica and catalog transactions are individually atomic but remain separate
databases. A regression deliberately stops after the replica pair and proves
that restart adopts the exact destination and source tombstone without minting
operations or duplicating payload bytes. The SQLite pair transaction itself is
history-cold: it reads the two path histories, bounded causal heads, and one
streaming current-visible uniqueness scan rather than reconstructing all retained
operations. Folder orchestration and model inference still reconstruct/scan
active evidence and catalog state, so this is not a million-file rename
throughput result. Directory/subtree moves, empty
directories, portable metadata, conflict UX, retention collection, ENOSPC,
Android adapters, and live Tor/I2P qualification remain open.

The release audit also found that the rev1018 wrapper's publication metadata was
not self-consistent under the current verifier. Rev1019 uses its physical hash
and Git-recorded source only as lineage, removes the generated bytecode cache,
and regenerates evidence, gate, manifest, and package verification rather than
borrowing the stale rev1017 release claim.

### Rev1019 validation

Exact rev1019 source passed a fresh GCC 14.2 Debug graph (573/573 configured build edges), all 311/311 registered tests, and an independent 56/56 product replay. Focused GCC proofs passed 104 network-model checks plus 41 generated operations, 416 SQLite-owner checks, 562 folder-owner checks, and 114 sync-once checks. The focused identity-preserving-rename source audit passed 31/31 checks and the structural authority audit passed 698/698 checks. An exact Clang 17 ASan/UBSan product graph reached a no-work state against the 284-edge configured product shape, and all 56/56 product tests passed with leak detection and halt-on-error. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev1018 parent SHA-256 matched 02fc26329d2274e6dbf440f3e9d4319a8af08efaa00bdfce8f61c8a59eddf90b; its stale rev1017 release metadata and generated Python cache are explicitly not borrowed as publication authority. The binary-aware source patch reconstructed all 19/19 changed active files. The final active implementation projection contains 649 files / 29,541,244 bytes with SHA-256 ef1df087c17ef62ee25466caeea2e4f105c8716aab3299553b391cc9bcefabf7. Final wrapper-directory verification, ZIP verification and CRC, canonical path/no-symlink policy, and clean-extraction path/byte/type/mode comparison all passed.

Archive: `AnonSync-rev1019-2026.08.07.06.02-causalrename-projectionreproof-singlepayload-bixbite.zip`

Codename: `bixbite`

See `IDENTITY_PRESERVING_REGULAR_FILE_RENAME_AUDIT_rev1019.md` and
`REVISION_NOTES_rev1019.md`.


## Rev1018: history-cold service startup and a real sparse >4 TiB memory gate

Rev1018 combines one startup refactor with the measurement it made useful.
`SyncReplicaDeliveryService`, `SyncReplicaReconciliationService`, and
`SyncReplicaFileDeliveryService` no longer reconstruct complete retained
replica or file-effect history after their durable owners have already
performed the required cold proof. They compose from transaction-pinned bounded
identity and policy cutpoints. One exact 24-column file-effect metadata decoder
feeds both the bounded cutpoint and the complete snapshot, so the optimization
does not create a second schema interpretation.

The product-labelled constructor regression binds an exact logical 4 TiB
history shape: 64 files at 64 GiB each. SQLite authorizer fences prove complete
replica and effect snapshots would fail, while all three service constructors
succeed under the same fences and perform zero allocations at or above 64 KiB.
The durable reference owners remain O(history) and still perform one complete
cold reconstruction.

Rev1018 then starts two real `anonsync_sync run` services over independent
selective-sync shares. Each share contains 4,097 sparse 512 MiB regular files,
for 2,199,560,126,464 logical bytes per share and exactly
4,399,120,252,928 aggregate logical bytes. A default metadata-only policy plus
one deeper materialization rule forces every root file to be classified without
opening selected payload work. The exact diagnostic pass reports 4,097
metadata-only files per share, zero selected/payload-mutation bytes, two
directory enumeration passes, and a 4,096-name maximum component batch.

A 24-point owner-only `resources-watch` series samples both services every
75 ms. The focused GCC run observed 16,280 KiB aggregate peak sampled PSS and
60,796 KiB summed Linux lifetime peak RSS, beneath release tripwires of 1 GiB
and 1.5 GiB respectively. Final release evidence records the clean authoritative
rerun. The resource surface remains diagnostic-only: sampled PSS can miss
between-point transients, and kernel peak RSS does not attribute allocator
fragmentation or cgroup pressure.

The new `metadata_only_regular_file_logical_bytes` field is checked `st_size`
accounting from the same no-follow observation that classified each excluded
regular file. It is sparse logical extent, not allocated blocks, retained
payload bytes, or bytes hashed. Descendants of a pruned metadata-only directory
are deliberately absent. Folder-pass diagnostics copy the existing traversal's
enumeration and component-batch evidence without another walk.

This is not a dense-media throughput result, a million-file proof, or Android
support. It does not complete placeholders, automatic eviction, retention
collection, quota/ENOSPC recovery, live public Tor/I2P qualification, or all
portable metadata. Delta synchronization remains mandatory and the retained
content-defined path supplies bounded same-path and current-visible cross-file
reuse, but this sparse gate does not qualify dense transfer speed.

The next product edge returns to file semantics: identity-preserving
rename/move, then complete directories and empty directories, understandable
conflict handling, and controlled ENOSPC. Dense multi-terabyte and million-file
scale tests should grow alongside those semantics rather than replacing them.
Android remains a worthy direction, but needs explicit scoped-storage,
lifecycle, notification, battery, and permission adapters rather than a false
claim that the Linux daemon contract already transfers unchanged.

See `HISTORY_COLD_PEER_SERVICE_STARTUP_AUDIT_rev1018.md`,
`SPARSE_MULTITERABYTE_SELECTIVE_MEMORY_AUDIT_rev1018.md`, and
`REVISION_NOTES_rev1018.md`.

### Rev1018 validation

Exact rev1018 source passed a fresh GCC 14.2 Debug graph (578/578 configured build edges), all 310/310 registered tests, and an independent 56/56 product replay. Focused GCC proofs passed 22 history-cold source-frame/startup checks, 26 real sparse multi-terabyte process checks, 90/90 folder-observer checks, 6/6 observer-race checks, and 557 folder-owner checks. Source audits passed 19/19 history-cold startup checks, 18/18 sparse multi-terabyte checks, and 690/690 structural authority checks. A fresh Clang 17 ASan/UBSan product graph completed 286/286 edges and all 56/56 product tests passed with leak detection and halt-on-error. The exact rev1017 parent SHA-256 matched and passed 41/41 wrapper-aware package checks. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The obsolete predictable-path validator, its kill guard, interrupted caches, and divergent branches are excluded.

Archive: `AnonSync-rev1018-2026.08.07.02.31-historycold-sparsefourterabyte-memoryproof-danburite.zip`

Codename: `danburite`


## Rev1017: bounded Linux resource series and sampled peak envelopes

Rev1017 composes rev1016's explicit owner-only `resources\n` observation into
one bounded operator time series. The shipping command accepts one through 256
share sockets, two through 1,024 sample rounds, a fixed one-millisecond through
one-hour interval, and one total deadline of at most 24 hours:

```text
anonsync_sync resources-watch \
  --socket /run/user/$UID/anonsync/share-a.status.sock \
  --socket /run/user/$UID/anonsync/share-b.status.sock \
  --samples 120 --interval-milliseconds 1000 \
  --timeout-milliseconds 180000
```

The `anonsync.local-process-resources.series.v1` result retains one compact
aggregate point per round and one first/last/peak envelope per process. It does
not retain the process-by-sample matrix, so the command's retained shape is
O(processes + samples), not O(processes × samples). Every later observation
must match the first round's peer-bound PID and process start ticks; restart,
socket replacement, or alias drift fails closed. The schedule is anchored to
command start, and one steady-clock deadline governs all waits and socket
requests.

A real-process regression triggers another touched 48 MiB reservation during a
16-point series and requires at least a 40 MiB observed rise in anonymous PSS
and private resident memory. It also proves compact points, fixed scheduling,
per-process envelopes, cumulative usage deltas, same-process alias rejection,
changed-process rejection, impossible-schedule preflight, one total deadline,
and ordinary-status isolation.

The adjacent refactor centralizes one-shot and series socket selection, checked
resource arithmetic, identity proof, round sampling, and deadline handling. The
fixture now validates page size before `mmap`, closing a constructor exception
window before RAII ownership exists.

This is diagnostic evidence, not a resource governor or a multi-terabyte result.
Samples remain sequential and non-atomic, and a transient between points can be
missed. Rev1017 does not attribute page cache, expose allocator fragmentation,
measure cgroup pressure, consolidate shares, prove Android, or change sync,
selective-sync, retention, Tor, I2P, readiness, or filesystem authority. The
next useful cloudtainer step is to apply this series to multiple real share
services over sparse multi-terabyte fixtures; then return product priority to
rename/move, complete directories, human conflicts, selective-sync surfaces,
and ENOSPC behavior.

See `LINUX_PROCESS_RESOURCE_SERIES_AND_PEAK_ENVELOPE_AUDIT_rev1017.md` and
`REVISION_NOTES_rev1017.md`.


## Rev1016: explicit Linux process resources and bounded multi-share aggregate

Rev1016 follows the rev1015 whole-process memory handoff instead of adding
another source-manifest representation. Every retained Linux share process now
answers one explicit owner-only local request, `resources\n`, with a strict
`anonsync.local-process-resources.response.v1` snapshot. Ordinary `status\n`
remains a read of already-rendered service state and performs no procfs
traversal.

The observer uses one bounded read of `/proc/self/smaps_rollup`, the Linux
interface that pre-sums mapping memory and exposes `Pss_Anon`, `Pss_File`, and
`Pss_Shmem`. It also reads the current process's `/proc/self/stat` start time,
counts numeric descriptor and task entries, and obtains peak RSS, page faults,
block-I/O operations, and context switches from `getrusage(RUSAGE_SELF)`. The
parser requires one canonical occurrence of every consumed memory field and
rejects missing, duplicate, wrong-unit, noncanonical, overflowed, or over-frontier
input.

The shipping aggregate command is:

```text
anonsync_sync resources \
  --socket /run/user/$UID/anonsync/share-a.status.sock \
  --socket /run/user/$UID/anonsync/share-b.status.sock \
  --timeout-milliseconds 5000
```

It accepts one through 256 distinct private sockets and emits
`anonsync.local-process-resources.aggregate.v1`. Socket responses remain bound
to `SO_PEERCRED`; the aggregate additionally combines PID with process start
time and refuses two aliases for the same live process. RSS, PSS,
anonymous/file/shared-memory PSS, private resident memory, swap PSS, peak RSS,
descriptors, and threads use checked sums.

One steady-clock deadline governs the complete request. The timeout is not
multiplied by the number of sockets. Output explicitly states that RSS sums
double-count shared pages, PSS uses the kernel's proportional share adjustment,
and process samples are sequential rather than one atomic global cutpoint. The
surface is diagnostic-only and does not change readiness, scheduling,
retention, transfer budgets, or filesystem authority.

A real-process regression starts two independent service fixtures, touches 48
MiB of private anonymous memory in one, and proves at least a 40 MiB
`Pss_Anon`/private-resident separation, exact aggregate equality, same-process
alias rejection, ordinary-status isolation, and clean socket drain. This is an
observer proof, not a claim that a multi-terabyte media workload now fits a
particular memory budget.

Rev1016 still does not attribute page cache, expose malloc arena fragmentation,
measure cgroup pressure, consolidate shares into one daemon, or prove Android
support. The next useful experiment is multiple real `anonsync_sync run`
services over sparse large-file trees through startup, manifest construction,
restart replay, delta reuse, full scans, selective hydration, high-latency
routes, and controlled ENOSPC. If that process boundary is acceptable, product
priority returns to identity-preserving rename/move, complete directories,
human conflict handling, and selective-sync user surfaces.

See `LINUX_PROCESS_RESOURCE_SNAPSHOT_AND_MULTISHARE_AGGREGATE_AUDIT_rev1016.md`
and `REVISION_NOTES_rev1016.md`.

### Rev1016 validation

Exact rev1016 source passed a fresh GCC 14.2 Debug graph (573/573 configured build edges), a no-work bundled-SQLite re-attestation, independent 55/55 product tests, and 252/252 non-product tests for all 307/307 registered tests. Focused GCC proofs passed 45 Linux process-resource, 165 local private-socket, and 42 real-process aggregate checks. Source audits passed 22/22 focused resource-boundary checks and 667/667 structural-authority checks. A fresh Clang 17 ASan/UBSan product graph completed 284/284 edges and all 55/55 product tests passed with leak detection and halt-on-error. The exact rev1015 parent passed 41/41 wrapper-aware package checks. Aggregate terminal-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. Predictable-path validators, the post-freeze divergent source delta, interrupted runs, and their build products are excluded.

Archive: `AnonSync-rev1016-2026.08.06.22.55-processresources-pssaggregate-deadlinefence-clinohumite.zip`

Codename: `clinohumite`


## Rev1015: fixed active-source digests and linear multi-share record memory

Rev1015 completes the fixed-digest source-manifest conversion at the last
in-progress owner. `SyncReplicaFilePayloadStoreContentDefinedChunk` no longer
retains one 64-character `std::string` per completed chunk. It is now one exact
40-byte extent-plus-`Sha256DigestValue` record, matching the fixed binary digest
used by the durable checkpoint and generation-9 manifest owners.

At the 8,192-chunk maximum, one active projection now retains one 327,680-byte
vector allocation. The prior GCC/libstdc++ shape requested 860,160 bytes through
8,193 allocations: the same vector plus 532,480 bytes across 8,192 digest
strings. Active restart restore, checkpoint publication, completed projection,
protocol construction, and compact-cache construction now copy the fixed value
directly without text round trips.

The adjacent refactor adds an allocation-free 32-byte terminal form to
`ResumableSha256`. Chunk completion no longer creates a temporary 64-character
hexadecimal string and parses it back into binary. Fixed hexadecimal arrays and
the owning string convenience API derive from the same binary terminal path.

Checkpoint publication now mutates the caller-owned bounded candidate in
place. Typed lease or atomic-publication deferral retains that same candidate
for a later owner turn instead of copying the maximum 8,192-record sequence.
Publication still advances only after exact committed-record, lease, and rooted
reproof.

The one completed compact source manifest is now an active-transfer cache. A
terminal generation-9 frame releases it only after frame assembly, source
descriptor release, and exact complete-checkpoint publication, with operation
id, canonical path, content digest, extent, and manifest digest all matching.
A duplicate request after a lost response rehydrates the exact checkpoint
without another source-manifest scan or source-byte hash.

A focused allocator oracle proves binary completion and post-reserve fixed-record
construction perform zero allocations. It then retains 64 maximum synthetic
active-source vectors through exactly 64 large allocations and exactly 20 MiB
of record storage. The equivalent prior requested shape was 52.5 MiB, a 32.5
MiB reduction and 524,288 fewer per-digest heap owners at that synthetic
frontier. This is not a whole-daemon RSS result.

Protocol generation remains 9 and checkpoint format remains v2. Network and
durable bytes, chunk boundaries, semantic manifest digests, structural digests,
and publication rules are unchanged. One active source still retains one
327,680-byte O(chunk count) vector, and whole-process RSS, SQLite/page cache,
TLS, payload indexes, directory scans, fragmentation, route latency, checkpoint
write amplification, and ENOSPC remain measurement gates.

See `ACTIVE_SOURCE_MANIFEST_FIXED_DIGEST_AND_MULTISHARE_MEMORY_AUDIT_rev1015.md`,
`TERMINAL_SOURCE_MANIFEST_CACHE_RELEASE_AUDIT_rev1015.md`, and
`REVISION_NOTES_rev1015.md`.

### Rev1015 validation

Exact rev1015 source passed a fresh GCC 14.2 Debug graph (567/567 configured build
edges), a no-work bundled-SQLite re-attestation, independent 53/53 product tests, and
final 251/251 non-product accounting for all 304/304 registered tests. Focused GCC
proofs passed 86 resumable-SHA-256, 737 payload-store, 30 source-manifest-checkpoint, 35
compact-manifest, 16 source-frame-memory, and 215 reconciliation-service checks. Source
audits passed 19/19 active-source-memory, 22/22 terminal-cache, 22/22 checkpoint-memory,
and 659/659 structural-authority checks. A fresh Clang 17 ASan/UBSan product graph
completed 278/278 edges and all 53/53 product tests passed with leak detection and
halt-on-error. The exact rev1014 parent passed 41/41 wrapper-aware package checks.
Aggregate terminal-log inspection found no compiler, linker, AddressSanitizer,
UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic.

Archive: `AnonSync-rev1015-2026.08.06.20.55-activefixeddigest-terminalrelease-multishare-kornerupine.zip`

Codename: `kornerupine`


## Rev1014: borrowed compact manifest and single-allocation direct framing

Rev1014 removes the final publication-only copy of a completed content-defined
source manifest. The cache-cold shipping path lends its exact retained
cumulative 40-byte-record sequence directly to the canonical generation-9
response-frame assembler; it no longer allocates a second 327,680-byte manifest
vector merely to serialize the first range.

At the hard 4 TiB / 8,192-chunk shape, an allocator probe observes exactly one
large allocation on the borrowed path—the final roughly 640 KiB response frame.
The owning compatibility baseline performs two and requests exactly 327,680
more bytes. Both paths emit byte-identical generation-9 frames. The shipping
service regression independently proves one borrowed manifest, zero
materialization bytes, no complete manifest owner in direct metadata, exact
frame decoding, and ordinary receiver application.

Validation, semantic digesting, body sizing, serialization, final response
validation, and request-bound first-range placement now share one private
read-only manifest view. Ordinary protocol paths supply an owning size-based
view; direct assembly may supply a borrowed cumulative view. The assembler
rejects double ownership, changed extents, noncanonical parameters, malformed
cumulative sequences, digest disagreement, and illegal first-range placement.
The borrow carries no durable or wire authority and must outlive only the
synchronous assembly call.

The protocol remains generation 9 and network bytes do not change. The ordinary
direct-assembly overload now uses an allocation-cold empty borrowed sidecar
instead of allocating one absent optional per payload; a runtime differential
proves exact wire equality and the eliminated allocation. The shipping service
re-proves expected borrowed count/chunk telemetry and rejects any retained
owning manifest. The legacy compatibility service still decodes the final frame
when an owning response is required. The shipping TLS path keeps bounded
metadata and one final frame.

This is not constant-memory multi-terabyte synchronization. One active source
still retains one 327,680-byte O(chunk count) sequence; a cold 4 TiB source still
requires 131,072 local 32 MiB hash pulses and may replay one 1 GiB checkpoint
interval. Whole-process multi-share RSS, page cache, complete scans, route
latency, disk amplification, and ENOSPC remain measurement gates. There is no
global chunk index, and rename/move identity, complete directory semantics,
conflicts, placeholders, automatic selective-sync eviction, retention
collection, Android, and live public Tor/I2P qualification remain incomplete.
See `BORROWED_COMPACT_MANIFEST_DIRECT_FRAME_AUDIT_rev1014.md` and
`REVISION_NOTES_rev1014.md`.

### Rev1014 validation

Exact rev1014 source passed a fresh GCC 14.2 Debug graph (567/567 configured build edges), a no-work bundled-SQLite re-attestation, independent 53/53 product accounting, and final 249/249 non-product accounting for all 302/302 registered tests. Focused GCC proofs passed 35 compact-manifest, 5,004 protocol, 25 memory-shape, 10 source-frame-memory, 30 checkpoint-codec, and 45 content-defined-chunker checks. A fresh Clang 17 ASan/UBSan product graph completed 278/278 edges; all 53/53 product tests and focused 35 compact, 5,004 protocol, and 10 source-frame checks passed with leak detection and halt-on-error. Source audits passed 32/32 borrowed-manifest, 30/30 fixed-binary, 29/29 compact-cache, 34/34 inherited direct-source, and 646/646 structural-authority checks. The exact rev1013 parent passed 41/41 wrapper-aware package checks. Aggregate terminal-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. Final staged-directory verification passed 32/32 checks; ZIP verification and CRC passed 41/41 checks; clean extraction matched every path, byte, type, and POSIX mode.

Archive: `AnonSync-rev1014-2026.08.06.18.37-borrowedmanifest-directframe-singleallocation-wulfenite.zip`

Codename: `wulfenite`


## Rev1013: fixed-binary source manifests and one shared digest codec

Rev1013 removes the remaining per-chunk heap ownership from cache-cold
source-manifest receive, copy, and publication. The generation-9 protocol
chunk, compact completed cache, and durable checkpoint now share one strict
`Sha256DigestValue`: exactly 32 bytes, standard-layout, trivially copyable, and
without `std::string`, pointer, allocator, or hidden heap state. Each manifest
chunk remains one contiguous 40-byte extent-plus-digest record.

At the 8,192-chunk frontier, rev1012 cache-cold wire materialization required
one 327,680-byte vector allocation plus 8,192 independent 65-byte digest-string
allocations: 8,193 allocations / 860,160 requested bytes. Rev1013 requires one
327,680-byte vector allocation. It removes 8,192 allocator calls and 532,480
requested bytes from that boundary. Parser-shaped receive construction,
compact-cache construction, compact-cache copy, and compact-to-wire
materialization each have one exact vector allocation; numeric cumulative lookup
remains allocation-cold. These are allocator-request measurements, not a claim
about whole-process RSS or allocator fragmentation.

The representation change does not change the network or durable formats. The
protocol remains generation 9 and emits the same 64 lowercase hexadecimal
characters per digest. Exact sealed-rev1012 request and response frame hashes
are retained as golden fixtures. The source-manifest checkpoint remains v2 and
reproduces the exact sealed-rev1010 active, complete, and maximum images.
Malformed digest text is rejected while constructing or assigning the fixed
value, and failed assignment leaves the previous value unchanged.

The adjacent refactor removes separate digest text/binary codecs from the
compact cache and checkpoint. Source-manifest protocol, cache, and restart state
now cross one canonical conversion boundary rather than three implementations
that could drift in syntax, diagnostics, or serialization.

This remains O(chunk count), not constant-memory multi-terabyte
synchronization. One maximum sequence is 327,680 bytes; a cold 4 TiB source
still requires 131,072 local 32 MiB hash pulses and a successful checkpoint may
replay one 1 GiB interval. Whole-process RSS, page-cache pressure, allocator
fragmentation, concurrent shares, complete scans, route latency, disk
amplification, and ENOSPC remain measurement gates. There is no global,
multi-file, or multi-share chunk database. Rename/move identity, complete
directory semantics, conflicts, placeholders, automatic selective-sync
eviction, best-effort retention collection, Android, and live public Tor/I2P
qualification remain incomplete. See
`FIXED_BINARY_WIRE_MANIFEST_AND_SHARED_DIGEST_CODEC_AUDIT_rev1013.md` and
`REVISION_NOTES_rev1013.md`.

### Rev1013 validation

Exact rev1013 source passed a fresh GCC 14.2 Debug graph (567/567 configured build edges across bounded resumptions) and a no-work bundled-SQLite re-attestation; all 301/301 registered tests and an independent 53/53 product accounting passed. Focused GCC proofs passed 22 compact-manifest, 30 checkpoint-codec, 45 content-defined-chunker, 43 true-process restart, 5,004 reconciliation-protocol, 25 memory-shape, 10 source-frame-memory, 20 terminal-state, 737 payload-store, 397 SQLite-owner, 536 folder-owner, 114 sync-once, 2,047 TLS, and 211 reconciliation-service checks. A fresh Clang 17 ASan/UBSan product graph completed 278/278 edges and all 53/53 product tests passed with leak detection and halt-on-error; the additional payload-store sanitizer proof passed 737 checks. Source audits passed 30/30 fixed-binary-manifest, 29/29 compact-cache, 22/22 checkpoint-memory, 27/27 manifest-reference, and 635/635 structural-authority checks; the exact rev1012 parent passed 41/41 wrapper-aware package checks. Aggregate terminal-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The overwritten first authority, divergent controller branches, discarded caches, interrupted early registry, and pre-correction lexical-audit failure are excluded.

Archive: `AnonSync-rev1013-2026.08.06.16.45-fixedbinarymanifest-sharedcodec-singleallocation-scheelite.zip`

Codename: `scheelite`


## Rev1012: compact completed source-manifest cache

Rev1012 removes the string-backed generation-9 manifest and separate cumulative
offset vector from the one completed source manifest retained by the shipping
reconciliation service. One fixed 40-byte record now carries both the exclusive
cumulative chunk end and the binary SHA-256 value.

At the 8,192-chunk frontier, the focused allocation probe measures the rev1011
manifest-plus-offset shape at 8,194 allocations / 925,704 requested bytes. The
rev1012 cache requires one 327,680-byte vector allocation, removing 8,193
allocator requests and 598,024 requested bytes from resident acceleration.
These are allocator measurements, not a whole-process RSS claim.

Generation 9 remains unchanged. A cache-cold first range materializes the exact
string-backed protocol manifest and moves it into the response; later ranges
and continuation requests retain only the existing manifest digest. Maximum
wire materialization remains 8,193 allocations / 860,160 requested bytes, but
it is transient rather than process-retained. Fresh projection and durable
checkpoint restoration both validate the canonical manifest and preserve the
existing digest, extent, parameter, inode, lease, and rooted-source reproofs.

The allocation audit also moved successful content-defined parameter diagnostic
construction onto error paths. Valid parameter checks no longer allocate one
long label string.
Numeric cumulative lookup also reuses the service owner's retained label instead
of constructing a diagnostic string for every range. The maximum 8,192-chunk
numeric lookup sweep performs zero allocations.

The cache remains one O(chunk count), one-source acceleration. Cold 4 TiB
hashing still requires 131,072 32 MiB pulses, restart may replay one 1 GiB
interval, and sparse multi-terabyte whole-process RSS, page-cache, throughput,
route-latency, and ENOSPC measurement remains open. This revision does not add a
global chunk index or solve rename/move identity, complete directories,
conflicts, placeholders, automatic eviction, Android, retention collection, or
live public Tor/I2P qualification. See
`COMPACT_SOURCE_MANIFEST_CACHE_AND_CUMULATIVE_INDEX_AUDIT_rev1012.md` and
`REVISION_NOTES_rev1012.md`.

### Rev1012 validation

Exact rev1012 source passed a fresh GCC 14.2 Debug graph (567/567 configured build edges) and no-work bundled-SQLite re-attestation; all 300/300 registered tests and an independent 53/53 product replay passed. Focused GCC proofs passed 20 compact-manifest, 30 checkpoint-codec, 45 content-defined-chunker, 43 true-process restart, 5,001 reconciliation-protocol, 25 memory-shape, 20 terminal-state, 737 payload-store, 397 SQLite-owner, 536 folder-owner, 114 sync-once, 2,047 TLS, and 211 reconciliation-service checks. A fresh Clang 17 ASan/UBSan product graph completed 278/278 edges and all 53/53 product tests passed serially with leak detection and halt-on-error. Source audits passed 29/29 compact-cache, 36/36 retained-checkpoint, and 625/625 structural-authority checks; the exact rev1011 parent passed 41/41 wrapper-aware package checks. Aggregate terminal-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. Superseded pre-hotfix builds, the interrupted early registry, and pre-correction lexical-audit failures are excluded.

Archive: `AnonSync-rev1012-2026.08.06.14.42-compactmanifest-cumulativeindex-wirematerialization-dumortierite.zip`

Codename: `dumortierite`


## Rev1011: fixed-width restart-checkpoint digests

Rev1011 removes the per-chunk heap allocation from rev1010's bounded durable
source-manifest checkpoint. Each checkpoint chunk now retains one 64-bit extent
and one fixed 32-byte SHA-256 array instead of a 64-character `std::string`.
The record remains 40 bytes in the retained Linux ABI, but its digest no longer
owns a separate allocation.

A sealed-rev1010 allocation probe measured 8,192 allocations and 532,480
requested bytes to construct a maximum chunk vector after `reserve()`, and
8,193 allocations / 860,160 requested bytes to copy it. Rev1011 performs zero
post-reserve allocations for construction and one 327,680-byte allocation for
the copy. These are allocator-request measurements, not whole-process RSS.

The checksum-framed v2 wire format is unchanged. Active, complete, and maximum
fixtures reproduce the exact sealed-rev1010 byte lengths and SHA-256 values.
Parsing and serialization use the fixed binary arrays directly. Hex strings are
created only when checkpoint state crosses back into the ordinary reconciliation
manifest or projection. The fresh-completion bridge still moves its existing
hex string into the protocol manifest after constructing the compact checkpoint;
it does not introduce an 8,192-string copy.

This refactor does not reduce the cold 4 TiB hash work, ordinary completed
manifest strings, offset index, or page-cache cost, and it does not create a
global chunk index. Sparse multi-terabyte RSS and I/O measurement remains the
next source-scale gate. See
`SOURCE_MANIFEST_CHECKPOINT_HEAP_COMPACTION_AUDIT_rev1011.md` and
`REVISION_NOTES_rev1011.md`.

### Rev1011 validation

Fresh GCC 14.2 Debug graph 563/563; GCC registry 298/298; GCC product 52/52; focused 30 checkpoint-codec, 45 chunker, 43 true-process restart, 5,001 protocol, 25 memory-shape, 20 terminal-state, 737 payload-store, 397 SQLite-owner, 536 folder-owner, 114 sync-once, 2,047 TLS, and 211 reconciliation-service checks; fresh Clang 17 ASan/UBSan product graph 274/274 and product 52/52 with leak detection and halt-on-error; dedicated heap-compaction audit 22/22, retained rev1010 checkpoint audit 36/36, structural authority audit 617/617, and exact rev1010 parent verification 41/41. Incremental, remount-lost, stale-validator, and transient aggregate TLS-EOF attempts are excluded.

Archive: `AnonSync-rev1011-2026.08.06.10.19-fixedwidthdigest-singleallocation-wirecompat-axinite.zip`

Codename: `axinite`


## Rev1010: durable source-manifest restart continuation

Rev1010 removes the whole-payload restart penalty from the one source-side
content-defined manifest already selected by the retained reconciliation owner.
The payload store now owns one checksum-framed acceleration record bound to the
exact store identity, causal operation and canonical path, immutable payload
digest and extent, POSIX inode observation, chunking parameters, arbitrary-byte
frontier, resumable whole/current-chunk SHA-256 states, rolling chunker state,
completed chunk records, and—after completion—the canonical manifest digest.

The record is bounded to **8,192 chunks** and less than **384 KiB**. It is
payload-extent independent but remains O(chunk count), not constant-size. It is
excluded from payload inventory and grants no replica, causal, payload-byte, or
transfer authority. Invalid, stale, missing, changed-inode, or unsupported state
is discarded as acceleration and ordinary exact source hashing remains
available.

A fresh service explicitly discovers at most that one record, performs a
targeted SQLite lookup of the exact operation/path, targeted-opens and re-proves
the digest-named payload, and only then restores the hash/chunker frontier. The
filesystem-cold status accessor remains effect-free. The shipping single-owner
scheduler performs the discovery before selecting source-local work, so restart
recovery does not wait for another peer request.

The existing **32 MiB** fairness pulse is unchanged. Publishing after every
pulse would impose 131,072 atomic file-sync/rename/directory-sync sequences for
a 4 TiB source, so the first active pulse publishes immediately, later active
records advance every **1 GiB**, and completion always publishes. Once a
checkpoint succeeds, ordinary crash replay is less than one 1 GiB interval
rather than the whole payload. The total cold-source hash cost is still 131,072
pulses, and the completed manifest plus offset index remains O(chunk count)
process memory.

A true self-exec regression uses three fresh process images: one writes a 1 MiB
interior checkpoint, a second resumes only the remaining 9 MiB without a peer,
and a third serves from the complete checkpoint with zero source hashing. A
separate `RLIMIT_FSIZE` fault rejects the final atomic write, proves the prior
active record is unchanged, and requires peer-free owner discovery to seal the
retained completion before a fresh service reuses it with zero hashing. The
codec, chunker, payload-store, reconciliation, scheduler, and structural audits
bind the same path.

The user-visible rev1009 handoff was not materialized in this cloudtainer. The
exact sealed source parent is rev1008; rev1010 does not fabricate an unavailable
rev1009 source delta. See
`DURABLE_SOURCE_MANIFEST_RESTART_CHECKPOINT_AUDIT_rev1010.md` and
`REVISION_NOTES_rev1010.md`.

### Rev1010 validation

Exact final source passed a fresh GCC 14.2 Debug graph (563/563 build edges), the complete 297/297 registry, and an independent 52/52 product replay. Focused GCC proofs passed 20 checkpoint-codec, 45 content-defined-chunker, 43 true-process restart, 5,001 reconciliation-protocol, 25 response-memory, 20 terminal-state, 737 payload-store, 397 SQLite-owner, 536 folder-owner, 114 sync-once, 2,047 TLS-transport, and 211 reconciliation-service checks. A fresh Clang 17 ASan/UBSan product graph completed 274/274 edges; the exact source rebuilt and reached a no-work state, and all 52/52 product tests passed with leak detection and halt-on-error. No compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic remained. The dedicated checkpoint audit passed 36/36 and the structural authority audit passed 610/610. The exact rev1008 parent SHA-256 matched and its wrapper-aware package verifier passed 41/41. A stale-validator guard that had been pointed at the authoritative build paths was disabled; every interrupted result it caused is excluded from this release evidence.

Archive: `AnonSync-rev1010-2026.08.06.08.49-pulsecheckpoint-execrestart-retryfence-eucryptite.zip`

Codename: `eucryptite`


## Rev1008: source-local manifest completion and shared owner fairness

Rev1008 removes the remaining requester-turn dependency after one authenticated
request discovers a large source manifest obligation. The retained linked-peer
daemon can exact-open the same digest-named payload and advance the existing
content-defined projection through bounded **32 MiB** owner-local pulses with no
peer connected.

Network and local paths share one projection helper. Every pulse re-proves the
exact causal operation, content digest, extent, chunking parameters, and POSIX
inode observation. A missing payload clears stale acceleration. Completion
reuses the existing canonical manifest digest, chunk-offset index, and ranged
response path; it changes no replica, folder catalog, payload object, or request
cursor.

Source-manifest preparation and receiver terminal verification now share one
single-threaded local-payload scheduler. Before either pulse enters payload
authority it publishes one ordinary-turn obligation. The next owner call is
reserved for control, ingress, network, watcher, or repair observation, and
priority alternates when both local lanes are pending. No worker thread, second
event loop, or second content engine was added.

Live and terminal reporting advances to
`anonsync.peer-service.status.v26`. It exposes the exact source frontier and
scheduler steps, progress, completion, missing-payload, restart, hashed-byte,
and ordinary-turn-yield counters. The real process oracle proves one request
discovers a 64 MiB-plus-4,097-byte obligation, exactly two local pulses finish
it in the same ready PID, and a fresh requester reuses the completed manifest
without another preparing response.

The scale limitation remains explicit. A cold 4 TiB source still costs 131,072
32 MiB pulses; restart repeats unfinished work; and the completed manifest plus
offset index remains O(chunk count) memory. Rev1008 removes network-turn
coupling, not multi-terabyte disk or RSS cost. Sparse synthetic measurement is
the next source-scale gate before introducing a durable or paged chunk index.
See `SOURCE_LOCAL_MANIFEST_SCHEDULER_AND_OWNER_FAIRNESS_AUDIT_rev1008.md` and
`REVISION_NOTES_rev1008.md`.

### Rev1008 validation

`Fresh GCC 14.2 Debug graph 557/557; GCC registry 294/294; GCC product 50/50; focused 5,001 protocol, 25 memory-shape, 211 reconciliation-service, 2,047 TLS, 114 sync-once, 737 payload-store, 536 folder-owner, 397 SQLite-owner, and 20 terminal-state checks, plus the shipping source-scheduler process oracle; fresh Clang 17 ASan/UBSan product graph 268/268 and product 50/50 with leak detection and halt-on-error; focused source-local scheduler audit 35/35 and structural authority audit 602/602.`

Archive: `AnonSync-rev1008-2026.08.06.02.39-sourcelocalscheduler-turnfairness-peerindependent-tsavorite.zip`

Codename: `tsavorite`


## Rev1007: bounded source projection and same-stream preparation turns

Rev1007 bounds the last whole-source operation in the shipping delta path. A
large source payload no longer constructs its complete content-defined manifest
inside one authenticated request. The retained reconciliation service advances
at most **32 MiB** of exact source bytes per request and can resume the same
process-local projection from a fresh authenticated serve session.

The projection binds the exact digest, extent, content-defined parameters, POSIX
inode observation, resumable hash/chunker state, and bounded 8,192-chunk
frontier. Every step targeted-opens and re-proves the digest-named payload. The
source descriptor is gone before TLS backpressure. Completion reuses the
existing canonical manifest digest, offset index, and grouped range-framing
path; no second delta representation was added.

Reconciliation advances to **generation 9**. The new
`SourcePayloadPreparing` response keeps the exact blocked operation outstanding,
carries no payload continuation or source range, and permits only an earlier
canonical evidence prefix. TLS, session supervision, `sync once`, and shipping
CLI switches preserve the typed bounded-progress state.

The first process replay exposed a liveness defect in the initial shape: every
preparing frame immediately discarded TLS, so a one-shot source process could
lose its process-local projection before any range became transferable. The
retained TLS loop now collapses consecutive preparation turns on the **same
authenticated stream** while its existing round-trip budget remains. A resumed
payload keeps its exact durable offset; an initial page retry does not invent
source-digest continuation authority. Requester and source JSON both expose the
number of preparation responses.

The adjacent audit also removed duplicate TLS response accounting and corrected
a historical source-index oracle that still assumed a session-owned cache.
Exact digest, extent, chunking, or inode drift clears the completed cache and
starts one cohesive projection; unrelated operation-set progress need not throw
away valid content-based acceleration.

Focused tests prove a 3 MiB-plus-173-byte source resumes through three distinct
1 MiB preparing sessions and completes with an exact 173-byte tail in a fourth
session. A TLS test proves two 512 KiB preparation turns followed by one bounded
range window on the same authenticated stream. The shipping process oracle
proves a 64 MiB-plus-4,096-byte source makes wire progress after two production
32 MiB preparation turns instead of restarting its one-shot process forever.

This remains a bounded liveness correction, not complete multi-terabyte
efficiency. The default 64-turn stream can hash at most 2 GiB; the 4,096-turn
hard ceiling can hash at most 128 GiB. A persistent peer service can resume the
process-local projection across later streams, but restart repeats unfinished
source work. A 4 TiB source still needs 131,072 pulses. The next source-scale
edge is a bounded source-local scheduler or conservative durable source/chunk
index, selected through sparse multi-terabyte measurement. Rename/move identity,
complete directories, Android, selective placeholders and eviction, ENOSPC
qualification, retention collection, and public Tor/I2P performance proof
remain open. See
`BOUNDED_SOURCE_MANIFEST_PROJECTION_AND_SESSION_RESUME_AUDIT_rev1007.md` and
`REVISION_NOTES_rev1007.md`.

### Rev1007 validation

`Fresh GCC 14.2 Debug graph 557/557; GCC registry 292/292; GCC product 49/49; focused 5,001 protocol, 25 memory-shape, 207 reconciliation-service, 2,047 TLS, 114 sync-once, 737 payload-store, 536 folder-owner, 397 SQLite-owner, and 20 terminal-state checks; fresh Clang 17 ASan/UBSan product graph 268/268 and product 49/49 with leak detection and halt-on-error; focused source audit 26/26 and structural authority audit 592/592.`

Archive: `AnonSync-rev1007-2026.08.06.00.57-sourcemanifest-turncollapse-sessionresume-vivianite.zip`

Codename: `vivianite`


## Rev1006: receiver-local terminal scheduler and peer-independent completion

Rev1006 removes the remaining authenticated peer-turn dependency after a target
payload's complete bytes are already durable. One ordinary complete writable
payload-store scan now discovers exact pending terminal SHA-256 obligations from
the canonical staged-prefix inode and rev1004's checksum-framed journal. The
retained service then advances one fixed 32 MiB pulse locally and forces at
least one ordinary owner-loop turn before another pulse.

This is one lane in the existing single owner thread, not a second worker or
content engine. Intermediate work keeps rev1005's exact-name rooted observation
and fixed 64 KiB buffer. Final publication still requires the complete payload-
store scan and no-replace rename of the exact verified staged inode. Integrity,
lease contention, readiness, drain, ingress, watcher repair, and authenticated
networking remain in the shared service state machine.

The process cache is bounded to the existing transient-entry frontier and stores
only digest, total extent, and verified offset. It starts unknown and becomes
complete only after an ordinary whole-store observation. Restart reconstructs
the cache from durable prefixes and journals. Selection is deterministic by the
smallest verified offset and then digest. A stale cache entry already published
by another owner is removed with zero reported hash bytes. If cross-process
change makes the advisory cache overfull after a valid durable staging effect,
the cache is invalidated rather than turning that committed effect into an
operation failure; the next complete scan rebuilds it.

Live and terminal status advance to `anonsync.peer-service.status.v25`. They
expose the known/unknown work projection, exact next obligation, scheduler and
progress counts, completion and insertion counts, stale-cache reconciliations,
hashed bytes, ordinary-turn yields, and the last terminal step. The renderer
fails closed on impossible offsets, aggregates, or known/empty combinations.

A real shipping-process regression creates a 64 MiB-plus-4,097-byte completed
staged prefix, starts the configured receiver service with **no peer process**,
and requires exactly three local pulses: two bounded progress steps and one
complete final scan/publication step. The same PID stays ready and owner-
controllable through status and clean drain. Focused storage regressions also
prove two-target restart fairness, exact-name intermediate progress while an
unrelated namespace entry exists, the mandatory final namespace fence, and
truthful stale-cache accounting.

The remaining scale cost is explicit. A 4 TiB file still requires 131,072 local
32 MiB pulses and the corresponding disk reads, though it no longer requires
131,072 authenticated peer applies. First discovery and final publication retain
complete payload-store scans. Source-side target-manifest construction can still
read a complete source in one owner call, and cross-file chunk discovery remains
process-local rather than a restart-durable global index. Rev1006 does not add
rename/move identity, complete directories, Android support, selective
placeholders or automatic eviction, ENOSPC qualification, or public Tor/I2P
performance proof. See
`RECEIVER_LOCAL_TERMINAL_VERIFICATION_SCHEDULER_AUDIT_rev1006.md` and
`REVISION_NOTES_rev1006.md`.

### Rev1006 validation

`Exact rev1006 source passed a fresh GCC 14.2 Debug complete graph with 557/557 configured build edges and exact-source no-work re-attestation; all 291/291 registered tests and the independent 49/49 product set passed. Focused GCC proofs passed 20 terminal-state-codec, 737 payload-store, 397 SQLite-owner, 536 folder-owner, 110 sync-once, 196 reconciliation-service, and 2,044 TLS-transport checks; the shipping peer-independent scheduler process regression passed with no source peer. Source audits passed 33/33 receiver-local terminal-scheduler and 584/584 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 268/268 configured edges; all 49/49 product tests passed with leak detection and halt-on-error, and focused sanitizer payload-store proof passed all 737 checks. No compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic remained in passing evidence. The exact rev1005 parent SHA-256 matched b94e3c496bbec3c230c8d3af3081f53d0f519e9945943022df80ecc3f5e3199d and passed 41/41 wrapper-aware package checks. The final active implementation projection contains 622 files / 28,656,401 bytes with SHA-256 808d8740871083908600d243359c97e0253b456afef4ba65c5f4e88bb39e2b1f. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excludes the pre-correction sanitizer fixture-link failure, interrupted wrapper commands, the duplicate Ninja that briefly entered the same cache and was terminated, the remount-vanished unsealed worktree, and all obsolete validator branches and builds.`

Archive: `AnonSync-rev1006-2026.08.05.22.03-receiverlocalscheduler-restartdiscovery-ownerfairness-malachite.zip`

Codename: `malachite`


## Rev1005: targeted terminal proof and receiver-local verification pulse

Rev1005 keeps the restart-safe 32 MiB terminal SHA-256 journal from rev1004
while removing two avoidable costs from intermediate verification. Beneath the
same store-global exclusive lease, an incomplete step now independently reopens
the retained root and exact-observes only the journal, canonical complete
staged-prefix inode, and possible digest name. It does not enumerate unrelated
payload or transient entries.

The targeted observer is intentionally not publication authority. It re-proves
root identity, private regular-file shape, exact extent, pathname binding,
retained authority, and the lease, but grants no capacity, cleanup, or complete
namespace claim. Terminal completion still performs the ordinary complete store
scan immediately before no-replace digest publication. The regression proves an
unexpected unrelated entry permits intermediate computation progress but blocks
final publication.

Reconciliation can now advance up to **32 fixed terminal steps per authenticated
apply**, or 1 GiB at the shipping 32 MiB step size. Those receiver-local steps
carry no source bytes and keep the exact operation cursor outstanding until
local publication. TLS and both shipping CLI JSON surfaces expose total terminal
steps, local-continuation steps, and pulse exhaustion.

The adjacent audit found that a page completing several ranged files could
consume one automatic terminal step per file after the configured pulse was
spent. A narrow deferred-terminal range API now durably commits the exact
authenticated bytes but performs zero terminal SHA-256 work after exhaustion.
Later local continuation must verify and publish the exact staged inode. The
service rejects any path that crosses its configured frontier.

Focused proofs currently pass **706 payload-store**, **196 reconciliation-
service**, and **2,044 TLS-transport** checks, plus the real two-process ranged-
transfer regression, before final release sealing.

The remaining boundary is explicit. Files larger than 1 GiB can still require
payload-cold verification applies; a 4 TiB target can require up to 4,096 such
applies. First journal admission and final publication retain complete store
observations, and source target-manifest construction can still read a complete
source in one owner call. Multi-terabyte measurement and, if justified, a
bounded durable receiver-local background scheduler remain next. Rev1005 does
not add a global chunk index, rename/move identity, complete directories,
Android support, selective placeholders or automatic eviction, ENOSPC
qualification, or public Tor/I2P performance proof. See
`TARGETED_TERMINAL_VERIFICATION_AND_LOCAL_PULSE_AUDIT_rev1005.md` and
`REVISION_NOTES_rev1005.md`.

### Rev1005 validation

`Exact rev1005 source passed a fresh GCC 14.2 Debug complete graph with 555/555 configured build edges and exact-source no-work re-attestation; all 289/289 registered tests were accounted for across bounded immutable invocations, and the complete 48/48 product set was accounted for through aggregate and isolated heavy-test runs. Focused GCC proofs passed 20 terminal-state-codec, 706 payload-store, 4,999 reconciliation-protocol, 196 reconciliation-service, 536 folder-owner, 397 SQLite-owner, and 2,044 TLS-transport checks. Source audits passed 24/24 targeted-terminal/local-pulse, 38/38 terminal-continuation, 27/27 response-memory-shape, 34/34 direct-source-frame, 21/21 bounded-history-access, and 575/575 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 266/266 configured edges with no-work re-attestation; all 48/48 product tests were accounted for with leak detection and halt-on-error, including serial isolation of the two memory-heavy suites and the remaining lifecycle process tests. Focused sanitizer proofs passed 706 payload-store, 196 reconciliation-service, and 536 folder-owner checks; payload-store and folder-owner peak RSS were 729,432 KiB and 1,707,948 KiB. No compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic remained in passing evidence. The exact rev1004 parent SHA-256 matched 26c3fa06faeac08f6086d7154a76f05d536443067a941d7adf37579ca0f796d1 and passed 41/41 wrapper-aware package checks. The final active implementation projection contains 619 files / 28,550,115 bytes with SHA-256 5be67041b1b0254d8524a9ce05b0262a524f235d764601008398b9b95b69d778. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excludes interrupted aggregate CTest wrappers, one concurrent sanitizer lifecycle fixture whose precondition was invalidated by test concurrency but which passed serially on the same binaries, remount-vanished unsealed worktrees, and obsolete validator branches and builds.`

Archive: `AnonSync-rev1005-2026.08.05.19.37-targetedterminal-localpulse-exactcursor-goshenite.zip`

Codename: `goshenite`


## Rev1004: bounded terminal SHA-256 with generation-8 handoff

Rev1004 turns the receiver's one unbounded staged-target SHA-256 call into a
restart-safe **32 MiB per owner-call** continuation. One fixed-width,
checksum-framed two-slot journal binds a provider-independent
`ResumableSha256Checkpoint` to the exact payload-store identity and private
identity inode, target digest and extent, complete staged-prefix inode
observation, verified offset, and monotonic generation.

The journal is computation progress, not content authority. It is created only
after the staged prefix is complete and durable. Each step reads the exact staged
descriptor with a fixed 64 KiB buffer, re-proves the descriptor, pathname,
identity, and exclusive lease, and either publishes another nonterminal slot or
finishes SHA-256 in the current process. Final publication still requires exact
whole-content digest equality, a complete namespace and capacity preflight, and
no-replace rename of that exact opened inode under its digest.

Missing, malformed, foreign, or stale state restarts at SHA-256 offset zero but
still reads no more than 32 MiB in the current call. It never triggers a
complete compatibility reread and never truncates basename-committed data. A
torn newest slot falls back to the prior valid generation, repeating at most one
bounded computation step. A digest mismatch removes the exact invalid staged
owner and journal and publishes nothing.

Reconciliation protocol generation 8 represents the previously missing state
“all payload bytes received, receiver-local proof unfinished.” The final range
keeps the prior operation cursor and returns a continuation at the exact total
size. Later terminal turns repeat the exact operation but carry no payload
ranges and do not reopen source payload authority. The receiver admits the
operation only after local publication. Mixed generation-7/generation-8
operation is not claimed.

The adjacent audit found and corrected the first integration's cursor-advance
bug, removed dead per-range checkpoint helpers, removed an unused test helper
that produced a clean-build warning, and excluded a timestamp-stale object tree.
Fresh Clang linking then exposed compile/link sanitizer-inventory drift for the
new codec test; the target is now present in both inventories and the focused
audit parses the final-link inventory so the defect cannot silently recur.
Clean focused proofs currently pass **20 terminal-state**, **696 payload-store**,
**4,999 protocol**, and **194 reconciliation-service** checks before final
release sealing.

The remaining scale risk is explicit: every incomplete 32 MiB terminal step
currently consumes another payload-cold peer turn and staged-prefix namespace
observation. That can amplify high-latency routes and large namespaces for a
multi-terabyte target even though source payload bytes are never resent.
Source-side target-manifest construction can also still read a complete source
in one owner call. Rev1004 does not add a durable/global chunk index,
identity-preserving rename/move, complete directories, Android support,
selective placeholders or automatic eviction, ENOSPC qualification, or public
Tor/I2P performance proof. See
`BOUNDED_TERMINAL_PAYLOAD_VERIFICATION_CONTINUATION_AUDIT_rev1004.md` and
`REVISION_NOTES_rev1004.md`.

### Rev1004 validation

`Exact rev1004 source passed a fresh GCC 14.2 Debug complete graph with 555/555 configured build edges, followed by exact-source CMake regeneration and bundled-SQLite no-work re-attestation; all 288/288 registered tests and an independent isolated 48/48 product replay passed. Focused GCC proofs passed 20 terminal-state-codec, 696 payload-store, 4,999 reconciliation-protocol, 194 reconciliation-service, 536 folder-owner, 397 SQLite-owner, and 2,044 TLS-transport checks. Source audits passed 38/38 bounded terminal-verification-continuation checks and 567/567 structural authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph compiled its 266-edge configured dependency set across bounded resumptions; the first final link exposed that the new codec test was present in the sanitizer compile inventory but absent from the final-link inventory, the target graph was corrected, 28 exact-source relink edges and a no-work re-attestation passed, and all 48/48 registered product commands passed serially with leak detection and halt-on-error. Focused sanitizer proofs passed the same 20 terminal-state-codec, 696 payload-store, 4,999 protocol, 194 reconciliation-service, and 536 folder-owner checks; payload-store, reconciliation-service, and folder-owner peak RSS was 648,772 KiB, 780,832 KiB, and 1,694,640 KiB. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev1003 parent SHA-256 matched 58be646d3714895037e2dd1f928aa81e2fd200614eb9dfa75a5fdde16a424b53 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 36/36 changed wrapper files, all 35/35 changed project files, all 32/32 changed active files, and the complete 618-file active projection byte-for-byte and mode-for-mode. The final active implementation projection contains 618 files / 28,499,104 bytes with SHA-256 7b4499a95932e5d3ec3452c9982c3dc8f3f2a3e15b79962f90b953144ac709e9. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excludes both remount-vanished unsealed worktrees and their builds, obsolete pre-generation-8 evidence, the first aggregate sanitizer run invalidated by concurrent memory-heavy tests, the CTest wrapper invocation that stalled despite a passing direct proof, and the pre-correction sanitizer final-link failure.`

Archive: `AnonSync-rev1004-2026.08.05.16.01-terminalcontinuation-zerobytepulse-inodejournal-cordierite.zip`
Codename: `cordierite`

## Rev1003: bounded same-path predecessor projection

Rev1003 keeps reconciliation protocol generation 7 and removes another hidden
complete-file read from one receiver apply. Same-path predecessor
content-defined projection now advances at most **32 MiB per apply** and at most
once per apply. The unfinished projection is process-local, bounded by the
existing 8,192-chunk frontier, and reopens and re-proves the exact immutable
source observation on every step.

Fully completed adaptive chunks are indexed and reused before the predecessor's
whole manifest finishes. Every reused range still passes through exact chunk
SHA-256 and size matching, descriptor-rooted source reproof, bounded range
hashing, crash-safe prefix staging, and final whole-target SHA-256. Only exact
whole-source completion creates the retained predecessor manifest and final
index.

Same-path and cross-file projection now share one incremental digest-order and
cumulative-offset helper. The adjacent audit also corrected a stale-state
hazard: when the lower payload-store projection clears private progress after a
failure, the service now clears the enclosing index at the same cutpoint.

The deterministic 48 MiB shifted-insertion regression requires exactly two
projection steps under the shipping 32 MiB frontier, proves the first step is
incomplete, reuses completed chunks before whole-source completion, hashes
exactly 48 MiB in aggregate, reduces network transfer, and converges exact bytes
and causal evidence. The focused suite passes **189 checks** before release
sealing.

This is not a global local-I/O bound. Incomplete predecessor projection is not
restart-durable; source-side target-manifest construction can still read a
complete source; and terminal staged-target completion still rehashes the
complete target in one owner call. A rejected pathname-carried resumable-SHA
prototype was excluded because it lacked a separately integrity-framed,
store-identity- and inode-bound durable authority record and safe crash/legacy
transitions. Final whole-target SHA-256 remains authoritative. Rev1003 is not a
durable or global chunk index, target-scale multi-terabyte measurement,
rename/move implementation, complete directory model, Android adapter,
selective placeholder or eviction system, ENOSPC qualification, or public-route
performance proof. See
`BOUNDED_SAME_PATH_PREDECESSOR_PROJECTION_AND_TERMINAL_VERIFICATION_AUDIT_rev1003.md`
and `REVISION_NOTES_rev1003.md`.

### Rev1003 validation

`Exact rev1003 source passed a fresh GCC 14.2 Debug graph: 262/262 product-dependency edges plus 290/290 remaining all-target edges (552/552 total), followed by bundled-SQLite re-attestation; all 286/286 registered tests and an independent 47/47 product replay passed. Focused GCC proofs passed 677 payload-store, 189 reconciliation-service, 536 folder-owner, 397 SQLite-owner, and 2,044 TLS-transport checks. Source audits passed 22/22 bounded predecessor projection, 32/32 bounded cross-file projection, 31/31 bounded local reuse, 31/31 content-defined delta, 27/27 multi-range window, 27/27 manifest reference, 21/21 bounded-history access, and 548/548 structural authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 262/262 edges and all 47/47 product tests passed with leak detection and halt-on-error; focused sanitizer proofs passed 677 payload-store, 189 reconciliation-service, and 536 folder-owner checks, with peak RSS 519,504 KiB, 791,616 KiB, and 1,704,200 KiB respectively. Aggregate final-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev1002 parent SHA-256 matched e547cbe11ae3bae98f15946a38f30dd64881510987edac35a6c490a64220bf03 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 14/14 changed wrapper paths, all 13/13 changed project paths, all 10/10 changed active paths, and the complete 614-file active projection byte-for-byte and mode-for-mode. The final active implementation projection contains 614 files / 28,363,976 bytes with SHA-256 16eeae537cb0683f6a51aa044b9c9aea9a44f93ced30530664b5de55cb580aa8. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excluded the remount-vanished initial worktree and build, the rejected raw pathname-carried SHA-state prototype, the stale non-authoritative /home/oai/share validator and its build tree, the initial unbuilt focused-sanitizer target invocation, and the superseded rev0999 lexical oracle failure before its exact cutpoint-owned lifetime check was corrected.`

Archive: `AnonSync-rev1003-2026.08.05.12.35-boundedpredecessor-partialindex-terminalfence-phenakite.zip`
Codename: `phenakite`

## Rev1002: bounded local delta-copy and interior-chunk resumption

Rev1002 keeps reconciliation protocol generation 7 and closes the matched-chunk
copy latency edge left by rev1001. At the four-terabyte payload ceiling, one
canonical adaptive chunk may reach **2 GiB**. Same-path and cross-file local
reuse now share one product-owned **32 MiB source-read frontier per apply**.
Every byte actually read from a local candidate consumes that frontier.

The receiver locates the adaptive chunk containing the durable prefix, derives
the exact intra-chunk source offset, reopens and re-proves the immutable
candidate, and advances the existing crash-safe contiguous prefix. A later
service can rebuild acceleration state and resume inside the same chunk.

Local copy uses a separate **four-MiB range ceiling** rather than peer-negotiated
wire framing. Exhaustion suppresses further local reads but does not discard the
rest of the authenticated response. Fully covered ranges are accounted as
already durable; a partial overlap drops only the committed prefix, hashes the
advancing suffix, and stages that suffix normally. Protocol generation remains
unchanged.

The deterministic regression uses a 24 MiB predecessor, a 256 KiB insertion,
three 768 KiB wire ranges per response, and a one-MiB test copy frontier. It
reconstructs the service after exhaustion and proves interior resumption,
partial-overlap suffix preservation, exact wire/staged/reused accounting,
bounded local reads, lower network bytes, exact target bytes, and exact causal
convergence. The focused suite passes **185 checks** before release sealing.

This is not a global local-I/O limit. Same-path predecessor manifest construction
can still hash a complete very large source in one apply, and final staged-prefix
completion can still rehash the complete target in one owner call. Cross-file
projection has its own independent 32 MiB frontier. Rev1002 does not add a
durable/global chunk index, target-scale sparse multi-terabyte measurements,
identity-preserving rename/move, complete directories, placeholders, automatic
eviction, Android support, ENOSPC qualification, or public-route performance
proof. See
`BOUNDED_LOCAL_DELTA_COPY_AND_INTERIOR_CHUNK_RESUMPTION_AUDIT_rev1002.md` and
`REVISION_NOTES_rev1002.md`.

### Rev1002 validation

`Exact rev1002 source passed a fresh GCC 14.2 Debug graph (551/551 configured build edges) and a no-work bundled-SQLite re-attestation; all 285/285 registered tests were accounted for, including both final documentation-sensitive audits, and an independent 47/47 product replay passed. Focused GCC proofs passed 677 payload-store, 185 reconciliation-service, 536 folder-owner, 397 SQLite-owner, and 2,044 TLS-transport checks. Source audits passed 31/31 bounded local reuse, 32/32 bounded resumable cross-file projection, 31/31 content-defined delta, 27/27 multi-range window, 27/27 manifest reference, and 538/538 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product dependency graph completed 262/262 edges and reached a no-work re-attestation; all 47/47 product tests were accounted for with leak detection and halt-on-error. Focused sanitizer proofs passed 677 payload-store, 185 reconciliation-service, and 536 folder-owner checks; the folder-owner proof completed in 30.21 seconds at 1,694,316 KiB peak RSS, the reconciliation-service proof in 21.07 seconds at 778,188 KiB, and the payload-store proof in 9.47 seconds at 519,228 KiB. Aggregate final-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev1001 parent SHA-256 matched f5f7313ecd228074cd040cf432305626aa2654e4d936c125ec4daa26098b2de4 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 17/17 changed wrapper paths, all 16/16 changed project paths, all 13/13 changed active paths, and the complete 613-file active projection byte-for-byte and mode-for-mode. The final active implementation projection contains 613 files / 28,332,387 bytes with SHA-256 adcc77e2efda814bfb8d69cfd03ee289ba7077085cd3fa6a6c44e45d90cd4374. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excluded remount-vanished scratch worktrees, the divergent unsealed local-copy prototype, an interrupted aggregate sanitizer shard, the pre-build missing-target invocation, superseded lexical-audit failures, and generated Python bytecode removed before projection sealing.`

Archive: `AnonSync-rev1002-2026.08.05.11.19-localcopyfrontier-interiorresume-wireoverlap-sinhalite.zip`
Codename: `sinhalite`

## Rev1001: bounded resumable cross-file projection

Rev1001 keeps reconciliation protocol generation 7 and corrects the remaining
single-turn latency defect in rev1000's cross-file discovery. A plausible local
candidate is no longer hashed to completion in one reconciliation apply. The
receiver advances one process-local content-defined projection by at most **32
MiB per apply invocation**, reopens the immutable source on every step, and
re-proves the exact eleven-field POSIX observation before accepting progress.

Complete and resumable source hashing now share one digest accumulator, so
rolling boundaries, whole SHA-256, chunk SHA-256, and final extent checks cannot
drift into two implementations. The move-only projection retains no descriptor,
payload lease, namespace capability, or durable authority. Any read or
observation failure clears unfinished progress.

Completed chunks become immediately eligible for the existing exact local-copy
and durable-staging path. A useful renamed source can therefore reduce network
bytes before its whole manifest finishes. A complete source manifest is cached
only after the exact whole source SHA-256 has been re-proved; final target whole
SHA-256 and terminal causal admission remain publication authority.

A current-visible source may be causally known before its payload exists in the
receiver's private store. The candidate sweep now binds the payload store's
process-local durable-availability generation. A newly inserted payload restarts
an exhausted same-process sweep without requiring a visible-state change.

The focused 48 MiB regression first skips an absent matching source, scans an
unrelated decoy in two bounded turns, publishes the useful source without
changing causal state, restarts the exhausted search, and scans the source in two
bounded turns. It proves partial chunk reuse before whole-manifest completion,
materially lower network bytes, and exact final bytes. Shipping TLS and both CLI
JSON surfaces expose unavailable candidates, availability restarts, and bounded
projection steps.

This bounds candidate projection hashing latency; it does not reduce the **total
cold** bytes required to reject every candidate. Progress is **process-local**
and is not restart-durable. This is not a **durable or global chunk index**. At
the four-terabyte ceiling, copying one already matched adaptive chunk is **not
yet resumable** under the 32 MiB projection frontier and can remain a large local
I/O effect. Rev1001 does not add identity-preserving rename/move, Android,
placeholders, target-scale multi-terabyte measurements, ENOSPC qualification, or
public-route performance proof. See
`BOUNDED_RESUMABLE_CROSS_FILE_PROJECTION_AUDIT_rev1001.md` and
`REVISION_NOTES_rev1001.md`.

### Rev1001 validation

`Exact rev1001 source passed a fresh GCC 14.2 Debug graph (551/551 configured build edges) and a no-work bundled-SQLite re-attestation; all 284/284 registered tests were accounted for, including both final documentation-sensitive audits, and an independent 47/47 product replay passed. Focused GCC proofs passed 677 payload-store, 158 reconciliation-service, 536 folder-owner, 397 SQLite-owner, and 2,044 TLS-transport checks. Source audits passed 32/32 bounded resumable projection, 22/22 inherited cross-file discovery, 31/31 content-defined delta, 27/27 manifest reference, and 521/521 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product dependency graph completed 262/262 edges and reached a no-work re-attestation; all 47/47 product tests were accounted for with leak detection and halt-on-error. Focused sanitizer proofs passed 677 payload-store, 158 reconciliation-service, and 536 folder-owner checks; the folder-owner proof completed in 32.10 seconds at 1,684,368 KiB peak RSS. Aggregate final-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev1000 parent SHA-256 matched c68736ec03cd91298180b689a5c85228cdced06679e3b1fc836949017fd6d8c3 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 21/21 changed wrapper paths, all 20/20 changed project paths, all 17/17 changed active paths, and the complete 612-file active projection byte-for-byte and mode-for-mode. The final active implementation projection contains 612 files / 28,276,868 bytes with SHA-256 9e3197543e4f453cd5bd17897304ab44c3733e08e510a496b391d56383ee3b9e. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excluded remount-vanished worktrees and caches, the divergent availability-only release branch, interrupted aggregate CTest wrappers, superseded lexical-audit failures, and generated Python bytecode removed before projection sealing.`

Archive: `AnonSync-rev1001-2026.08.05.08.49-boundedprojection-lateavailability-singleindex-chrysoprase.zip`
Codename: `chrysoprase`

## Rev1000: bounded cross-file content-defined discovery

Rev1000 closes the first same-path-only delta gap for Linux media trees. A
receiver can now discover reusable content-defined chunks in another current
visible file even when the incoming operation has no same-path causal
predecessor. Renamed, reorganized, duplicated, or regenerated media can reuse
local immutable bytes after an insertion or edit instead of retransmitting the
complete changed file.

The SQLite owner exposes one canonical current-primary path page with hard
product ceilings of 64 visible paths and 4 MiB of canonical operation bytes.
The cursor is bound to the exact visible-state digest, stale state returns
before operation decoding, tombstones consume the frontier without becoming
candidates, and the query neither reconstructs retained history nor sorts a
complete visible projection.

The receiver moves one page into process state and consumes it across apply
turns. It hashes at most one plausible candidate payload per turn and retains at
most one matching manifest and index. An unrelated 48 MiB media candidate and a
matching renamed 48 MiB candidate prove the same page is not re-read after the
first hash. Same-path predecessor reuse and cross-file reuse now share one exact
local range-copy and durable-staging boundary.

Every reused range is reopened from the immutable payload store, matched by
exact chunk SHA-256 and size, and staged through the existing crash-safe prefix.
Final whole-payload SHA-256 and terminal causal admission remain authority.
Protocol generation 7 is unchanged, and the new work counters flow through TLS
and both shipping CLI JSON surfaces.

This is not a global chunk index. The candidate page and manifest are memory-
bounded, but one complete candidate can still require a complete multi-terabyte
byte read. Search covers current visible files only and is process-local.
Rev1000 does not add identity-preserving rename/move, directory semantics,
Android support, placeholders, retention collection, ENOSPC qualification, or
public-route throughput proof. See
`CROSS_FILE_CONTENT_DEFINED_DISCOVERY_AUDIT_rev1000.md` and
`REVISION_NOTES_rev1000.md`.

### Rev1000 validation

Exact rev1000 source passed a fresh GCC 14.2 Debug graph (551/551 configured build edges) and a no-work bundled-SQLite re-attestation; all 283/283 registered tests were accounted for, including the two final documentation-sensitive source audits, and an independent 47/47 product replay passed. Focused GCC proofs passed 397 SQLite-owner, 144 reconciliation-service, 536 folder-owner, and 2,044 TLS-transport checks. Source audits passed 22/22 cross-file discovery, 31/31 content-defined delta, 27/27 manifest-reference, and 511/511 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product dependency graph completed 262/262 edges and reached a no-work re-attestation; all 47/47 product tests passed with leak detection and halt-on-error. Focused sanitizer proofs passed 397 SQLite-owner, 144 reconciliation-service, and 536 folder-owner checks; the folder-owner proof completed in 29.87 seconds at 1,690,840 KiB peak RSS, the reconciliation-service proof in 30.17 seconds at 774,444 KiB, and the SQLite-owner proof in 11.38 seconds at 777,440 KiB. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0999 parent SHA-256 matched 7b897c44e66870dd55e5df707d5d5e5180f60edbbe2baf4af431b861490cd3e0 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 20/20 changed wrapper paths, all 19/19 changed project paths, all 16/16 changed active paths, and the complete 611-file active projection byte-for-byte and mode-for-mode. The final active implementation projection contains 611 files / 28,197,616 bytes with SHA-256 9653cca2703de4448b510a49c8321d95c72354716de08152bedaec8185197c05. Final wrapper-directory verification passed 32/32 checks; ZIP, CRC, canonical-path, no-symlink, and release-policy verification passed 41/41 checks; and clean extraction matched the staged wrapper path-for-path, byte-for-byte, type-for-type, and mode-for-mode. Validation excluded remount-vanished worktrees and caches, timestamp-only CMake regeneration attempts, interrupted aggregate real-process harnesses, a divergent indexed cross-file prototype and its validators, unrelated build lanes, and a redundant terminated sanitizer rerun.

Archive: `AnonSync-rev1000-2026.08.05.06.02-crossfilechunks-visiblepage-singlehash-hackmanite.zip`
Codename: `hackmanite`

## Rev0999: bounded reconciliation history access

Rev0999 keeps reconciliation protocol generation 7 while removing a severe
history-wide multiplier from bounded large-file transfer. A maximum four-
terabyte payload can require 65,536 response windows at the fixed 64 MiB page
frontier. Rev0998 bounded payload ownership, but requester creation, source
serving, and receiver apply still reconstructed complete retained replica
history on every window. That admitted 262,144 complete model reconstructions
across one maximum transfer before terminal admission work.

The SQLite owner now exposes a fixed identity cutpoint that re-attests schema,
foreign-key mode, typed owner metadata, limits, database incarnation, and
recovery epoch without decoding operation or projection rows. Evidence paging
uses one primary-key range query with an exact cursor lookup and a page-plus-one
SQL limit; it no longer rebuilds or sorts the complete causal model. Receiver
predecessor reuse uses the released exact-path cutpoint instead of searching a
whole local operation vector. The predecessor is copied out of the cutpoint
before its lifetime ends.

SQL-trace regressions populate nontrivial histories and reject complete
operation or visible projections in identity and page paths. The shipping
multi-range delta regression proves the first progress turn is history-cold and
that every source window uses one bounded evidence range. Final remote operation
admission deliberately retains complete causal reconstruction; rev0999 moves
that cost out of each byte-progress turn rather than weakening admission.

This optimization assumes the deployment singleton and AnonSync-owned SQLite
connection remain the cooperative local writer boundary. It is not protection
against a noncooperating same-UID process editing database rows between cold
full validations. It does not add cross-file chunk discovery, rename/move,
Android support, target-scale soak proof, quota/ENOSPC behavior, or route
throughput qualification. See
`BOUNDED_RECONCILIATION_HISTORY_ACCESS_AUDIT_rev0999.md` and
`REVISION_NOTES_rev0999.md`.

### Rev0999 validation

Exact rev0999 source passed a fresh GCC 14.2 Debug graph (551/551 configured build edges)
and a no-work bundled-SQLite re-attestation; all 282/282 registered tests were accounted
for, including the two final documentation-sensitive source audits, and an independent 47/47
product replay passed. Focused GCC proofs passed 380 SQLite-owner, 122 reconciliation-
service, and 536 folder-owner checks. Source audits passed 21/21 bounded-history-access,
34/34 direct-source-frame, 27/27 response-memory-shape, 30/30 targeted-path-cutpoint, and
503/503 structural-authority checks. A fresh Clang 17 Debug
AddressSanitizer/UndefinedBehaviorSanitizer product dependency graph completed 262/262 edges
across bounded resumptions and reached a no-work re-attestation; all 47/47 product tests
passed with leak detection and halt-on-error. Focused sanitizer proofs passed 380 SQLite-
owner, 122 reconciliation-service, and 536 folder-owner checks; the folder-owner proof
completed in 28.75 seconds at 1,689,024 KiB peak RSS, while the complete product lane peaked
at 1,692,312 KiB. Aggregate retained-log inspection found no compiler, linker,
AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic.
The exact rev0998 parent SHA-256 matched
dbc9b4f7fb972abd2ecfa10cabebeed6b5bba7c8c277d511bf2834d87bfd702f and passed 41/41 wrapper-
aware package checks. The binary-aware source patch reconstructed all 17/17 changed wrapper
paths, all 16/16 changed project paths, all 13/13 changed active paths, and the complete
610-file active projection byte-for-byte and mode-for-mode. The final active implementation
projection contains 610 files / 28,125,448 bytes with SHA-256
5110b2cce7e9f19917c9bf10a958fb22c4a42eee1affdadb64b5c88128153d68. Validation excluded
divergent unsealed rev0999 prototypes, an orphaned exclusion guard that named the live
authority, unrelated compiler/test lanes, vanished remount-era worktrees and build caches,
interrupted build chunks, and every result not re-proved from the reconstructed exact
source. Final directory, ZIP, CRC, path-policy, no-symlink, and clean-extraction equality
checks remain mandatory publication gates.

Archive: `AnonSync-rev0999-2026.08.05.02.52-primarykeypage-identitycutpoint-historycold-taaffeite.zip`
Codename: `taaffeite`

## Rev0998: direct immutable-payload fill into one source frame

Rev0998 keeps reconciliation protocol generation 7 wire-compatible while
removing the remaining payload-sized source owner beside one grouped response
frame. The service now plans metadata plus exact immutable payload descriptors
and bounded ranges, reserves one canonical frame, and asks those descriptors to
fill the frame's writable payload holes directly. Payload bytes are hashed as
they enter the frame, the exact inode observation is re-proved afterward, and
the complete request-bound response is validated against frame-backed views
before the structural trailer is committed.

The new opened-payload operation accepts caller-owned `std::span<char>` storage.
It uses position-independent `pread`, caps each syscall at `SSIZE_MAX`, retains
the existing complete-payload corruption witness and typed error, and shares one
byte-reading implementation with the compatibility string-returning API. Exact
payload descriptors and inode-use leases are released before the frame can enter
TLS backpressure. The shipping TLS path uses this direct result; only the
explicit compatibility service API reconstructs owned payload strings.

A product allocation oracle publishes an actual 64 MiB payload, releases the
setup buffer, tags allocations by observation generation, and observes every
allocation at or above 2 MiB. The shipping path must have exactly one such
allocation live at once: the final frame. The compatibility API must expose the
expected two simultaneously live owners—frame plus decoded payload—without
changing canonical bytes. A second fixture models the maximum 4 TiB payload
extent with 4,096 one-GiB content-defined chunks while transferring one four-MiB
range; it likewise permits one live large allocation and proves that logical
extent does not become resident payload ownership. Protocol lifecycle and
payload-store range tests bind incomplete, duplicate, malformed, oversized, and
post-finish failures.

This is a deterministic C++ heap-shape correction, not complete operating-system
peak-RSS proof. Public in-process protocol limits may reduce but cannot raise the
fixed product frontiers of 128 payload descriptors, 64 MiB of payload bytes per
page, or a 96 MiB response frame. Live TLS and process accounting requires zero
aggregate payload-page bytes at frame reservation, zero range staging, and at
most 128 exact source descriptors. The final frame itself, metadata vectors, one
bounded manifest, descriptor objects, OpenSSL, kernel buffers, page cache, and
validation hashes remain outside the one-frame allocation claim. Rev0998 does not add cross-file chunk discovery,
rename/move identity, complete directory semantics, placeholders, retention
collection, Android adapters, route throughput qualification, or ENOSPC
recovery. See `DIRECT_SOURCE_PAYLOAD_FRAME_ASSEMBLY_AUDIT_rev0998.md` and
`REVISION_NOTES_rev0998.md`.

### Rev0998 validation

Exact rev0998 source passed a fresh GCC 14.2 Debug graph (551/551 configured build edges) and a no-work bundled-SQLite re-attestation; all 281/281 registered tests and an independent 47/47 product replay were accounted for from the exact source. Focused GCC proofs passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 652 payload-store, 39 content-defined-chunker, 98 network-model plus 41 generated-operation, 361 SQLite-owner, 536 folder-owner, 110 sync-once, 4,989 reconciliation-protocol, 6 response-frame-memory, 25 borrowed-memory-shape, 10 direct-source-frame, 117 reconciliation-service, 2,044 TLS-transport, and 162 local-control checks. Source audits passed 34/34 direct-source-frame, 19/19 response-frame-memory, 27/27 response-memory-shape, 33/33 targeted-source-access, and 496/496 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product dependency graph completed 262/262 edges; all 47/47 product tests passed with leak detection and halt-on-error. Focused sanitizer proofs passed 652 payload-store, 4,989 reconciliation-protocol, 10 direct-source-frame, 117 reconciliation-service, 2,044 TLS-transport, and 536 folder-owner checks; the folder-owner proof completed in 29.39 seconds at 1,692,128 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0997 parent SHA-256 matched 64125a2e82f1e9bb789c14abc2f94f5dbf55c667e6f61b92406b5fbd4389e6de and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 25/25 changed project paths, all 22/22 changed active paths, the one changed wrapper restart page, and the complete 609-file active projection byte-for-byte and mode-for-mode. The final active implementation projection contains 609 files / 28,088,843 bytes with SHA-256 35acfcd7ff22a865d1321a5272b96af33dd6d138a21641178386a4ab746fbe41. Validation excluded two divergent unsealed rev0998 branches, pathname-based cleanup actors, vanished worktrees, interrupted aggregate CTest wrappers, and every result not bound to the final exact source.

Archive: `AnonSync-rev0998-2026.08.05.01.10-directsourceframe-zerostaging-fourterabyteproof-ulexite.zip`
Codename: `ulexite`

## Rev0997: one owned source frame and borrowed receiver payloads

Rev0997 keeps reconciliation protocol generation 7 wire-compatible while
collapsing avoidable ownership across both sides of one grouped response. The
source overflow-checks the exact canonical body and frame sizes, reserves one
final frame, and appends the body directly behind the wire header. The shipping
request-bound encoder does not materialize a full body and does not derive an
unused semantic digest; the compatibility API can still derive that digest from
the body already resident inside the final frame without serializing it again.

A by-value TLS write path moves the final frame allocation into the existing
bounded continuation. Before network backpressure, the source retains compact
post-write decisions and releases response operations, payload strings, and
metadata-only IDs. Shipping JSON reports
`reconciliation_response_frame_owned_handoffs`, and process tests bind the
counter to actual continuation ownership.

The receiver structurally verifies the retained TLS frame and parses payload
byte fields as `std::string_view` instances into that frame. Owned payload
strings remain empty through the shipping apply path. Normal contiguous-prefix
staging hashes, compares, and writes those views directly; the only remaining
record copy is the explicitly bounded whole-payload or legacy compatibility
path, never another 64 MiB aggregate owner.

Two deterministic allocation regressions bind the change. An 8 MiB source
response permits one frame-sized allocation plus bounded auxiliary work. A
sixteen-payload, 16 MiB fixture requires exactly one page-sized encode
allocation, zero page-sized borrowed-decode allocations, frame-contained views,
unchanged generation-7 bytes and semantic digest, and the expected copy
differential from the legacy owned decoder.

This is not an end-to-end peak-RSS claim. Response payload objects and the final
frame still coexist at the source encoding cutpoint, and OpenSSL and kernel
socket buffers are outside both allocation oracles. The 64 MiB frontier must not
be raised until measured sparse and synthetic multi-terabyte tests cover RSS,
disk amplification, restart, high-latency direct/Tor/I2P behavior, and
controlled ENOSPC. Rev0997 does not add cross-file chunk discovery, rename/move
identity, complete directory semantics, placeholders, retention collection,
Android lifecycle/storage adapters, or public-route privacy qualification. See
`DIRECT_RESPONSE_FRAME_AND_OWNED_TLS_HANDOFF_AUDIT_rev0997.md`,
`SINGLE_FRAME_RESPONSE_AND_BORROWED_PAYLOAD_DECODE_AUDIT_rev0997.md`, and
`REVISION_NOTES_rev0997.md`.

### Rev0997 validation

Exact rev0997 source passed a fresh 549-edge GCC 14.2 Debug graph and a no-work bundled-SQLite re-attestation; all 279/279 registered tests passed, and an independent 46/46 product replay passed. Focused GCC proofs passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 650 payload-store, 39 content-defined-chunker, 98 network-model plus 41 generated-operation, 361 SQLite-owner, 536 folder-owner, 110 sync-once, 4,967 reconciliation-protocol, 6 source-frame-memory, 25 borrowed-memory-shape, 117 reconciliation-service, and 2,044 TLS-transport checks. Source audits passed 19/19 direct-response-frame, 27/27 borrowed-response-memory, and 482/482 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 260/260 edges; all 46/46 product tests passed with leak detection and halt-on-error, and focused sanitizer proofs passed 650 payload-store, 4,967 reconciliation-protocol, 6 source-frame-memory, 25 borrowed-memory-shape, 117 reconciliation-service, and 2,044 TLS-transport checks. The sanitized 536-check folder-owner proof completed in 28.20 seconds at 1,688,636 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0996 parent SHA-256 matched f57105c8156a138decc394c4c25092b87d5df83f919b03c401e18a3fec75a007 and passed 41/41 wrapper-aware package checks. Its inherited stale visible goshenite/20.48 labels were corrected to the actual sealed petalite/20.52 identity already bound by lineage and release gate. The active implementation projection contains 607 files / 27,989,270 bytes with SHA-256 00840cfa9a06971c6d5e69784303b524a8158275624a7abe78b17b38027c8f5b. Final directory, ZIP, CRC, path-policy, no-symlink, and clean-extraction equality checks remain mandatory publication gates.

Archive: `AnonSync-rev0997-2026.08.04.22.41-singleframe-ownedtls-borrowedstaging-diaspore.zip`
Codename: `diaspore`

## Rev0996: bounded multi-range payload windows

Rev0996 advances reconciliation to protocol generation 7 and lets one large-file
response carry several canonical contiguous range records instead of exactly
one. The existing independent limits remain authoritative: at most 128 payload
records, 4 MiB in one record, 64 MiB of payload bytes in one page, one ranged
payload identity, and one complete bounded content-defined manifest.

At the exact 4 TiB frontier, the default window carries sixteen 4 MiB records.
The framing arithmetic falls from 1,048,576 request/response turns to 65,536,
avoiding 983,040 serialized turns. This is exact limit arithmetic, not a
measured 4 TiB transfer.

Every group is sorted by digest and offset, gap-free, size-bound, and tied to
one manifest digest. The complete manifest appears only on the first cache-cold
record; later records use exact references. The source performs one cumulative-
index lookup and advances linearly through the retained index. The receiver
consumes contiguous spans into the validated response, preserves the durable-
prefix and final whole-file SHA-256 rules, skips records already covered by
local reuse, and rejects overlap or gaps. Operation metadata remains behind
whole-payload durability.

Grouped-window, range-record, and ranged-byte counters cross the authenticated
TLS source result and the shipping JSON surface. The TLS restart oracle now
stages two four-byte records in one round trip; the real process oracle stages
sixteen four-mebibyte records in one 64 MiB round trip. A separate deterministic
frontier regression proves that once a whole payload exhausts the page byte
budget, the next large file is not opened, hashed, indexed, or published.

The adjacent refactor removed pointer vectors from both protocol validation and
receiver grouping. The configured 64 MiB page can now become real resident
payload data, and encoding/TLS may add page-sized copies; target-scale RSS is
therefore the next delta-transfer measurement and refactor boundary. Rev0996
does not claim streaming framing, a completed multi-terabyte transfer, cross-
file chunk discovery, Android, rename/move identity, complete directory
semantics, placeholders, quota safety, or ENOSPC qualification. See
`MULTI_RANGE_PAYLOAD_WINDOW_AND_TURN_COLLAPSE_AUDIT_rev0996.md` and
`REVISION_NOTES_rev0996.md`.

### Rev0996 validation

Exact rev0996 source passed a fresh 545-edge GCC 14.2 Debug graph and a no-work bundled-SQLite re-attestation; all 275/275 registered tests were accounted for across bounded terminal shards, and an independent 44/44 product replay passed. Focused GCC proofs passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 650 payload-store, 39 content-defined-chunker, 98 network-model plus 41 generated-operation, 361 SQLite-owner, 536 folder-owner, 110 sync-once, 4,960 reconciliation-protocol, 117 reconciliation-service, and 2,044 TLS-transport checks. Source audits passed 31/31 content-defined-delta, 18/18 source-chunk-index, 27/27 manifest-reference, 33/33 targeted-source-access, 52/52 selective-sync, 27/27 multi-range-window, and 472/472 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 256/256 edges; all 44/44 product tests passed with leak detection and halt-on-error, and focused sanitizer proofs passed 650 payload-store, 39 content-defined-chunker, 4,960 reconciliation-protocol, 117 reconciliation-service, and 2,044 TLS-transport checks. The sanitized 536-check folder-owner proof completed in 31.26 seconds at 1,694,252 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0995 parent SHA-256 matched 1129c9f66ba195ceda3f18b274ae58a997820ce332b44c39f9cfdf0fa033efc2 and passed 41/41 wrapper-aware package checks. The active implementation projection contains 603 files / 27,896,855 bytes with SHA-256 a42f7210b2c2109e990fef097fc26e87497cffe3770b4a1fe4b1de20f6432052. Final directory, ZIP, CRC, path-policy, no-symlink, and clean-extraction equality checks remain mandatory publication gates.

Archive: `AnonSync-rev0996-2026.08.04.20.52-multirangewindow-turncollapse-memoryfrontier-petalite.zip`
Codename: `petalite`


## Rev0995: retained source chunk index and million-range frontier

Rev0995 removes a severe source-side repeated-work multiplier from the
content-defined delta path. Rev0994 retained the canonical source manifest across
one authenticated serve session, but each 4 MiB ranged response rebuilt its full
cumulative chunk-offset vector. At the exact 4 TiB frontier, 1,048,576 ranges and
8,192 chunks admitted 8,589,934,592 redundant prefix additions and
68,727,865,344 bytes (64.0078125 GiB) of avoidable offset-vector element traffic.

The source session now retains one cohesive bounded cache binding exact payload
identity, rooted descriptor metadata, manifest digest, canonical manifest, and
cumulative offsets. It builds the index once, reuses it for valid continuations,
and resets it as one object on source change. A stale manifest reference is
rejected before chunk lookup and before payload range copy. Build, reuse, and
lookup counters cross TLS and reach the shipping JSON surface.

This correction is not the completed multi-terabyte performance model. A 4 TiB
file at a 4 MiB wire range still requires 1,048,576 serialized request/response
turns. The next delta-transfer slice is bounded multi-range or byte-window
framing that preserves the current chunk confinement, durable-prefix restart,
and whole-file SHA-256 authority.

Rev0995 does not claim a completed multi-terabyte transfer, target-scale RSS,
cross-file chunk discovery, Android, rename/move identity, directory semantics,
placeholders, quota safety, or ENOSPC qualification. See
`SOURCE_CHUNK_INDEX_AND_MULTI_TERABYTE_RANGE_SCALE_AUDIT_rev0995.md` and
`REVISION_NOTES_rev0995.md`.

### Rev0995 validation

Exact rev0995 source passed a fresh 545-edge GCC 14.2 Debug graph and a no-work bundled-SQLite re-attestation; all 274/274 registered tests were accounted for across bounded terminal shards and an independent 44/44 product replay passed. Focused GCC proofs passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 650 payload-store, 39 content-defined-chunker, 98 network-model plus 41 generated-operation, 361 SQLite-owner, 536 folder-owner, 110 sync-once, 4,956 reconciliation-protocol, 115 reconciliation-service, and 2,044 TLS-transport checks. Source audits passed 18/18 source-chunk-index, 31/31 content-defined-delta, 27/27 manifest-reference, 33/33 targeted-source-access, 52/52 selective-sync, and 463/463 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 256/256 edges; all 44/44 product tests passed with leak detection and halt-on-error, and focused sanitizer proofs passed 650 payload-store, 39 content-defined-chunker, 4,956 reconciliation-protocol, 115 reconciliation-service, and 2,044 TLS-transport checks. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0994 parent SHA-256 matched cce60aea2ce146228f5163720b74b1ec666b3e56e204c5f155108d22f91ecd9a and passed 41/41 wrapper-aware package checks. The active implementation projection contains 602 files / 27,851,618 bytes with SHA-256 98fd496d786433027529c2628adc2a0f1e12c029300cb1084bd55804c965d7c1. Final directory, ZIP, CRC, path-policy, no-symlink, and clean-extraction equality checks remain mandatory publication gates.

Archive: `AnonSync-rev0995-2026.08.04.19.00-sourceindex-millionrange-framingfrontier-indicolite.zip`


## Rev0994: bounded content-defined delta and shifted predecessor reuse

Rev0994 replaces the shipping fixed-boundary delta seam with one bounded
content-defined implementation. Fixed offsets made a small insertion near the
front of a large file shift every later block and collapse reuse. The new scalar
gear-hash boundary engine emits canonical variable chunks, forces a maximum
boundary, and rejects a bounded 8,192-record manifest frontier. Canonical
average sizes scale from 4 MiB to 1 GiB, covering the exact 4 TiB payload limit
without peer-selected geometry.

The payload store streams the selected rooted descriptor once, computes every
chunk SHA-256 and the whole-file SHA-256, and re-proves exact source metadata.
Reconciliation protocol generation 6 carries ordered chunk sizes and digests,
plus an exact manifest digest. A cache-cold receiver receives the complete
manifest; same-process continuations use a constant-size reference. The receiver
retains bounded cumulative offset vectors and may copy a SHA-256-and-size
matching predecessor chunk from a different absolute offset into the target's
durable prefix.

A deterministic 48 MiB regression inserts 256 KiB near the front and changes a
distant region. It proves at least four shifted chunks and at least 16 MiB are
reused while final bytes, whole-file identity, and causal evidence converge. The
superseded fixed-block payload projection and shipping vocabulary were removed,
leaving one current delta engine.

This is insertion-resilient delta, not measured multi-terabyte completion. It
does not yet provide cross-file chunk discovery, multilevel chunking,
compression, target-scale RSS and disk-amplification evidence, placeholders,
Android, rename/move identity, directory semantics, or ENOSPC qualification.
See `CONTENT_DEFINED_DELTA_AND_INSERTION_RESYNCHRONIZATION_AUDIT_rev0994.md`
and `REVISION_NOTES_rev0994.md`.

### Rev0994 validation

Exact rev0994 source completed a fresh 540-edge GCC 14.2 Debug graph and a no-work bundled-SQLite re-attestation; all 273/273 registered tests and all 44/44 product tests were accounted for across bounded terminal shards. Focused GCC proofs passed 39 content-defined-chunker, 650 payload-store, 4,955 reconciliation-protocol, 113 reconciliation-service, and 2,044 TLS-transport checks. Source audits passed 31/31 content-defined-delta, 27/27 manifest-reference, 33/33 targeted-source-access, 52/52 selective-sync, and 458/458 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 256/256 edges; all 44/44 product tests and the same five focused suites passed with leak detection and halt-on-error. The sanitizer folder-owner proof passed 536 checks with 1,686,160 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0993 parent SHA-256 matched a9ac6bd2a95c56061d4ea836725d3e5691f117e2887d415b4bb82c9964540504 and passed 41/41 checks under its sealed wrapper-aware verifier. The binary-aware source patch reconstructed all 29/29 changed project paths, all 26/26 changed active paths, and the complete 601-file active projection byte-for-byte and mode-for-mode. The active projection contains 601 files / 27,831,652 bytes with SHA-256 ec5931b9b28566148ffd8d053d22d88a07549ac39b52d1e22dffb66db21e07e7. Final directory, ZIP, CRC, path-policy, no-symlink, and clean-extraction equality checks remain mandatory publication gates.

Archive: `AnonSync-rev0994-2026.08.04.17.13-contentdefined-shiftedreuse-boundedmanifest-kyanite.zip`


## Rev0993: request-scoped targeted source access

Rev0993 removes a payload-namespace-scaled source-session owner from ordinary
reconciliation. Rev0992 retained one complete payload-store snapshot for the
life of every payload-bearing source session. Serving one selected file could
therefore enumerate, validate, and retain metadata for every current and
historical payload object. Worse, operation evidence may arrive before payload
bytes: a session that cached exact payload absence behind an unchanged evidence
digest could continue returning `PayloadUnavailable` after the bytes arrived,
until an unrelated reconnect discarded the stale snapshot.

Each payload-bearing request now creates one request-local targeted access and
opens only the selected SHA-256 basename under the current store identity and
rooted lease. Exact absence blocks only that operation. A later request on the
same authenticated session sees bytes that arrived without evidence churn.
Whole inline payloads are fully SHA-256 checked before advertisement; ranged
payloads build or reuse a manifest only after the selected descriptor's exact
canonical metadata is re-proved. Corrupt whole payload bytes enter the existing
typed integrity-fault path before receiver state changes.

The request scope is deliberate. An earlier draft retained targeted access in
the network session, but that capability can reopen every current payload and
therefore conservatively roots the complete payload namespace for retention.
The final implementation destroys access and descriptors before the service
returns, leaving only bounded manifest acceleration across requests. A runtime
negative control serves one valid digest while an unrelated invalid payload-root
entry makes the complete namespace scan fail, and then proves no targeted live
root survives the call.

This removes a real liveness defect and an O(retained-payload-count) source
traversal/memory multiplier. It is not a measured multi-terabyte peak-RSS claim,
namespace-health proof, content-defined delta, cross-file block discovery,
Android support, rename/move identity, placeholders, or ENOSPC qualification.
See `REQUEST_SCOPED_TARGETED_SOURCE_ACCESS_AUDIT_rev0993.md` and
`REVISION_NOTES_rev0993.md`.

### Rev0993 validation

Exact rev0993 source reached a no-work GCC 14.2 Debug complete graph across four bounded resumptions with no retained compiler or linker diagnostic; all 272/272 registered tests and all 43/43 independently replayed product tests were accounted for. Focused GCC proofs passed 644 payload-store, 119 reconciliation-service, and 2,044 TLS-transport checks. Source audits passed 42/42 fixed-block-delta, 52/52 selective-sync, 31/31 manifest-reference, 33/33 targeted-source-access, and 453/453 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 252/252 edges and all 43/43 product tests passed with leak detection and halt-on-error; focused sanitizer proofs passed the same 644, 119, and 2,044 checks, including the 536-check folder-owner proof in the product lane. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0992 parent SHA-256 matched 2e0c19129634200ea2c1e2575e3cdcb286b46257bea2f47993558ebfdcbbca93 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 14/14 changed active files and the complete 598-file projection byte-for-byte and by mode. The final active implementation projection contains 598 files / 27,812,299 bytes with SHA-256 3416936101fdc9cc2ae244bedaa39546575e9a3a52ae5c7c017fcc3d5f6af9ba. The final wrapper directory and ZIP passed release-package verification, CRC integrity, canonical-path and no-symlink checks, and clean-extraction path/byte/type/mode equality.

Archive: `AnonSync-rev0993-2026.08.04.15.02-requestscopedsource-liveavailability-retentionunroot-prehnite.zip`


## Rev0992: constant-size manifest continuations and retained delta index

Rev0992 removes two repeated fixed-block delta multipliers from the required
multi-terabyte Linux workflow. Reconciliation protocol generation 5 binds every
ranged payload to one canonical target-manifest digest. A cache-cold receiver
gets the complete bounded manifest; a same-process continuation advertises that
exact digest and receives only a constant-size reference. A restarted receiver
has no cache authority and automatically bootstraps the complete manifest again.
At the 4 TiB payload frontier, an uninterrupted 4 MiB range walk avoids
309,237,350,400 bytes—just under 288 GiB—of repeated digest-vector framing after
the first response, before counting optional-field and container overhead.

The receiver now keeps one exact target-manifest cache and one cohesive causal-
predecessor cache containing the predecessor manifest plus a digest-sorted index.
The index is built once per selected predecessor and reused by later block
boundaries instead of allocating and sorting 4,096 indices on every range. The
source still computes or reuses its own complete manifest and compares the exact
digest before honoring a receiver reference. The receiver requires its actual
process-local cache and validates every complete referenced block against the
retained target manifest before staging bytes. A negative regression changes
both wire bytes and their chunk digest and proves rejection leaves the durable
prefix unchanged.

The caches are bounded acceleration, not durable admission authority. This is
still fixed-block delta: insertion near the beginning of a large file may shift
boundaries and collapse reuse. Rev0992 does not claim content-defined chunking,
a measured multi-terabyte peak-RSS result, cross-file block discovery, Android,
rename/move identity, or ENOSPC qualification. See
`MANIFEST_REFERENCE_AND_DELTA_INDEX_CACHE_AUDIT_rev0992.md` and
`REVISION_NOTES_rev0992.md`.

### Rev0992 validation

Exact rev0992 source passed the GCC 14.2 Debug 340-edge rebuild to a no-work bundled-SQLite re-attestation, all 271/271 registered tests, and an independent 43/43 product replay. Focused GCC proofs passed 4,891 reconciliation-protocol, 109 reconciliation-service, and 2,044 TLS-transport checks. Source audits passed 42/42 fixed-block-delta, 52/52 selective-sync, 31/31 manifest-reference, and 448/448 structural-authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 252/252 edges; all 43/43 product tests passed with leak detection and halt-on-error. Focused sanitizer proofs passed 98 network-model checks plus 41 generated operations, 26 selective-policy, 4,891 protocol, 361 SQLite-owner, 238 prepared-publication, 536 folder-owner, 109 service, and 2,044 TLS checks; the folder-owner proof peaked at 1,689,104 KiB RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0991 parent SHA-256 matched ac2c873d6828d1421a7c0e637ba7efa49dce62f59e7f7dbcf8e9c40d1398016c and passed 41/41 wrapper-aware package checks. The final active implementation projection contains 597 files / 27,777,046 bytes with SHA-256 25a5beffcc7792c5a6a96e42e85803597a67f56d7eb6b67f0a617ad3397a565d.

Archive: `AnonSync-rev0992-2026.08.04.13.20-manifestreference-indexcache-restartbootstrap-sodalite.zip`


## Rev0991: targeted local publication and incremental replica witnesses

Rev0991 removes the complete-replica rebuild from the ordinary prepared local-file
publication path. Before this change, a 4,096-file observation segment against a
10,000-operation frontier admitted 8,192 complete model rebuilds and 81,920,000
prior operation-row decodes merely to publish new local files. That bound was not
credible for the intended multi-terabyte Linux workflow.

Replica SQLite schema v8 adds a canonical operation-path index, an exact visible-
path count, and fixed-width counted commutative witnesses for active operations,
complete retained evidence, and visible-path projections. Preparation now reads
one target path's history plus the active causal frontier. Commit re-proves the
same path, local actor chain, durable policy, schema, foreign-key mode, and absence
of executable TEMP triggers in one immediate transaction before applying bounded
metadata updates. Unrelated remote progress may advance concurrently; same-path
drift returns a stale cutpoint. A rare retained child that references the future
operation ID deliberately falls back to complete-model publication.

The adjacent audit corrected an idempotence defect in the first fast path. An
identical retry can return `AlreadyPublished` only while the retained operation is
still active and the local actor remains uncompromised. A same-dot fork that
quarantines the operation now makes the retry fail closed without changing durable
state. Fixed-width accumulator tests also cover exact modulo-2^256 carry and
borrow.

The normal complexity is O(history-of-that-path + active causal heads), not
O(total retained history) per local file. This is not constant memory, a
cryptographic set commitment, a measured multi-terabyte soak, rename/move
identity, Android support, or content-defined delta synchronization. The additive
witnesses are unkeyed structural evidence, not authentication authority; complete
reconstruction remains the acceptance oracle. No rev0990 archive is part of
release lineage. See
`TARGETED_LOCAL_PUBLICATION_AND_INCREMENTAL_REPLICA_WITNESS_AUDIT_rev0991.md`
and `REVISION_NOTES_rev0991.md`.

### Rev0991 validation

Exact rev0991 source passed the GCC 14.2 Debug complete graph across its 470-edge exact-change dependency state, followed by a no-work bundled-SQLite re-attestation, all 270/270 registered tests, and an independent 43/43 product replay. Focused GCC proofs passed 1,291 hash-graph, 238 prepared-publication, 361 SQLite-owner, and 536 folder-owner checks. Source audits passed 43/43 SQLite-owner, 30/30 targeted local-publication, and 442/442 structural authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 252/252 edges; all 43/43 product tests passed with leak detection and halt-on-error. Direct sanitizer proofs passed the same 1,291, 238, 361, and 536 checks; the folder-owner proof peaked at 1,688,812 KiB RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0989 parent SHA-256 matched 9af82eab8ce067088e65bf1ca165eb099967b72e18fde3660767454374a9387e and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 14/14 changed active files and the complete 596-file projection byte-for-byte and by mode. The final active implementation projection contains 596 files / 27,719,683 bytes with SHA-256 25888965fb9c560846cb528617655c38586f80dd9e27f2c3538baecb83f696b3. The final wrapper directory and ZIP passed release-package verification, CRC integrity, canonical-path and no-symlink checks, and clean-extraction path/byte/type/mode equality.

Archive: `AnonSync-rev0991-2026.08.04.11.50-countedwitness-targetedpublication-quarantinefence-spessartine.zip`


## Rev0989: targeted replica reproof for metadata-only scale

Rev0989 removes the remaining per-effect O(history) multiplier from the
metadata-only selective-sync path. Rev0988 made catalog reproof path-local, but
planning, pre-unlink, and post-unlink still took complete replica snapshots and
reconstructed the complete causal model. At 4,096 remote effects and 10,000
retained operation envelopes, that shape admitted 12,288 complete replica
snapshots and as many as 122,880,000 operation-row decodes in one pass.

The retained `SyncReplicaSqliteTargetedPathCutpoint` reads one typed metadata
row, at most two exact visible rows for a canonical path, the sole visible
operation when one exists, and at most one distinct retained catalog
predecessor. Two visible rows conservatively reject sole visibility without
allocating the conflict set. Exact and complete readers share one canonical
operation-row decoder. When target and predecessor are the same operation, one
owned envelope serves both roles instead of copying a potentially 4 MiB
canonical operation twice.

A successful rooted dematerialization now uses exactly three targeted replica
cutpoints, paired with the three targeted catalog cutpoints. No SQLite writer
transaction spans filesystem work. Descriptor-rooted observation, current
selection proof, private-payload retention, causal supersession, atomic
removal, full displaced-inode hashing, and final rooted absence proof remain
unchanged. Complete replica snapshots remain global planning and terminal
settlement authority.

The adjacent audit removed a more dangerous authority overclaim. The first
path-local result copied stored global generations and digests even though it
did not recompute the complete operation, evidence, visible, outbox, clock, or
pin sets. Those fields are gone. Each cutpoint instead re-attests the exact
trigger-free schema and foreign-key mode in its pinned read transaction and
exports only the operation rows it independently proves. Statement-traced
regressions prove one exact visible query, one or two operation primary-key
reads, one fixed schema proof, zero complete visible or operation projections,
and no history-dependent query shape. An eight-file folder regression proves
24 targeted reads while complete projections remain pass-bounded.

This is not a complete-replica shortcut or a target-scale memory result. It does
not prove unrelated paths or aggregate operation/evidence/outbox state, and it
does not replace full snapshots. The next product work should measure peak RSS,
initial sync, mutation catch-up, and disk amplification on a real multi-terabyte
Linux media tree, while advancing insertion-resilient delta and rename/move
identity. See
`TARGETED_REPLICA_PATH_OPERATION_CUTPOINT_AND_HISTORY_SCALE_AUDIT_rev0989.md`
and `REVISION_NOTES_rev0989.md`.

### Rev0989 validation

Exact rev0989 source passed the GCC 14.2 Debug complete graph in its 540-edge configured dependency state, followed by a no-work bundled-SQLite re-attestation, all 269/269 registered tests, and an independent 43/43 product replay. Focused GCC proofs passed 356 SQLite-owner checks and 536 folder-owner checks. Source audits passed 52/52 selective-sync checks, 24/24 targeted catalog-cutpoint checks, 30/30 targeted replica path-cutpoint checks, and 433/433 structural authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 251/251 edges; all 43/43 product tests passed with leak detection and halt-on-error, including direct 356-check SQLite-owner and 536-check folder-owner proofs. The sanitized folder-owner proof peaked at 1,664,276 KiB RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0988 parent SHA-256 matched 067de76a76061db941ebccde03821c84134428152784954a51feba153505d23d and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 13/13 changed active files and the complete 593-file projection byte-for-byte and by mode. The final active implementation projection contains 593 files / 27,588,416 bytes with SHA-256 195b1897e39b44b6f32d2838ee6eff35dc65849de7a3e2e70c6bb0882d43ea4a. The final wrapper directory and ZIP passed release-package verification, CRC integrity, canonical-path and no-symlink checks, and clean-extraction path/byte/type/mode equality.

Archive: `AnonSync-rev0989-2026.08.04.07.53-targetedreplica-historybounded-pathreproof-larimar.zip`


## Rev0988: targeted catalog reproof for metadata-only scale

Rev0988 removes a severe memory and allocation multiplier from the rev0987
metadata-only effect path. A successful dematerialization previously rebuilt the
complete folder catalog three times: during planning, immediately before rooted
unlink, and immediately afterward. The production composition permits 4,096
remote effects in one pass and 1,000,000 catalog paths, so that shape admitted
12,288 complete catalog projections in one pass. It was formally bounded but
not credible for the first supported multi-terabyte Linux workflow.

The retained implementation introduces one internal, transactionally pinned
`FolderCatalogPathCutpoint`. One deferred SQLite read transaction proves the
current folder identity, limits, catalog generation, selective-sync generation,
absence-fence generation, policy digest, and zero or one exact
`WHERE canonical_path=?` row. Complete and targeted readers now share one
current-format catalog-row decoder and validator. A successful rooted removal
uses exactly three path-local cutpoints; the complete catalog remains observed
only at pass-level planning and terminal settlement boundaries where global
contents and aggregate digest authority are actually required.

The folder-owner runtime oracle traces SQLite statements across eight files and
proves 24 exact path reads, three per successful effect, while complete catalog
projections remain pass-bounded. The shipping low-level and configured JSON
surfaces expose `remote_targeted_catalog_path_cutpoints` so the optimized path
is observable rather than implicit. Rooted descriptor proof, private payload
retention, sole-visible causal checks, atomic displacement, full displaced-inode
hashing, and final rooted absence proof remain unchanged.

This is a targeted catalog correction, not a global catalog shortcut. It does
not recompute the aggregate catalog digest or prove unrelated rows. The replica
SQLite owner also remains an explicit O(history) reference owner, so causal
state is still reconstituted around each successful effect. A transactionally
exact targeted replica path/operation cutpoint is the next clear per-effect
scaling seam. Rev0988 is not a measured million-path soak, content-defined
chunking, placeholders, automatic payload eviction, garbage collection, Android
support, or ENOSPC qualification. See
`TARGETED_CATALOG_PATH_CUTPOINT_AND_DEMATERIALIZATION_SCALE_AUDIT_rev0988.md`
and `REVISION_NOTES_rev0988.md`.

### Rev0988 validation

Exact rev0988 source passed the complete GCC 14.2 Debug graph in its 540-edge configured dependency state, including 261 exact-change rebuild edges and a no-work source re-attestation. The documentation-independent registry passed 266/266 tests; the finalized targeted-cutpoint and structural audits complete 268/268 registered-test accounting. The independent GCC product lane passed 43/43 tests in bounded exact-source invocations. Focused proofs passed 532 folder-owner checks, 52/52 selective-sync audit checks, 24/24 targeted catalog-cutpoint audit checks, and 425/425 structural authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 251/251 edges; all 43/43 product tests passed in bounded invocations with leak detection and halt-on-error. The direct sanitizer folder-owner proof passed 532 checks in 29.67 seconds at 1,668,096 KiB peak RSS. Aggregate inspection found no retained compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0987 parent SHA-256 matched 33680473e933ecf4e588eb24d8d90cf080002c256a2b4ed6408253424ded6d96 and passed 41/41 wrapper-aware package checks. The binary-aware patch reconstructed all 9/9 changed active files and the complete 592-file active projection byte-for-byte and mode-for-mode. That projection contains 27,537,575 bytes with SHA-256 d9d3383d821bb05d6c41b9610ec3cbe0bfaceec60ec0c968d4ea9fa430c759f9. The final wrapper directory and ZIP passed release-package verification, CRC integrity, canonical-path and no-symlink checks, and clean-extraction path/byte/type/mode equality.

Archive: `AnonSync-rev0988-2026.08.04.06.00-targetedcatalog-pathcutpoint-projectionfence-celestite.zip`


## Rev0987: bounded selective sync and safe rooted dematerialization

Rev0987 advances reconciliation to protocol generation 4 and implements the
first shipping selective-synchronization slice. One configured folder owns one
durable policy containing a default mode plus at most 1,024 canonical
longest-component-prefix rules and 48 KiB of rule path bytes. The policy is not
one row per synchronized path, and ordinary path and directory-pruning decisions
allocate no memory. Fully excluded subtrees are pruned before descendant
enumeration.

The owner-only offline commands are:

`anonsync_sync selective-sync-status --manifest ABSOLUTE_JSON`

`anonsync_sync selective-sync-set --manifest ABSOLUTE_JSON --default materialize|metadata_only [--rule MODE=CANONICAL_PATH ...]`

Both claim the deployment singleton and touch only the folder catalog. A
metadata-only file operation retains causal evidence but requests no payload and
publishes no rooted file. A later genuine expansion uses the ordinary
reconciliation and convergence engines to acquire and publish the missing bytes.

A newly excluded file that is already materialized can now be removed from the
synchronized root, but only while the exact catalog predecessor, unchanged
rooted descriptor, current sole-visible causal target, current selection, and an
independently verified immutable private payload copy all remain valid. A
second complete SHA-256 pass over the atomically displaced private inode must
also remain under one exact POSIX observation immediately before unlink. Failed
byte or observation proof restores the displaced object when possible. A
changed, untracked, conflicted, or only-copy path is preserved and reported as
unresolved. No tombstone is minted. Rooted removals obey the ordinary bounded
remote-operation cursor. This reclaims synchronized-root space, not total
AnonSync storage: the private payload is intentionally retained. The first
implementation pays a second complete file read before unlink, and a crash in
the narrow post-displacement window can leave a reserved private recovery
artifact; its bytes are preserved, but automatic residue recovery is not yet
implemented.

The durable absence fence now opens only for a real materialization expansion.
Pure narrowing no longer stalls deletion repair for unrelated selected paths. A
reselected absent path may materialize either its cataloged head or a current
causal successor learned while excluded, under the exact expansion fence. Local
scan publication, direct remote apply, and historical restore all re-prove the
selection generation and digest so stale in-flight work cannot rematerialize an
excluded path.

The adjacent audit corrected an allocation-free lexical bug: lower-bounding on
`directory` could stop at an unrelated sibling such as `directory-archive`
before reaching `directory/keep`. The retained comparator searches for the
virtual `directory/` key without allocating it, and an adversarial regression
binds that ordering. A bounded exhaustive oracle also compares every pair of
the 486 policies over a focused nested-prefix basis against direct path
semantics.

This is not a placeholder filesystem, automatic payload eviction, quota policy,
garbage collector, Android adapter, or completed Resilio user experience. The
first target remains Linux/headless multi-terabyte media synchronization with
mandatory delta transfer and selective sync. Target-scale RSS and disk behavior
still require a real soak. See
`BOUNDED_SELECTIVE_SYNC_AND_DEMATERIALIZATION_AUDIT_rev0987.md` and
`REVISION_NOTES_rev0987.md`.

### Rev0987 validation

Exact rev0987 source passed a fresh GCC 14.2 Debug complete graph (540/540 configured build edges), 265/265 documentation-independent tests plus the finalized selective-sync and structural audits for complete 267/267 registered-test accounting, and an independent 43/43 GCC product replay. Focused GCC proofs passed 26 selective-policy, 18/18 conditional-unlink-authority, 644 payload-store, 4,861 reconciliation-protocol, 106 reconciliation-service, 518 folder-owner, 2,043 TLS-transport, and 110 sync-once checks. Source audits passed 52/52 selective-sync, 43/43 atomic-publication, 42/42 fixed-block-delta, and 420/420 structural payload-store authority checks. A fresh Clang 17 Debug product graph completed 251/251 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 43/43 product tests passed in bounded exact-source invocations with leak detection and halt-on-error. Focused sanitizer proofs passed the same 26, 18, 644, 4,861, 106, 518, 2,043, and 110 checks; the folder-owner proof peaked at 1,649,884 KiB RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0986 parent SHA-256 matched 00eca1b35b4072365aac651717506a4d02f6ea9593124151c18af99de0d8c3c3 and passed 41/41 wrapper-aware package checks. The binary-aware patch reconstructed all 31/31 changed active files and the complete 591-file projection byte-for-byte and by mode. The final active implementation projection contains 591 files / 27,507,720 bytes with SHA-256 307fe1ce3827c871ffe3dfdc3f9c4ac477fbad1b205dfb6ef986ac3fccd2f59f. The final wrapper directory and ZIP remain publication-gated on the exact manifest, package verification, CRC integrity, canonical paths, absence of symlinks, and clean-extraction path/byte/type/mode equality.

Archive: `AnonSync-rev0987-2026.08.04.03.36-selectivepolicy-rooteddematerialization-expansionfence-dioptase.zip`


## Rev0986: bounded fixed-block delta and multi-terabyte capacity

Rev0986 moves the shipping reconciliation path to protocol generation 3 and
implements AnonSync's first production delta transfer. Every ranged payload
carries one complete canonical fixed-block manifest. Blocks begin at 4 MiB and
double only as needed to keep one active file at or below 4,096 SHA-256 hashes;
the largest canonical block is 1 GiB and the complete-file frontier is 4 TiB.
Whole-file payloads carry no redundant manifest.

The receiver considers only exact retained direct causal predecessors for the
same canonical path. A usable predecessor is opened through the existing
rooted targeted payload-store authority, hashed once into the bounded block
projection, and cached across continuation pages for the current target. Each
matching block is reopened and copied through bounded ranges into the existing
crash-safe contiguous prefix. Ordinary network transfer resumes at the first
miss. The complete reconstructed whole-file SHA-256 must become durable before
remote operation metadata is admitted.

The focused 12 MiB regression makes the product gain concrete. A one-byte edit
transmits one 4 MiB block and reuses the remaining 8 MiB locally. Another
successor spanning two network pages proves that both the source and receiver
hash their active manifests once rather than once per range. TLS and shipping
JSON report network staging, locally reused blocks/ranges/bytes, and source and
predecessor manifest scan/reuse/hashed-byte work.

The adjacent capacity audit found that the old 4 GiB deployment ceiling and
64 GiB aggregate payload-store ceiling made a multi-terabyte media tree
structurally impossible despite bounded streaming. New deployments default to
64 GiB per file and may select up to 4 TiB. The production aggregate uses 8 PiB
minus one as an exact comparison frontier. It is not a quota, preallocation, or
disk reservation; wire buffers remain bounded and no container is sized from
that value. The explicit 100,000 retained-payload identity ceiling and real
filesystem/free-space limits still apply.

This is fixed-block delta, not content-defined chunking. Insertions can shift
later boundaries and destroy reuse, and the receiver does not search all
historical versions for an optimal source. Protocol generations 2 and 3 require
both peers to upgrade together.

The first supported workflow is now Linux/headless synchronization of large
media trees measured in terabytes. Delta transfer and selective synchronization
are mandatory. Rev0986 implements the first; **selective sync is the next
existential product slice**. Android compatibility remains desirable but is not
claimed. A Termux or app-private-storage experiment may validate the portable
C++ core, while a supported Android app still needs explicit storage and
lifecycle adapters. Credentials and keys remain operator-owned and outside
AnonSync backup authority. See
`FIXED_BLOCK_DELTA_AND_MULTI_TERABYTE_CAPACITY_AUDIT_rev0986.md` and
`REVISION_NOTES_rev0986.md`.

### Rev0986 validation

Exact rev0986 source passed a fresh GCC 14.2 Debug complete graph (536/536 configured build edges), 264/264 documentation-independent tests plus the finalized fixed-block delta audit for complete 265/265 registered-test accounting, and an independent 42/42 GCC product replay. Focused GCC proofs passed 30 deployment-manifest, 4,638 reconciliation-protocol, 644 payload-store, 99 reconciliation-service, 2,043 TLS-transport, 470 folder-owner, and 110 sync-once checks. Source audits passed 42/42 fixed-block delta and multi-terabyte capacity checks, 41/41 database-replacement checks, and 412/412 structural payload-store authority checks. A fresh Clang 17 Debug product dependency graph completed 247/247 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 42/42 product tests passed in bounded exact-source invocations with leak detection and halt-on-error. Focused sanitizer proofs passed the same 4,638 protocol, 644 payload-store, 99 reconciliation-service, 2,043 TLS, and 470 folder-owner checks; the folder-owner proof peaked at 1,485,264 KiB RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0985 parent SHA-256 matched a87f6fcd1f7ea371e0974c4b89ca097def56e07301bc3ffeb9cbe19bdf496c4c and passed 41/41 wrapper-aware package checks. The binary-aware patch reconstructed all 23/23 changed active files and the complete 587-file projection byte-for-byte and by mode. The final active implementation projection contains 587 files / 27,271,627 bytes with SHA-256 7c706289c0b0e26d28a42d9b6c486a148044ab92c13a6cb0757696f038fbe1e2.

Archive: `AnonSync-rev0986-2026.08.03.20.41-fixedblockdelta-multiterabyte-memoryfrontier-azurite.zip`


## Rev0985: role-bound offline database artifacts

Rev0985 extends the released immutable database backup owner to all five
manifest-selected SQLite authorities:

`anonsync_sync database-backup-create --manifest ABSOLUTE_JSON --snapshot ABSOLUTE_SQLITE --role replica|file-effect|tls-membership|tls-membership-anchor|folder-catalog`

`anonsync_sync database-backup-inspect --manifest ABSOLUTE_JSON --snapshot ABSOLUTE_SQLITE --role replica|file-effect|tls-membership|tls-membership-anchor|folder-catalog`

Omitting `--role` preserves the exact v1 primary-replica behavior. Explicit
roles use v2 responses. Every role reuses the same deployment singleton,
transactionally pinned bounded SQLite copy, exact source bracket, create-new
mode-0600 publication, sidecar denial, resident seal, and independent durable
reopening. An explicit replica artifact remains accepted by the v1 inspector
and existing replacement ceremony; file-effect, membership, anchor, and catalog
artifacts are inspection-only.

The adjacent refactor adds a distinct filename-free forensic read-only SQLite
profile. SQLite deserialized with `SQLITE_DESERIALIZE_READONLY` may not report
`sqlite3_db_readonly() == 1`, so named readers retain that native gate while
detached images are proved through an unnamed/query-only/MEMORY-journal profile,
sealed bytes, and behavioral write denial. File-effect and folder-catalog
inspection also validates persisted canonical root identity without opening the
configured synchronized tree.

This is **not a complete-share backup**. The five images have no cross-database
atomic cutpoint, and the set contains no payload bytes, credentials, or
configuration. It is a bounded prerequisite for a backup-set and recovery model
that can state exactly what was captured together and what partial recovery
means. See `ROLE_BOUND_OFFLINE_DATABASE_BACKUP_AUDIT_rev0985.md` and
`REVISION_NOTES_rev0985.md`.

### Rev0985 validation

Exact rev0985 source passed the fresh GCC 14.2 Debug complete graph (536/536 configured build edges), all 264/264 registered tests in indexed final-source accounting, and an independent 42/42 product replay. Focused GCC proofs passed 108 file-effect SQLite-owner checks, 470 folder-owner checks, the existing 598-check database backup/recovery/replacement process oracle, and the new 699-check five-role backup oracle. Source audits passed 28/28 original backup checks, 31/31 role-bound backup checks, 39/39 TLS-membership profile checks, and 412/412 structural authority checks. A fresh Clang 17 Debug product dependency graph completed 247/247 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 42/42 product tests passed with leak detection and halt-on-error, including the direct 470-check folder-owner proof at 1,479,148 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0984 parent SHA-256 matched 0dcadb3e3bd4aa620e80e39ba009b9bdbbf89686b638c61c2e1fc4db961cd664 and passed 41/41 wrapper-aware package checks. The final active implementation projection contains 585 files / 27,187,739 bytes with SHA-256 ec2072db6a95736b907e8363844ac46cad7550c78433af2f9f0d359c4a9fdeb6.

Archive: `AnonSync-rev0985-2026.08.03.18.23-roleboundbackup-detachedprofile-sharerecoverymap-orthoclase.zip`


## Rev0984: immutable receipt and exact database-replacement resume

Rev0984 closes the bounded offline crash window left by rev0983. The supported
command is now:

`anonsync_sync database-recovery-replace --manifest ABSOLUTE_JSON --snapshot ABSOLUTE_SQLITE --rollback ABSOLUTE_SQLITE --receipt ABSOLUTE_RECEIPT --expected-current v1:INCARNATION:EPOCH:CUTPOINT`

Before the first rollback or database effect, the owner publishes one bounded,
private, checksum-framed, create-new receipt. It binds the deployment, the exact
selected paths by SHA-256 digest, the original operator-approved database
expectation, and complete candidate and rollback artifact observations. The
receipt is immutable evidence, not a mutable progress journal and not effect
authority.

Restart progress is classified from the active database itself. Exactly three
states are admitted: the displaced database is still current; the candidate is
installed but its recovery epoch is pending; or the candidate's exact recovery
successor is current. The owner performs only the missing effects. A completed
replay is mutation-free, a candidate-installed replay advances only the epoch,
and a receipt-only replay can recreate the rollback only while the exact
displaced database remains current. Any other state fails closed as unknown
continuity.

The adjacent refactor centralizes exact optional-file absence handling for both
receipt and rollback paths and releases the complete resident displaced image
before reopening the durable rollback. This removes duplicated `ENOENT`
classification and avoids an unnecessary three-database-image memory peak.

The final success cutpoint no longer treats retained resident images as proof of
the selected candidate and rollback pathnames. After the writable database is
closed, the owner proves the final database, releases the resident candidate and
rollback images, independently recaptures and fully re-attests each pathname one
at a time against the immutable receipt, re-proves the receipt, and then proves
the exact final database again. This brackets the potentially long artifact reads
without increasing the two-image peak. The response advances to
`anonsync.local-database-recovery-replacement.response.v3` and explicitly states
that these observations are not a continuous reservation against a noncooperating
same-UID writer.

The audit also found a terminal-liveness defect at integer exhaustion. A candidate
whose recovery epoch or state generation is already `UINT64_MAX` has no possible
mandatory recovery successor. Rev0984 rejects that shape immediately after full
candidate validation and before publishing a new receipt, rollback, or database
effect, rather than admitting an immutable action that can never finish.

The real process oracle independently recomputes the explicit-NUL action and
record digests, rejects damaged/nonprivate/hard-linked receipts, and reconstructs
receipt-only, candidate-installed, completed, and unknown-continuity cutpoints.
See `IMMUTABLE_DATABASE_REPLACEMENT_RECEIPT_AUDIT_rev0984.md` and
`REVISION_NOTES_rev0984.md`.

### Rev0984 validation

Exact rev0984 active source passed a fresh GCC 14.2 Debug graph (536/536 configured build edges), all 262/262 registered tests in an indexed final-source replay (261/261 immutable-preseal tests plus the final documentation-sensitive structural audit), and an independent 41/41 product replay. Focused GCC proofs passed 334 SQLite-owner checks, 38 deployment-binding checks, 102 snapshot-seal checks, 53 SQLite live-backup/replacement checks, 470 folder-owner checks, and the shipping database backup, recovery, replacement, and restart oracle passed 598 checks. Source audits passed 24/24 bounded-reader checks, 41/41 database-replacement checks, and 404/404 structural authority checks. A fresh Clang 17 Debug product dependency graph completed 247/247 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 41/41 product tests passed with leak detection and halt-on-error, including the direct 470-check folder-owner proof at 1,481,008 KiB peak RSS, and focused sanitized proofs passed the same 334, 38, 102, and 53 checks. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0983 parent SHA-256 matched 64ef96593d809861275fe7b9ec5fbf67554a25c23b6e543de70cfe9fd59519b6 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 12/12 changed active files and the complete 583-file projection byte-for-byte and by mode. The final active implementation projection contains 583 files / 27,098,385 bytes with SHA-256 48c4b04bb58f482b3dc8dc853ba951d78941ccbea552ddbb3e442a0b2ede2419. Validation excluded overlapping Ninja invocations, vanished build trees, divergent source authorities, interrupted nonterminal runs, and every result not bound to the frozen exact C++ source or the final prose-and-audit seal. The final wrapper directory and ZIP remain publication-gated on the exact manifest, package verification, CRC integrity, canonical paths, absence of symlinks, and clean-extraction path/byte/type/mode equality.

Archive: `AnonSync-rev0984-2026.08.03.12.22-receiptresume-pathreproof-successorfence-grandidierite.zip`


## Rev0982: canonical replica-database backup and detached reproof

Rev0982 adds the artifact half of the supported database-recovery runbook.
`anonsync_sync database-backup-create --manifest ... --snapshot ...` claims the
same deployment singleton as the retained service and recovery commands,
brackets one transactionally pinned SQLite copy with exact source observations,
canonicalizes a standalone rollback-journal image, and publishes it create-new
at mode 0600. The destination cannot collide with the manifest, an active
SQLite family, payload storage, or synchronized files.

`anonsync_sync database-backup-inspect --manifest ... --snapshot ...` can
inspect the detached artifact while the live primary database family is absent.
The manifest is required because it supplies the exact deployment, database-
role, normalized source-path, folder, and actor authority against which the
artifact binding is attested. Inspection verifies one single-linked sidecar-free
regular file, bounded page geometry,
SHA-256, schema v7, complete causal cutpoint, and an actual denied write. The
create path closes its source, reopens the published bytes, and repeats those
proofs independently.

The adjacent audit corrected two implementation drags. First, SQLite reports a
read-only deserialized in-memory image as writable through
`sqlite3_db_readonly()`, so detached images now prove filename-free MEMORY
journaling, `query_only`, and real `SQLITE_READONLY` denial instead of trusting
that misleading introspection result. Second, the initial probe issued raw
savepoint SQL beside the typed transaction owner. The final probe receives the
outer `SyncSqliteTransactionAuthority`, uses one nested `SyncSqliteSavepoint`,
rolls it back before interpreting the write result, and leaves no raw
savepoint-transition literals in production deployment-binding code.

The memory audit also stopped retaining several complete causal/outbox graphs
beside the resident artifact. Each full source observation is restored and
validated, then reduced immediately to a compact exact lineage/cutpoint
witness. The 512 MiB artifact ceiling remains a bounded resident-input limit,
not a streaming or total-RSS claim.

The sanitizer product replay then exposed an adjacent service-lifecycle defect.
After sending a valid drain response, the daemon may complete shutdown and
unlink its owner-only Unix socket before the client performs its final pathname
reproof. The client had reported that successful drain as failure. The final
client policy is command-specific: only a validated `stop` response may be
followed by exact `ENOENT`; a surviving pathname must still be the original
mode-0600 socket, malformed stop responses still fail, and status, recheck,
quarantine, history, restore, and retention operations retain the strict final
identity requirement. A deterministic one-shot server regression proves the
positive stop race and the malformed-stop and non-stop negative controls.

This is not a whole-share backup or restore command. The artifact excludes
payload bytes, the folder catalog, TLS membership and anchor databases, effect
receipts, rooted files, network state, and retention-mark age. A restore still
requires offline rollback-preserving database-family replacement followed by
`database-recovery-advance`; unknown continuity still resets retention age, and
SQLite lineage is not an external anti-rollback anchor. See
`OFFLINE_REPLICA_DATABASE_BACKUP_ARTIFACT_AUDIT_rev0982.md` and
`REVISION_NOTES_rev0982.md`.

### Rev0982 validation

Exact rev0982 active source passed a fresh GCC 14.2 Debug graph (534/534 configured build edges), all 261/261 registered tests after final release-prose sealing, and an independent 41/41 product replay. Focused proofs passed 334 SQLite-owner checks, 38 deployment-binding checks, and the 265-check database backup/recovery process oracle. Source audits passed 27/27 deployment-binding checks, 100/100 transaction-stack authority checks, 27/27 backup checks, and 393/393 final structural authority checks. A fresh Clang 17 Debug product dependency graph completed 245/245 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 41/41 product tests were accounted for in bounded fresh invocations with leak detection and halt-on-error, and focused sanitized proofs passed the same 334 and 38 checks. Aggregate authoritative-log inspection retained no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0981 parent SHA-256 matched 1f27e580cae7e25d5b0f55df14688ff975e4e3b88f103a96e36f47421716b934 and passed 41/41 wrapper-aware package checks. The binary-aware patch reconstructed all 17 changed active files and the complete 577-file projection byte-for-byte and by mode. The final active implementation projection contains 577 files / 26,906,635 bytes with SHA-256 3e15ca2ba0f24c68b808290b11d64e0cd8b3d5b05c99eca5a7be358a988faaf4. Validation excluded the raw-savepoint prototype, source-divergent workers, vanished build trees, stale caches, and interrupted runs without terminal evidence.

Archive: `AnonSync-rev0982-2026.08.02.23.59-backupartifact-detachedverify-recoverybridge-scapolite.zip`


## Rev0981: offline database recovery and one deployment owner

Rev0981 turns rev0980's internal recovery-epoch transition into an exact
operator workflow. `anonsync_sync database-recovery-inspect --manifest ...`
opens the current primary replica database through the descriptor-rooted
read-only VFS, attests its deployment binding, requires schema v7, and emits one
canonical `v1:INCARNATION:EPOCH:CUTPOINT` expectation. Inspection cannot create,
initialize, migrate, checkpoint, or write the SQLite family.

`anonsync_sync database-recovery-advance --manifest ... --expected ...`
first repeats the exact forensic observation. Malformed, stale, or consumed
tokens are rejected before writable SQLite authority is opened, so rejection
cannot trigger WAL recovery, sidecar creation, checkpointing, migration, or
another writer effect. An accepted token is then independently re-proved under
the existing `BEGIN IMMEDIATE` recovery transition. It advances database
recovery epoch and state generation once, preserves every causal, evidence,
visible, outbox, clock, policy, limit, and historical-pin fact, and publishes
one successor cutpoint.

The adjacent lifecycle audit found that `anonsync_sync once` did not share the
retained service's per-deployment singleton. It now acquires that owner before
route, TLS, peer, folder, or network authority. Retained service, one-shot sync,
read-only inspection, and recovery advance therefore cannot overlap one valid
deployment. Manifest-to-primary-database targeting and durable role binding are
centralized in shared writer and read-only seams. A real-process negative
control supplies an absent native-I2P private-destination path and proves that
exact deployment ownership wins before route parsing can open key material.

The first read-only refactor exposed and corrected a WAL ordering defect:
connection-local exclusive locking and the hardened query-only profile must be
selected before the first schema page read, otherwise a read-only observer can
attempt to join or create persistent `-shm`. The process oracle fingerprints
all SQLite family bytes across inspection, hides payload/files/catalog roots,
rejects malformed and stale expectations while fingerprinting the exact
SQLite family before and after every rejection, advances once, rejects token
reuse before writable open, and proves every non-lineage ordinary status field
is preserved. The recovery result is fully materialized before `COMMIT` and is
required to move without throwing, removing one avoidable post-commit
allocation failure. Terminal output is still not a durable receipt: after an
unknown command completion, fresh inspection is authoritative.

This remains in-database continuity only. Exact whole-image rollback restores
its older incarnation and epoch; no backup validation, file replacement,
external monotonic anchor, trusted time, retention-age reset, collection,
reclaim, rename, or unlink is added. See
`OFFLINE_DATABASE_RECOVERY_AND_DEPLOYMENT_SINGLETON_AUDIT_rev0981.md` and
`REVISION_NOTES_rev0981.md`.

### Rev0981 validation

Exact rev0981 active source passed a fresh GCC 14.2 Debug graph (532/532 configured build edges), all 260/260 registered tests after final release-prose sealing, and an independent 41/41 product replay. The 105-check real-process recovery oracle proved descriptor-rooted read-only inspection, byte-for-byte SQLite-family preservation for malformed and stale expectations, exact one-step advancement, consumed-token rejection before writable open, narrow authority, and deployment-singleton ordering. The database-open policy audit passed 48/48 checks and the structural authority audit passed 385/385 checks. A fresh Clang 17 Debug product dependency graph completed 243/243 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 41/41 product tests passed serially with leak detection and halt-on-error. Aggregate authoritative-log inspection retained no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0980 parent SHA-256 matched 0fc470ab43ce97374e1a562f9c2c275b18bbc6f4e3f8c27127711ed7b18ca40d and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 14/14 changed active files and the complete 574-file projection byte-for-byte and by mode. The final active implementation projection contains 574 files / 26,812,446 bytes with SHA-256 d399a8ad3f077bf3467752e4355933be71117cdfff0f4cd789cd0cfd445f1b16. Validation was rerun from the reconstructed exact source after the cloudtainer removed prior unsealed worktrees; all vanished, interrupted, stale-cache, and source-divergent results were excluded. The final wrapper directory and ZIP are publication-gated on 41/41 package checks, CRC integrity, canonical paths, absence of symlinks, and clean-extraction path/byte/type/mode equality.

## Rev0980: database incarnation, recovery epoch, and retention witness

Rev0980 closes a cross-database retention-authority alias. Two independently
created SQLite replica databases can contain identical operations, evidence,
pins, visible state, payload roots, and `state_generation`; rev0979 could
therefore give both the same restart-stable candidate witness over one payload
store. Schema v7 now mints a CSPRNG-derived database incarnation and starts a
nonzero recovery epoch. Both participate in the exact SQLite cutpoint and in
every retention candidate, writer-fenced page, and deletion-free-mark digest.

The exact released v6 schema remains embedded as a migration oracle. Migration
restores and attests all causal, outbox, clock, policy, limit, and historical-pin
authority before minting the v7 lineage, advancing state generation once, and
committing one successor cutpoint. An explicit
`advance_database_recovery_epoch_or_throw` transaction lets a recovery workflow
invalidate all prior same-incarnation evidence while preserving every other
database fact. It requires the exact current incarnation, epoch, and cutpoint.

Retention-plan and mark requests now carry incarnation, recovery epoch, and
state generation. The restart-stable candidate witness advances to v2, the
writer-fenced page digest to v2, and the deletion-free mark digest to v5. The
fixed-width retention record remains unchanged: its opaque candidate witness
transitively binds the new lineage. Foreign-database and stale-pre-recovery
requests fail at `retention_mark_publication` before payload observation. Live
and terminal status advance to `anonsync.peer-service.status.v24`; the local
retention response advances to `anonsync.local-retention-plan.response.v6`.

This is not external anti-rollback authority. Exact whole-database rollback also
restores the incarnation and epoch. A future destructive feature must use an
external monotonic anchor, require the recovery workflow to advance the epoch,
or conservatively reset all mark age when continuity is uncertain. Rev0980
remains deletion-free and adds no trusted clock, quota decision, collection
quarantine, reclaim, rename, or unlink. See
`REPLICA_DATABASE_LINEAGE_AND_RETENTION_WITNESS_AUDIT_rev0980.md` and
`REVISION_NOTES_rev0980.md`.

### Rev0980 validation

Exact rev0980 C++ source passed a clean GCC 14.2 Debug graph (532/532 configured build edges), all 259/259 registered tests in an uninterrupted serial replay in 123.72 seconds, and an independent 40/40 GCC product replay in 67.12 seconds. The finalized source audits passed 43/43 SQLite-owner checks and 372/372 structural authority checks. Focused exact-source suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 30 retention-mark, 640 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 334 SQLite-owner, 470 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 158 local-control, 87/87 observer, and 6/6 observer-race checks. A clean Clang 17 Debug product dependency graph completed 243/243 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 40/40 product tests passed serially in 122.76 seconds with leak detection and halt-on-error. Focused sanitizer proof passed the 640-check payload-store suite in 16.57 seconds at 514,388 KiB peak RSS, the 470-check folder-owner suite in 21.90 seconds at 1,467,012 KiB peak RSS, and the 158-check local-control suite in 1.12 seconds at 106,900 KiB peak RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0979 parent SHA-256 matched 5fc1ee63e991a261b9473f7a80887eb2b010e5d6167dc09405dba20fb779f58f and passed 41/41 wrapper-aware package checks. Validation excluded the divergent local-control prototype, vanished or interrupted build caches, source-divergent workers, the superseded v6-only SQLite audit oracle, duplicate validators, and every result not bound to the reconstructed schema-v7 source. The binary-aware source patch reconstructed all 16/16 changed active files and the complete 573-file projection byte-for-byte and by mode. The final active implementation projection contains 573 files / 26,745,576 bytes with SHA-256 c3b2f86e2a279e4114a546260c4010af75030ae5cf03657beb5371f55405248f.

## Rev0979: durable deletion-free retention mark and ABA fence

Rev0979 persists the restart-stable retention witness introduced in rev0978.
One fixed-width, checksum-framed
`.anonsync-payload-retention-mark-v1` record binds the exact immutable
payload-store identity, its private single-link identity inode, the complete
operation/evidence/pin/visible/payload/transient cutpoint, the full unreferenced
candidate-set digest and cardinality, and explicit bounded grace and future
collection count/byte frontiers. The record deliberately contains no reclaim,
quarantine, rename, or unlink authority.

Publication is part of the existing retention-planner authority path rather
than a second scanner. The folder owner recomputes the complete candidate
witness under the existing store-global exclusive identity lease and moves that
exact writer-fenced snapshot into the payload-store publisher. The publisher
accepts only a snapshot from the exact retained owner, overwrites identity and
generation fields, atomically creates or exact-metadata-replaces the record,
reopens the committed bytes, compares the full record and checksum, and re-
proves the writer fence and rooted identity. The mark is excluded from payload
and transient digests so publishing metadata cannot invalidate the physical
cutpoint it records.

The adjacent capacity audit moved store-specific policy validation ahead of
that expensive path. Candidate count and byte frontiers which exceed the exact
configured payload-store limits now fail before the owner acquires the writer
fence or enumerates one payload. A regression holds an independent exclusive
lock on the exact identity inode while submitting both impossible policies and
proves that neither a durable mark nor payload/transient namespace state
changes.

SQLite `state_generation` closes a causal ABA within one retained database
lineage that content digests alone cannot see. Removing and restoring the same
historical pin can return all source digests and the candidate witness to their
prior values, but ordinary forward mutation cannot return the owner generation.
Old mark requests fail at typed stage `retention_mark_publication`. If a
concurrent source change occurs after the atomic record commits, the method
still fails; the record remains visible but its earlier forward-lineage
generation makes it conservative stale evidence rather than an inherited grace
interval.

That generation is not an external anti-rollback counter. Restoring an exact
older replica-database image can recreate both generation and source digests,
and the mark's own replacement generation restarts at one after absent or
unusable evidence. Rev0979 remains safe because no collector consumes the mark.
A future destructive operation must bind a separately attested
replica-database incarnation or recovery epoch, or reset all prior mark age
after database replacement or rollback.

The adjacent API audit added `retention_mark_observation_known()`. A synchronized
writable scan can now distinguish clean absence from damaged or stale evidence,
while `ReadOnlyInspect` remains byte-cold and reports only basename presence.
Malformed or wrong-size records are recognized internal metadata but grant no
authority. Fresh product bootstrap refuses to adopt a pre-existing mark.

This is still deletion-free. The supplied Unix time is historical operator
evidence, not a trusted elapsed-time proof. There is no owner CLI, quota or
ENOSPC decision, per-version age selection, collection quarantine,
collection-time restart byte proof, or unlink. A future collector must reacquire
every current causal,
transient, live-capability, exact-inode, byte, root, clock, and policy cutpoint.
See `DURABLE_PAYLOAD_RETENTION_MARK_AND_POLICY_AUDIT_rev0979.md` and
`REVISION_NOTES_rev0979.md`.

### Rev0979 validation

Exact rev0979 C++ source passed a clean GCC 14.2 Debug graph (532/532 configured build edges), 258/258 preseal registered runtime tests, and an independent 40/40 GCC product replay in 114.17 seconds. The finalized registered structural authority audit passed 362/362 checks, accounting for all 259/259 registered tests across the unchanged C++ bytes and final release prose. Focused exact-source suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 30 retention-mark, 640 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 320 SQLite-owner, 463 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 158 local-control, 87/87 observer, and 6/6 observer-race checks. A clean Clang 17 Debug product dependency graph completed 243/243 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 40/40 product tests passed serially in 155.48 seconds with leak detection and halt-on-error. Focused sanitizer proof passed the 640-check payload-store suite in 11.33 seconds at 514,824 KiB peak RSS, the 463-check folder-owner suite in 37.23 seconds at 1,467,772 KiB peak RSS, and the 158-check local-control suite in 0.68 seconds at 113,860 KiB peak RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0978 parent SHA-256 matched 5d8c9bc1470f3c7bcd38ed039dc69d766bc1ff9fdddba1ee4ef9de49a045d734 and passed 41/41 wrapper-aware package checks. Validation excluded source-divergent retention prototypes, shared-cache and in-tree build contamination, self-restarting mutable-source launchers, interrupted rev0979-named sanitizer processes, and every result not bound to the byte-reconciled clean source. The binary-aware source patch reconstructed all 13/13 changed active files and the complete 573-file projection byte-for-byte and by mode. The final active implementation projection contains 573 files / 26,681,569 bytes with SHA-256 7ef1c72b253f25a8e8fb1154aafbc4ce0220891b4de7eebef6ce139eb76e7f7b.

## Rev0978: process-store live roots and writer-fenced retention observation

Rev0978 closes two deletion-free gaps between the exact retention projection and
future collection authority. First, independently opened
`SyncReplicaFilePayloadStore` owners over the same descriptor-attested root and
immutable store identity now share one bounded process-store live-capability
registry. Snapshots, opened payload descriptors, targeted accessors, and
mutation batches from either owner appear in the same canonical cutpoint. The
last capability keeps the scope alive; after final release and later reopening,
a fresh non-durable incarnation prevents an old same-process mark from silently
crossing the lifetime break. This composition does not weaken byte-integrity
authority: snapshot handoff still requires the issuing owner's exact
verification cache, integrity epoch, rooted authority, limits, and live
registration.

Second, the retention planner now obtains its complete physical payload
snapshot under the existing store-global exclusive identity lease and retains
that exact lease through the physical/reference merge, page-bounded exact-inode
payload-use probes, final SQLite cutpoints, rooted identity reproof, and the
final process-store capability cutpoint. The allocation-heavy causal operation
projection and canonical sort happen before the exclusive lease, reducing the
period in which ordinary synchronization is excluded. Each returned physical
object not named by a retained File operation is then reported as
`exclusive_available_at_cutpoint` or `busy_at_cutpoint` under the exact inode
lease protocol. A busy result is evidence, not an error; an available result is
still not reclaim authority.

The logical retention page remains bounded to 1,024 entries. The independent
status-byte frontier may serialize only a canonical prefix, so status now
reports `writer_fenced_candidate_page_entry_count` separately from the visible
entry array. The page digest and candidate-probe partition bind the complete
logical page even when presentation truncates it.

The page-invariant deletion-free mark advances to domain v4 and binds the exact
process-store incarnation and live set. A separate
`durable_candidate_witness_digest` binds the durable causal, payload, transient,
and complete candidate-set cutpoints without claiming persistence. Live and
terminal status advance to `anonsync.peer-service.status.v23`; the owner-only
retention response advances to
`anonsync.local-retention-plan.response.v5`.

The adjacent audit removed an unsealed standalone retention-mark codec and test
target that had no shipping persistence owner, policy consumer, recovery path,
or collection operation. Keeping it would have added a second ceremonial
format without closing a product boundary. Rev0978 instead strengthens the
existing planner and leaves durable mark-plus-policy design to the first slice
that can consume and recover it.

This remains a deletion-free preflight. It does not bind copied transport
buffers, every active receiver/publication/mutation lifetime, other-process work
before exact-inode open, noncooperating writers, policy, grace, quota/ENOSPC,
collection quarantine, restart reobservation, reclaim, or unlink. The writer
fence releases with the returned plan. A future collector must reacquire the
store-global exclusive lease, reobserve every durable and live root, lock every
candidate inode at its mutation cutpoint, and stage collection separately from
corruption quarantine and user-restorable history. See
`PROCESS_STORE_LIVE_CAPABILITY_AND_WRITER_FENCED_RETENTION_AUDIT_rev0978.md`
and `REVISION_NOTES_rev0978.md`.

### Rev0978 validation

Exact rev0978 source passed a fresh GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests in bounded final-source shards, and an independent 39/39 product replay in 86.36 seconds. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 630 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 320 SQLite-owner, 450 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 158 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 349/349 checks. An isolated Clang 17 Debug product dependency graph completed 239/239 edges with AddressSanitizer and UndefinedBehaviorSanitizer. All 39/39 product tests passed in bounded lanes with leak detection and halt-on-error: the allocation-heavy 450-check folder-owner test passed separately in 30.71 seconds at 1,454,776 KiB peak RSS, and the remaining 38/38 product tests passed in 114.43 seconds. Focused sanitizer proof also passed the 630-check payload-store suite in 9.06 seconds at 503,672 KiB peak RSS and the 158-check local-control suite in 0.74 seconds at 112,900 KiB peak RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0977 parent SHA-256 matched acf4f08be987f2fb5d44b2ff1a0e4b34a460248ac29f72ff0f3498f7d7f0e73f and passed 41/41 checks under the rev0978 wrapper-aware verifier. The binary-aware source patch reconstructed all 16/16 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,575,951 bytes with SHA-256 f47ed3037fb6a2e553a2b278e7dd591f3b97afd4d62e44e8d0fb0dcb69962c89. Validation excluded superseded monolithic sanitizer invocations, interrupted full-registry wrappers, competing orphan release launchers, stale or source-divergent runs, and a transient Python bytecode cache removed before projection sealing.

## Rev0977: exact same-owner live payload-capability cutpoint

Rev0977 closes the next deletion-free retention gap: move-only payload-store
objects can outlive the short shared lease that created them and later reopen or
consume immutable payload bytes. One bounded process-local registry now tracks
snapshots, exact opened payload descriptors, targeted accessors, and mutation
batches issued by the exact retained store owner. Registration identity—not
only aggregate counts—is canonical. A separate non-durable activity generation
also advances on every successful register and unregister, so a capability
created and destroyed entirely between planner cutpoints cannot alias an idle
set. Both sequences fail closed instead of wrapping, and RAII member ordering
removes a root only after its descriptor or authority state has been released.

The planner excludes only its own exact live snapshot, captures the registry
before and after projection, and fails at typed stage
`retention_live_capability_set` on any set or interval-activity change. The
activity generation is deliberately absent from the canonical set digest,
serialized response, and deletion-free mark: quiescent roots still have one
page-invariant identity, while the in-process bracket detects complete ABA
activity. Live snapshots and targeted
access conservatively root every current physical payload; opened descriptors
root only their exact digest and size. Each physical entry exposes
`same_store_owner_live_capability` without converting that temporary lifetime
into causal history.

The exact deletion-free mark advances to domain v3. Live and terminal status
advance to `anonsync.peer-service.status.v22`; the owner-only retention response
advances to `anonsync.local-retention-plan.response.v4`. The response explicitly
binds only same-owner in-process capabilities. Independently opened owners,
other processes, copied transport buffers, complete active-pass/receiver roots,
policy, durable mark intent, collection quarantine, and unlink remain false or
absent.

The adjacent audit restored historical rev0976 schema prose and revision-
specific structural checks after an unsealed global replacement had rewritten
them to v22/v4. It also found the complete create-and-destroy ABA interval that
registration-set identity alone could miss. A test-only friend bridge now
exercises the private cutpoint without adding a shipping operation or widening
targeted access. See
`EXACT_LIVE_PAYLOAD_CAPABILITY_CUTPOINT_AUDIT_rev0977.md` and
`REVISION_NOTES_rev0977.md`.

## Rev0977: payload-use lease and current snapshot reader fence

Rev0977 closes the live-descriptor seam that prevented rev0976's exact
retention evidence from becoming a safe future collector input. A complete
snapshot previously reopened digest-named payloads without reacquiring the
current store reader fence, and a returned descriptor carried no cooperating
cross-process lifetime witness. An open descriptor alone does not preserve its
pathname against rename or unlink.

Every snapshot byte reopen now takes the current shared payload-store identity
lease, then a shared lock on the exact payload inode under
`anonsync:sync-replica-file-payload-use-flock-lease:v1`. Targeted one-digest
selection uses the same order. The short global lease is released at the
selection cutpoint, while `SyncReplicaFilePayloadStoreOpenedPayload` carries the
exact-inode lease through local byte consumption and releases it with the final
descriptor close. Bounded range sending copies bytes before network I/O, so a
slow Tor or I2P peer does not retain either lease.

The existing corruption-quarantine rename and diagnostic-quarantine release
unlink now exercise the collector side of the protocol: global store `LOCK_EX`
first, exact candidate inode `LOCK_EX` second, then rooted mutation. Focused
regressions prove current snapshot reader fencing, same-process contention,
clean final-close release, unchanged namespaces on contention, and a forked
child that remains the sole holder of an API-issued descriptor and still blocks
quarantine until it closes.

The adjacent audit corrected stale append-only comments and removed an embedded
NUL accidentally introduced into the C++ regression. Required rev0977 release
source and records are now independently checked for NUL-free UTF-8 input.

This remains a necessary writer-fence primitive, not collection authority. The
deletion-free plan still truthfully reports
`opened_sender_transient_roots_bound:false`,
`external_transient_root_model_complete:false`,
`writer_fenced_collection:false`, and `reclaimable_authority:false`. Active
passes that have not opened bytes, receiver/publication/mutation lifetimes,
policy, a durable mark, collection quarantine, restart reobservation, and final
unlink remain incomplete. Advisory locking does not constrain noncooperating
same-UID or privileged writers, and remote filesystems still require live
qualification. See
`PAYLOAD_USE_LEASE_AND_SNAPSHOT_READER_FENCE_AUDIT_rev0977.md` and
`REVISION_NOTES_rev0977.md`.

### Rev0977 validation

Exact rev0977 source passed a fresh GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests in a final serial replay (129.22 seconds), and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 613 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 320 SQLite-owner, 448 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 155 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 339/339 checks. An isolated Clang 17 Debug product dependency graph completed 239/239 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 39/39 product tests passed serially in 144.09 seconds with leak detection and halt-on-error. Focused sanitizer proof passed the 613-check payload-store suite in 13.33 seconds at 484,272 KiB peak RSS, the 448-check folder-owner suite in 39.78 seconds at 1,453,628 KiB peak RSS, and the 155-check local-control suite in 1.44 seconds at 105,116 KiB peak RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0976 parent SHA-256 matched 44d90e8b74fffe16239ea0e6b1516a215950d7bc1d558344e7c64b5189a7f566 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 18/18 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,498,367 bytes with SHA-256 d4ad87ef909365a2af2515451da83248a94680bce23f0056dfff0f3c8db0b8b6. Validation excluded overlapping or stale shared-tree launchers, interrupted wrappers, divergent unsealed branches, and every result not bound to the exact final active projection.

## Rev0976: exact transient-namespace retention cutpoint

Rev0976 closes a collision in rev0975's deletion-free storage witness. The
payload snapshot previously bound only transient entry count and physical
bytes. Different staged transfer or publication obligations could therefore
share one snapshot and retention mark when those aggregates matched.

A complete rooted payload-store scan now emits one canonical digest over every
staged-prefix, staged-range, assembly-residue, and publication-residue identity,
including the staged-prefix reserved completion extent and one canonical
POSIX regular-file observation for each transient inode. The regression
separately proves same-reservation target drift and reservation-only drift, so
neither semantic identity nor capacity can hide behind unchanged physical
aggregates. The complete snapshot
advances to domain v4 and binds that witness plus reserved bytes. The exact
deletion-free retention mark advances to domain v2 and independently binds the
same transient witness and aggregates. Same-count/same-byte identity drift now
invalidates a paginated retention cutpoint.

Stable plan output exposes
`payload_store_transient_namespace_bound:true`,
`external_transient_root_model_complete:false`, the exact transient namespace
digest, and its count/physical/reserved byte totals. Live and terminal status
are `anonsync.peer-service.status.v21`; the owner-command acceptance response
advances to `anonsync.local-retention-plan.response.v3`.

The adjacent refactor centralizes all four transient ordering predicates and
uses them for both scanner sorting and digest-order assertions. A stale build
whose CMake authority pointed at a divergent rev0976 tree was excluded and
removed; all release validation is rebuilt from the exact active parent
extraction.

This remains a deletion-free diagnostic. Open senders, active passes,
in-memory receiver and mutation obligations, explicit policy, durable mark
intent, collection quarantine, final revalidation, and unlink are not
implemented. See
`EXACT_TRANSIENT_NAMESPACE_RETENTION_CUTPOINT_AUDIT_rev0976.md` and
`REVISION_NOTES_rev0976.md`.

### Rev0976 validation

Exact rev0976 source passed a fresh GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 601 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 320 SQLite-owner, 443 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 155 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 320/320 checks. A fresh Clang 17 Debug product dependency graph completed 239/239 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 39/39 product tests passed with leak detection and halt-on-error. Focused sanitizer proof passed the 601-check payload-store suite in 9.26 seconds at 471,604 KiB peak RSS, the 443-check folder-owner suite in 21.26 seconds at 1,435,944 KiB peak RSS, and the 155-check local-control suite in 0.60 seconds at 99,144 KiB peak RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0975 parent SHA-256 matched f702193a48c41b500ded456a901532f18113d183170a86fed4203dcbc0606269 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 16/16 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,404,832 bytes with SHA-256 1e93e8685e695b93153a8a2a4ff05991c67ca5587a11b95f02cf5c95c931a17b. Validation excluded the partially generated unsealed evidence directory, every divergent cache tree, and every interrupted or superseded run.

## Rev0975: page-invariant deletion-free mark witness

Rev0975 keeps the exact rev0974 dry-run planner deletion-free while making its
complete result cheaper to compute and easier to bind across pages. The owner
replaces a node-allocated ordered map and one logarithmic lookup per physical
payload with one bounded borrowed vector, canonical sort, in-place root-mask
fold, and linear merge against the complete payload inventory. Immutable
operation strings remain owned by the restored causal model for the duration of
the call.

Every plan now carries `unreferenced_candidate_set_digest`, computed from the
complete canonical `(SHA-256, size)` set of physical objects not named by
retained File operations, and `exact_deletion_free_mark_digest`, which binds
that set to the folder plus exact operation, inactive-evidence, pin, visible,
and payload-snapshot digests. Both values are invariant across entry pages and
the independent status-byte frontier. The local response is
`anonsync.local-retention-plan.response.v2`; live and terminal status are
`anonsync.peer-service.status.v20`.

This is not a durable collection mark. Every result reports
`durable_mark_persisted:false` alongside the existing false reclaim, quota,
grace, and writer-fence flags. In-flight transfer roots, mutation/pass/sender
roots, explicit retention policy, durable intent, collection quarantine,
revalidation, restart repair, and unlink remain absent.

The adjacent cloudtainer audit rejected an unsealed worktree after a fresh build
found unrelated payload-store source that did not match the sealed rev0974 ZIP.
Rev0975 was reconstructed over a fresh exact parent extraction; only the
reviewed retention projection, witness, schema, tests, audit, and documentation
patch is eligible for release authority. See
`PAGE_INVARIANT_DELETION_FREE_MARK_WITNESS_AUDIT_rev0975.md` and
`REVISION_NOTES_rev0975.md`.

### Rev0975 validation

Exact rev0975 source passed a fresh GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 320 SQLite-owner, 441 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 155 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 312/312 checks. A fresh Clang 17 Debug product dependency graph completed 239/239 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 39/39 product tests passed with leak detection and halt-on-error. Focused sanitizer proof passed the 441-check folder-owner suite in 22.74 seconds at 1,418,744 KiB peak RSS and the 155-check local-control suite in 0.63 seconds at 99,008 KiB peak RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0974 parent SHA-256 matched 82d713da7546d14e3875e4b5beea1fb6ecb3fe4d4031e07c01ec7a10d39165f7 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 11/11 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,357,846 bytes with SHA-256 f2df82e79b066db5af8cef5545d4135e6714bbdf7cd05b1d72d6b8c069e12826. Validation excluded the contaminated unsealed payload-usage prototype, its abandoned worktree, and every result produced from it.

## Rev0974: exact deletion-free physical retention planning

Rev0974 composes rev0972's exact retained-payload reachability with rev0973's
durable causal-version pins into the first per-object storage explanation. The
retained service now accepts:

```text
anonsync_sync retention-plan --socket ABSOLUTE_SOCKET \
    [--after LOWERCASE_SHA256] [--limit 1..1024] \
    [--source-cutpoint \
      v4:exact:OPERATION_SET:EVIDENCE_SET:PIN_SET:PAYLOAD_SNAPSHOT]
```

One page observes the complete rooted payload namespace and reports physical
objects in lowercase digest order. Each entry preserves four overlapping root
facts—current visible, superseded active, inactive retained evidence, and
explicit local pin—and receives one explanatory disposition:
`current_or_explicit_pin`, `retained_history_or_evidence`, or
`unreferenced_by_retained_file_operations`. Complete-scope totals still include referenced
content that is physically missing.

The planner reuses the exact-v4 historical source cutpoint. A first SQLite
snapshot rejects known-stale operation, evidence, or pin policy before payload
work; one complete payload snapshot is bracketed by a second SQLite snapshot;
payload drift then fails closed. A continuation cursor must name one object in
the exact physical snapshot. All root, operation, object, and byte partitions
are checked before a page publishes.

`retention-plan` uses the existing mutex-linearized historical action lane and
strict owner-only socket. Equal complete queries coalesce; different pending
work rejects. The local response is
`anonsync.local-retention-plan.response.v1`, and live plus terminal status
advance to `anonsync.peer-service.status.v19`. One completed bounded plan is
retained in stable historical status; the generic step record drops the
duplicate page.

The adjacent audit found that a 256 KiB plan byte frontier was unreachable by
valid owner output: the largest accepted 1,024-entry plan encoded to 245,443
bytes. The presentation envelope is now 224 KiB, and a maximum-page regression
proves deterministic prefix truncation, exact digest continuation, and
independent headroom in the one-megabyte local response. The owner implementation
also centralizes the physical content key, root masks, disposition mapping, and
canonical reachability serializer instead of creating a second collector truth.

Every plan explicitly reports `reclaimable_authority:false`,
`quota_policy_applied:false`, `grace_period_applied:false`, and
`writer_fenced_collection:false`. Unreferenced means only “not named by retained
File evidence at this cutpoint.” Rev0974 has no in-flight/pass roots, durable
mark plan, grace/quota policy, collection quarantine, revalidation journal, or
unlink path. See `DELETION_FREE_EXACT_RETENTION_PLAN_AUDIT_rev0974.md` and
`REVISION_NOTES_rev0974.md`.

### Rev0974 validation

Exact rev0974 source passed the fresh GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 320 SQLite-owner, 441 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 155 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 305/305 checks. A clean Clang 17 Debug product dependency graph completed 239/239 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 39/39 product tests passed across bounded serial shards with leak detection and halt-on-error. One superseded combined sanitizer shard let the unchanged service lifecycle oracle reach its 30-second runtime cap after four of five cycles; the isolated authoritative rerun passed in 12.79 seconds with no sanitizer diagnostic. Focused sanitizer proof passed the 320-check SQLite-owner suite in 3.33 seconds at 556,136 KiB peak RSS, the 441-check folder-owner suite in 21.71 seconds at 1,412,208 KiB peak RSS, and the 155-check local-control suite in 0.63 seconds at 98,620 KiB peak RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0973 parent SHA-256 matched 62d265f026db82c946fe86df8700c6019826afc86604242716e9af564b84f7cd and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 18/18 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,336,658 bytes with SHA-256 1eb35263f32e14bb15be047a6bcadc88eb7aaac6bd5bcb9fd0898bf593b3377b. Validation excluded the rejected duplicate age-based planner prototype and every interrupted or timing-only non-authoritative run.

## Rev0973: durable causal-version retention pins

Rev0973 adds the first owner-controlled storage-lifecycle root over retained
causal history. The existing private service socket now accepts:

```text
anonsync_sync version-pin --socket ABSOLUTE_SOCKET \
    --operation LOWERCASE_SHA256
anonsync_sync version-unpin --socket ABSOLUTE_SOCKET \
    --operation LOWERCASE_SHA256
```

A pin names one exact immutable retained File operation. It is local durable
policy, not a mutable path label or a payload-side marker. SQLite schema v6 owns
one canonical sorted pin set, its count, and a folder-bound digest inside the
same cutpoint that already attests evidence, visible projection, outbox, limits,
and clock policy. Repeating an exact transition is a no-op; a real transition
advances state generation. Pinning rejects missing evidence and tombstones,
while unpinning an absent canonical ID is retry-safe and idempotent.

Every history page reports the pin-set digest/count and one `pinned` bit per
entry. Exact mode also reports an overlapping `explicit_pins` reachability
class, including missing pinned content; metadata mode remains payload-cold.
New v4 exact and metadata source cutpoints bind pin policy. Compatible v3/v1
exact and v2 metadata tokens are accepted only while the pin set is empty, so a
pre-pin token cannot wildcard later policy changes.

Pin and unpin use the existing mutex-linearized historical action lane. Live
and terminal reporting advance to `anonsync.peer-service.status.v18`, with one
typed `last_pin_update` result and separate pin/unpin counters. Dedicated
owner-only acceptance responses remain PID-bound and mode-0600.

The adjacent audit rejected an unsealed payload-namespace marker design because
it would split history policy from the causal SQLite owner. The real configured-
service regression then found and corrected a shipping wiring defect: valid Pin
and Unpin actions fell through to restore-request validation and terminated the
daemon. Validation is now action-specific, and the same retained process proves
pin, metadata reinspection, unpin, reinspection, exact status, and continued
operation. A second correction prevents legacy source tokens from acting as
wildcards once any pin exists. The complete registry also exposed a stale
schema-v5 source oracle and the absence of a direct v5-to-v6 runtime fixture.
The upgraded audit and regression now prove full prior-state preservation, an
empty migrated pin root, post-migration pin/restart behavior, and rollback of a
malformed v5 cutpoint before any schema-v6 surface publishes.

Rev0973 does not unlink payloads or add automatic retention, age/count/byte
policy, quota eviction, Archive chronology, batch restore, or remote pin
propagation. `reclaimable_authority:false` remains explicit. See
`HISTORICAL_VERSION_RETENTION_PIN_AUTHORITY_AUDIT_rev0973.md` and
`REVISION_NOTES_rev0973.md`.

### Rev0973 validation

Exact rev0973 source passed the fresh GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 320 SQLite-owner, 433 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 140 local-control, 87/87 observer, and 6/6 observer-race checks. The upgraded SQLite-owner source audit passed 43/43 checks, and the complete structural authority audit passed 292/292 checks. A clean Clang 17 Debug product dependency graph completed 239/239 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error. Focused sanitizer proof passed the 320-check SQLite-owner suite in 2.89 seconds at 556,172 KiB peak RSS, the 433-check folder-owner suite in 26.11 seconds at 1,432,996 KiB peak RSS, and the 140-check local-control suite in 0.56 seconds at 94,148 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0972 parent SHA-256 matched 5d8c791ded176f4b76e685103bf75b7697d5e466f5f8236ef7bf822f03523ded and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 21/21 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,229,745 bytes with SHA-256 576051d058ff39a23b32d3aef2487e296a18a398a67e4e28bc5a331e4e8b043e. The registry-driven audit correction also added direct exact v5-to-v6 migration, restart, and malformed-cutpoint rollback proof.

## Rev0972: retained-payload reachability inside the canonical frontier

Rev0972 makes the existing exact `versions` operation answer the first safe
storage-lifecycle measurement while preserving rev0971's shipping byte bound.
The completed inventory now reports one share-global
`retained_payload_reachability` object over current visible file operations,
superseded active history, inactive pending or quarantined evidence, their
deduplicated union, missing exact content, and physical payload objects named by
no retained file operation.

Identity is the exact `(SHA-256, declared size)` pair. Class totals can overlap
when several evidence classes share immutable bytes; `retained_union` counts the
object once. Entry, byte, and operation-reference equations are checked against
the same complete payload snapshot before output. The JSON explicitly carries
`reclaimable_authority:false`: unreferenced-by-retained-operation is a diagnostic
fact, not permission to unlink around catalogs, transfers, pass snapshots,
pins, policy, grace, or a collector journal.

Because inactive evidence now affects exact output, new pages emit
`v3:exact:<operation-set>:<evidence-set>:<payload-snapshot>` source cutpoints.
Evidence drift fails before payload work when already knowable and is bracketed
across the payload scan. Compatible v1 exact input and unchanged v2 metadata
input remain accepted. Metadata browsing stays payload-cold and returns null
evidence and reachability fields.

The adjacent refactor resolves an incompatible sibling-schema collision by
advancing service status to `anonsync.peer-service.status.v17`. It also removes a
second inline reachability serializer: source evidence, reachability, page
entries, and both truncation frontiers now use the same canonical stream for
exact 256 KiB counting and live/terminal emission. The owner-only response is
`anonsync.local-historical-versions.response.v5`, and the completed inventory
remains a single stable copy.

This is exact diagnostic reachability, not collection authority, retention
policy, Archive, chronology, selective sync, or remote historical transfer. See
`RETAINED_PAYLOAD_REACHABILITY_AND_CANONICAL_STATUS_FRONTIER_AUDIT_rev0972.md`
and `REVISION_NOTES_rev0972.md`.

### Rev0972 validation

Exact rev0972 source passed the fresh GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 296 SQLite-owner, 421 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 132 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 279/279 checks. A clean Clang 17 Debug product dependency graph completed 239/239 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error. Focused sanitizer proof passed the 421-check folder-owner suite in 33.17 seconds at 1,376,128 KiB peak RSS and the 132-check local-control suite in 0.57 seconds at 91,608 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0971 parent SHA-256 matched 7212288343824982bfc5c505cf32c39c9ec920d84850103daeafdbd8187f8c33 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 14/14 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,108,596 bytes with SHA-256 e226a95f2c0bf343ad4ff41353415686ea78bde24bcf3ea12c615eaac745d912. Validation also removed multiple orphaned divergent rev0972 build and prototype trees so only the sealed reachability/frontier source and its isolated build directories contributed release authority.

## Rev0971: byte-bounded history status and one stable result

Rev0971 closes a composition defect between the history query and the shipping
owner-only status socket. The query accepts up to 1,024 entries with canonical
paths as long as 4,096 bytes, while the socket rejects JSON above 1 MiB. A valid
large page could therefore succeed inside the folder owner but fail when the
same daemon attempted to publish its result.

The service now applies one deterministic encoded-byte prefix after the folder
owner produces its ordinary causal page. The exact canonical history JSON
encoder counts without allocating the rejected output, retains the largest
prefix at or below 256 KiB, and continues through the existing exact operation-
ID cursor and source cutpoint. Status distinguishes the folder owner's entry-limit frontier from the transport byte frontier through
`entry_limit_frontier_reached`, `status_byte_limit`, and
`status_byte_frontier_reached`.

The adjacent refactor leaves a single stable completed result by removing the
second copy of a completed inventory from generic `last_step`.
`historical_versions.last_inventory` remains the one stable result; generation,
action, request, and typed failure correlation remain in the step event. The
shipping renderer also streams the canonical inventory directly into the status
object instead of allocating another inventory-sized JSON temporary. Live and terminal reporting advance to
`anonsync.peer-service.status.v16`; CLI requests, local acceptance responses,
source tokens, restore semantics, and reconciliation generation 2 are
unchanged.

This is a bounded diagnostics and recovery-browser correction, not retention
policy, garbage collection, chronology, selective sync, or remote history
transfer. See
`BOUNDED_HISTORICAL_STATUS_PAGE_AND_SINGLE_RESULT_AUDIT_rev0971.md` and
`REVISION_NOTES_rev0971.md`.

### Rev0971 validation

Exact rev0971 source passed the clean GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 296 SQLite-owner, 406 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 132 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 267/267 checks. A clean-root Clang 17 Debug product dependency graph completed 239/239 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error. Focused sanitizer proof passed the 406-check folder-owner suite in 18.93 seconds at 1,371,184 KiB peak RSS and the 132-check local-control suite in 0.57 seconds. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0970 parent SHA-256 matched 57cb832afa5b63c3b7ab63028873855ec18c6e2ec90059c7ac7b64200ba2e7d7 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 13/13 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,058,026 bytes with SHA-256 11b2a46a3fc169546819c71172347dc64bb6f05bbca16d58ff5a790d21e239a8.

## Rev0970: payload-cold causal-metadata history browsing

Rev0970 separates two history-inspection authorities that rev0969 had combined.
The default exact mode still performs one complete, bracketed private
payload-store observation and reports whether each retained predecessor is
immediately restorable. The new metadata mode reads only the immutable causal
replica snapshot:

```text
anonsync_sync versions --socket ABSOLUTE_SOCKET \
    --inspection-mode metadata \
    [--path CANONICAL_RELATIVE_PATH] [--limit 1..1024]
```

Metadata mode returns operation IDs, paths, immutable sizes and content
digests, actor dots, current-primary identities, and bounded pagination without
acquiring the payload-store lease, enumerating its namespace, opening objects,
reading bytes, or hashing payloads. It does not guess availability. Payload
snapshot digest, scan accounting, aggregate payload/restore counts, and each
entry's `payload_present` / `restore_ready` values are JSON `null`.

Source tokens are mode-bound. Existing exact pages retain the byte-for-byte v1
form:

```text
v1:OPERATION_SET_SHA256:PAYLOAD_SNAPSHOT_SHA256
```

Metadata pages return:

```text
v2:metadata:OPERATION_SET_SHA256
```

A token from one mode is rejected by the other. This prevents a cheap causal
page from silently inheriting byte-availability authority and prevents exact
pagination from dropping its payload source. The default CLI remains exact for
compatibility.

The strict owner-only request now includes the canonical mode as its first
field. Rev0966–rev0968 request forms remain accepted as exact compatibility
frames. The local response advances to
`anonsync.local-historical-versions.response.v4`; live and terminal reporting
advance to `anonsync.peer-service.status.v15`.

The adjacent refactor centralizes canonical mode vocabulary in the shared query
header and changes payload-derived C++ fields to `std::optional`. Unknown is
therefore represented at the authority boundary rather than reconstructed by a
JSON renderer. The focused regression poisons the payload namespace with an
unexpected entry and proves metadata browsing remains payload-cold while exact
inspection still fails closed. The configured two-peer service regression
exercises the shipping metadata CLI and requires null payload evidence.

This is cheap causal browsing, not selective sync, placeholders, remote history
transfer, retention policy, chronology, conflict UI, garbage collection, or a
cheaper exact-availability scan. Restore still re-proves payload, catalog,
replica, and rooted filesystem authority. See
`CAUSAL_METADATA_HISTORY_INSPECTION_AUDIT_rev0970.md` and
`REVISION_NOTES_rev0970.md`.

### Rev0970 validation

Exact rev0970 source passed the complete GCC 14.2 Debug graph (527/527 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 296 SQLite-owner, 406 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 123 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 260/260 checks. A clean-root Clang 17 Debug product dependency graph completed 238/238 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error. Focused sanitizer proof passed the 406-check folder-owner suite in 18.02 seconds at 1,370,916 KiB peak RSS and the 123-check local-control suite. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0969 parent SHA-256 matched f06573e09238174517eb8cef22fd5df19276665665edcba71cb151527daa1d6b and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 14/14 changed active files and the complete 568-file projection byte-for-byte and by mode. The final active implementation projection contains 568 files / 26,027,982 bytes with SHA-256 4c1be1a1ff28901e0a9d769316dc258a7eceb2ce99794b332c07bf638e380fb8.

## Rev0969: exact-current-bound historical restore

Rev0969 closes the stale-browse overwrite gap in the shipping recovery command.
Every history entry already reports the sole visible
`current_primary_operation_id` against which it was classified. The operator
now copies that ID into the state-changing request:

```text
anonsync_sync restore --socket ABSOLUTE_SOCKET \
    --operation HISTORICAL_OPERATION_SHA256 \
    --expected-current CURRENT_PRIMARY_OPERATION_SHA256
```

The folder owner restores only when the selected path still has exactly one
visible operation and that operation is the expected current ID. A stale request
completes as `source_changed` at `restore_current_operation` before catalog,
rooted-path, or payload-store work. The service remains alive, and stable status
retains both operation IDs. The existing visible-state projection guard then
re-proves the same causal cutpoint before publication, so the early check is a
no-work rejection rather than a replacement for later authority fences.

Operation identity is deliberate. Equal file bytes can belong to distinct
causal operations, and a conflict cannot be reduced to whichever head sorts as
primary. A complete rev0968 page token would be too broad: unrelated path or
payload changes would reject an otherwise safe path-local restore. The exact
sole current operation is the minimum compare-and-restore validator.

The owner-only exact frame is
`restore-exact HISTORICAL EXPECTED_CURRENT\n`; its PID-bound response is
`anonsync.local-historical-version-restore.response.v2`. Live and terminal
reporting advance to `anonsync.peer-service.status.v14`. The rev0966 unbound
local frame remains accepted for protocol compatibility, but the shipping CLI
does not emit it and therefore never claims stale-browse protection for it.

The adjacent refactor replaces split socket/service operation strings with one
`SyncReplicaHistoricalVersionRestoreRequest` used by parsing, generation
coalescing, stable and transient status, and folder-owner execution. A different
expected current head is a different pending request. The focused regression
holds the exact payload store's exclusive mutation lease while proving stale
intent fails at the replica cutpoint; the real two-peer service regression
replays stale intent after a successful restore and proves same-PID survival,
unchanged state, exact failure evidence, and continued operation.

The full process registry additionally found a race in test-only tree
comparison: an exact internal atomic-publication temporary could disappear
between enumeration and read. Both affected process oracles now exclude only
the product's canonical lowercase-hex publication-temporary grammar, and the
sync-once oracle hashes files in bounded streaming blocks instead of reading a
whole large file into memory.

This is a path-local compare-and-restore precondition, not a durable transaction
from browse through restore. It does not add retention policy, version pins,
chronology, conflict selection, batch or directory restore, quotas, or garbage
collection. See `EXACT_CURRENT_BOUND_HISTORICAL_RESTORE_AUDIT_rev0969.md` and
`REVISION_NOTES_rev0969.md`.

### Rev0969 validation

```text
Exact rev0969 source passed the complete GCC 14.2 Debug graph (527/527 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 296 SQLite-owner, 397 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 119 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 247/247 checks. A clean-root Clang 17 Debug product dependency graph completed 238/238 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error. Focused sanitizer proof passed the 397-check folder-owner suite in 22.24 seconds at 1,348,040 KiB peak RSS and the 119-check local-control suite. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0968 parent SHA-256 matched 3edbc700faa3f736321ae8f41aade11e2198985f3a1a0552b1a237e72d9d916f and passed 41/41 wrapper-aware package checks. The final active implementation projection contains 568 files / 25,986,608 bytes with SHA-256 0d8b28b316b616dcd091fe374eff3468b36dfacc52749a39f7e14cb0c9851174.
```

## Rev0968: exact causal-history page source

Rev0968 turns rev0967's advisory per-page diagnostics into one owner-enforced
continuation contract. The first bounded history page now reports a canonical
`source_cutpoint` binding the exact active operation set and retained payload
namespace. Later pages can copy it back into the shipping command:

```text
anonsync_sync versions --socket ABSOLUTE_SOCKET \
    [--path CANONICAL_RELATIVE_PATH] \
    [--after LOWERCASE_SHA256] [--limit 1..1024] \
    [--source-cutpoint v1:OPERATION_SET_SHA256:PAYLOAD_SHA256]
```

A mismatched operation set fails before the complete payload-store scan. The
payload observation is bracketed by a second exact operation-set snapshot, and
a mismatched retained-payload snapshot also fails closed. The service reports
`source_changed` plus one exact stage instead of parsing prose or terminating.
Live and terminal `anonsync.peer-service.status.v13` expose the bound query,
`source_operation_set_digest`, canonical source token, retained failure class,
and drift stage from cached owner state; the exact completing `last_step` carries
the same typed evidence. The owner-only local response is
`anonsync.local-historical-versions.response.v3`; the strict frame gains an
optional source-token field while remaining backward compatible with rev0967's
three-field request.

The adjacent audit corrected both a consistency hole and avoidable work. A
valid cursor bound only its own current superseded operation, so other active
operations or retained payloads could change between pages. Rev0968 binds the
complete causal and payload inputs. It deliberately uses `operation_set_digest`
rather than generic replica `state_generation`, because unrelated liveness
writes do not determine a history page and must not manufacture false drift.
Stale source tokens and stale cursors are rejected before O(payload namespace)
work whenever the causal mismatch is already knowable.

This is exact browse consistency, not a durable snapshot transaction, chronology,
version pinning, retention policy, quota, Archive UI, or garbage collection.
Restore still re-proves every mutable owner and rooted destination from scratch.
See `EXACT_CAUSAL_HISTORY_SOURCE_CUTPOINT_AUDIT_rev0968.md` and
`REVISION_NOTES_rev0968.md`.

### Rev0968 validation

```text
Exact rev0968 source passed the complete GCC 14.2 Debug graph (527/527 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 296 SQLite-owner, 393 folder-owner, 7 folder-process, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 115 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 237/237 checks. A clean-root Clang 17 Debug product dependency graph completed 238/238 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error, including the focused 393-check folder-owner suite in 28.51 seconds at 1,342,052 KiB peak RSS and the 115-check local-control suite. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic.
```

## Rev0967: paged causal history and grouped projection

Rev0967 makes the bounded causal-version surface completely navigable. The
owner may now select one canonical relative path, choose a 1..1,024 entry page,
and continue after the exact active superseded operation at the prior page
tail:

```text
anonsync_sync versions --socket ABSOLUTE_SOCKET \
    [--path CANONICAL_RELATIVE_PATH] \
    [--after LOWERCASE_SHA256] [--limit 1..1024]
```

The completed `anonsync.peer-service.status.v12` inventory retains the exact
query, total operations in scope, operations after the cursor, bounded entries,
and `next_start_after_operation_id`. Missing, visible, malformed, or
out-of-path cursors fail closed. Separate pages remain separate observations;
their replica generation, visible-state digest, and payload-snapshot digest
must agree before a caller treats them as one listing.

The adjacent audit found that rev0966's 64-entry result could still perform
quadratic model work. Inspection called a whole-model path lookup for every
active operation, and a long path compared every candidate with every other
candidate. The shared model now groups one sorted vector of borrowed operation
pointers by path and aggregates maximum causal coverage per actor. A
differential regression proves the optimized visible set equals the public
pairwise supersession definition across a 258-operation concurrent history.
The response still retains only O(requested entries) value objects; global
grouping retains O(active operations) borrowed pointers. Causal aggregation
uses a deterministic actor map, so its exact bound is O(context entries log
actors), not the earlier draft's linear claim.

An adjacent safety audit rejected an unsealed protocol-generation-3 branch that
would have transferred superseded file operations without bytes. Operation-ID
paging can make such a predecessor temporarily visible after a partial pull;
a crash could then retain visible metadata with no later payload source.
Protocol generation 2 and its operation-before-bytes invariant remain intact.
Metadata-only history transfer needs durable staging or causally safe ordering.

Ordinary status remains filesystem-cold. Explicit inspection still pays one
complete payload-store observation so payload-presence and restore-readiness
bits are exact. This is deterministic causal browsing, not chronology,
retention policy, Archive UI, version pinning, quotas, or garbage collection.
See `PAGED_CAUSAL_VERSION_QUERY_AND_GROUPED_PROJECTION_AUDIT_rev0967.md` and
`REVISION_NOTES_rev0967.md`.

### Rev0967 validation

```text
Exact rev0967 source passed the complete GCC 14.2 Debug graph (527/527 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 296 SQLite-owner, 386 folder-owner, 7 folder-process, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 113 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 227/227 checks. A fresh Clang 17 Debug product dependency graph completed 238/238 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error, including the 386-check folder-owner suite in 18.72 seconds at 1,347,424 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic.
```

## Rev0966: bounded causal versions and rooted restore

Rev0966 turns already-retained causal predecessors into the first owner-operable
version-recovery slice. The private linked-peer control socket accepts:

```text
anonsync_sync versions --socket ABSOLUTE_SOCKET
anonsync_sync restore --socket ABSOLUTE_SOCKET --operation LOWERCASE_SHA256
```

Both commands report admission immediately and completion through ordinary
`anonsync.peer-service.status.v11`. They share the existing mode-0600 Unix
socket, PID-bound response validation, monotonic generations, request
coalescing, mutex-linearized action snapshot, and drain seal. A changed history
request cannot replace one already pending, and a request serialized after drain
is rejected without advancing its generation.

Inspection is explicit because it is potentially expensive. It performs one
complete rooted payload-store snapshot and one immutable replica snapshot, then
returns at most 64 entries by default (1,024 hard maximum). Each entry is an
active non-visible file operation with exact path, size, digest, actor/counter,
current head, payload presence, and restore readiness. Counts cover the complete
candidate set even when the list is truncated. Causal counters are not wall-
clock timestamps, and ordinary status polling remains filesystem-cold.

Restore does not trust the earlier inventory. It re-proves the active historical
operation, one unambiguous visible head, catalog, current rooted file or absence,
exact targeted payload descriptor, and guarded replica projection. It publishes
the selected bytes through the existing rooted atomic replace/create helpers and
then runs the ordinary prepared local scanner. The result must be a new causal
successor that supersedes the current head; old evidence remains immutable. A
stale candidate, missing payload, unresolved conflict, equal current bytes, or
replica/catalog/path drift completes as an explicit owner-visible failure rather
than terminating the daemon.

The adjacent refactor removes two avoidable whole-model response clones. The
causal model exposes a borrowed immutable active-operation visitor, and the
64-entry projection maintains one bounded max-heap before canonical sorting. A
real two-peer process regression changes a file from v1 to v2, discovers the
exact retained v1 operation, restores it, and proves both authenticated peers
converge v1 under a distinct successor.

This is not yet Resilio-style Archive UX. Availability depends on retained
append-only payloads; there is no version window, reachability pin, quota,
collector, friendly timestamp, batch restore, directory restore, or conflict
resolution. See
`EXPLICIT_CAUSAL_VERSION_INSPECTION_AND_ROOTED_RESTORE_AUDIT_rev0966.md`.

## Rev0965: one traversal-wide selected-name batch

Rev0965 closes the depth-multiplied memory boundary left by rev0964. The
resumable scanner already selected at most 4,096 immediate basenames at a time,
but it retained each unprocessed parent batch during recursive descent. A deep
tree could therefore hold one full selected-name vector per active directory
frame.

The component walker now returns descriptor-owning pending descent state at the
first child directory. The caller destroys the selected parent vector, including
its reserved capacity, before entering that child, then resumes the same open
parent strictly after the processed component. The child component, canonical
path, descriptor, and observation are independently owned; recursive traversal
and post-walk rebinding still prove the same rooted directory identity. The
non-resumable complete observer shares the classifier/rebinding path but keeps
its existing whole-directory vector.

The resumable loop proves no selected-name batch is live before the next
selector reserves storage, and the RAII owner independently rejects overlap. A
new diagnostic records the largest aggregate number of selected basenames live
at once. A two-level 8,191-file regression gives both an individual-batch peak
and a simultaneous peak of 4,096 rather than 8,192, while preserving exact
preorder, five expected directory passes, and one-time capacity charging. This
is a traversal-wide selected-name bound, not constant total memory: the number
of descriptors and pending component/path records scales with depth, while
aggregate canonical-path bytes also depend on growing path lengths. Releasing
batches can add parent `readdir` passes.

The adjacent audit tightened moving-namespace completion. Whenever released
parent state requires another selection pass, that rescan must match the exact
unconsumed first-census suffix count before it processes any selected name.
Detected growth, shrinkage, or a rename across the processed component boundary
returns `directory_census_frontier`; that inconsistent rescan cannot manufacture
a completed epoch or authorize absence. A deterministic child-callback rename
regression proves the first sweep stops conservatively and a fresh epoch sees
the moved path in exact order. This remains an asynchronous filesystem sweep,
not snapshot isolation; equal-cardinality mutation and changes after the last
required pass remain later-epoch/watcher work.

The adjacent release audit also restored four unrelated retained-version
prototype files from the sealed parent and removed an obsolete cleanup loop that
was terminating current rev0965 validators by pathname. Interrupted runs are not
release evidence; their affected link and test shards were rerun after process
quiescence.

See `GLOBAL_RESUMABLE_DIRECTORY_BATCH_LIFETIME_AUDIT_rev0965.md` and
`REVISION_NOTES_rev0965.md`.

### Rev0965 validation

- Fresh GCC 14.2 Debug complete graph: **527/527 configured build edges**, followed by an exact-final-source **35/35-edge** delta rebuild and no-work bundled-SQLite profile re-attestation.
- Complete GCC registry: **258/258 tests** in bounded terminal shards, with the final documentation-sensitive structural audit rerun as registered test 123.
- Independent GCC product lane: **39/39 tests** in bounded serial shards.
- Focused GCC checks: **84** resumable SHA-256, **19** scrub-state, **26** verification-index, **576** payload-store, **30/30** rooted POSIX resolution, **92** network-model checks with **41** generated operations, **296** SQLite-owner, **360** folder-owner, **110** sync-once, **2,043** TLS, **17** integrity-evidence, **92** local-control, **87/87** folder-observer, and **6/6** observer-race checks.
- Structural payload-store/folder-traversal authority audit: **210/210 checks**.
- Fresh Clang 17 ASan/UBSan product dependency graph: **238/238 build edges**, followed by an exact-final-source **35/35-edge** delta rebuild and no-work re-attestation.
- Clang ASan/UBSan product set: **39/39 tests** with leak detection and UBSan halt-on-error. The allocation-heavy folder-owner executable passed **360 checks** outside CTest's fixed timeout at **1,311,404 KiB peak RSS**, and the focused observer suites passed **87/87** and **6/6**.
- Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic.
- Exact rev0964 parent SHA-256 matched and the wrapper-aware parent verifier passed **41/41 checks**.
- Source patch reconstruction covers **5/5 changed active files** byte-for-byte and by mode.
- Active implementation projection: **567 files / 25712778 bytes**, SHA-256 `c1fda16a5a848ed3da1ff8548f08cddb30fcde711da8b8e027afd1f12bfca35d`.
- Publication remains contingent on the exact manifest, wrapper-directory and ZIP verifiers, ZIP CRC/path/no-symlink policy, and clean-extraction path/byte/type/mode equality.

## Rev0964: bounded resumable immediate-directory batches

Rev0964 removes a repeated flat-directory memory cliff from the shipping local
repair scan. The durable continuation and 4,096-path frontier already bounded
callbacks and scan-journal rows, but the observer still copied and sorted every
immediate basename before it could classify the first path. A flat directory
near the namespace ceiling therefore rebuilt one complete component vector on
every segment.

The resumable observer now selects the next component-wise lexicographic prefix
with a fixed 4,096-name max-heap held in one reserved `std::vector`. It performs
one complete `readdir` pass, retains only the smallest eligible batch, sorts that
same vector in place, moves it into the batch, and processes it through the same
regular-file classification,
recursive descent, callback, cursor, and post-walk directory-rebinding code.
Unselected `dirent` names are compared as `std::string_view`, so they do not
create one transient heap-owned string apiece. Another directory pass occurs
only when names remain and the current segment can still deliver useful work.
The first eligible-component count becomes a decreasing visit fence, so a
concurrently appended suffix cannot turn bounded storage into an unbounded
rescan chase. If a later enumeration sees names beyond that first census, the
segment returns `directory_census_frontier` rather than claiming
end-of-namespace. Its last delivered cursor remains usable, but completed-epoch
absence and deletion authority stay unavailable until a later stable segment.

Every non-dot entry observed by the first complete pass is charged exactly once
for that directory visit. Later selection rescans do not double-spend the
independent namespace ceiling, while every cursor-skipped regular file is still no-follow classified
and counts toward whole-folder file capacity. The traversal remains an
asynchronous sweep rather than a point-in-time namespace snapshot. Completed-
epoch absence, rooted mount/path authority, and callback-before-cursor ordering
are unchanged.

Two diagnostic fields expose enumeration-pass count and the largest individual
component batch. They are diagnostic test evidence only. At the rev0964
cutpoint, the 4,096 value was **not** a process-wide simultaneous-name bound:
recursive descent could retain one bounded batch per active directory depth.
Rev0965 releases ancestor batches before descent. The non-resumable complete
observer still retains its former whole-immediate-directory vector. The focused 4,113-file
regression proves exact sorted delivery without omission or duplicate, two
count frontiers followed by exact namespace completion, a largest batch of
4,096, one-versus-two enumeration passes, and no duplicate namespace charging.
A second 4,097+17-file mutation regression inserts one name between the first
batch boundary and the last original census member, plus sixteen later suffixes.
It proves the new name may consume the final bounded slot but cannot manufacture
completion: the segment stops at `directory_census_frontier`, persists its
cursor, and the continuation reaches the displaced original plus every new name
exactly once. Existing rooted-race and folder-owner suites continue to bind
directory identity, durable progress, restart, and deletion fences.

This exchanges unbounded flat-directory allocation for bounded per-batch memory,
not for a durable subtree index. Large skipped prefixes and later batches still
repeat enumeration/classification, and no huge-tree RSS or latency claim is
made. See
`BOUNDED_RESUMABLE_DIRECTORY_COMPONENT_BATCH_AUDIT_rev0964.md` and
`REVISION_NOTES_rev0964.md`.

### Rev0964 validation

- Fresh GCC 14.2 debug graph: **527/527 configured build edges**, followed by exact-source no-work bundled-SQLite re-attestation.
- Complete GCC registry: **258/258 tests** on the final source and documentation, with the final structural source audit closing test 123.
- Independent GCC product lane: **39/39 tests** in bounded serial shards.
- Focused GCC checks: **84** resumable SHA-256, **19** scrub-state, **26** verification-index, **576** payload-store, **30/30** rooted POSIX resolution, **92** network-model checks with **41** generated operations, **296** SQLite-owner, **360** folder-owner, **110** sync-once, **2,043** TLS, **17** integrity-evidence, **92** local-control, **77/77** folder-observer, and **6/6** observer-race checks.
- Structural payload-store/folder-traversal authority audit: **205/205 checks**.
- Fresh Clang 17 ASan/UBSan product dependency graph: **238/238 build edges**, followed by exact-source no-work re-attestation.
- Clang ASan/UBSan product set: **39/39 tests** with leak detection; the allocation-heavy folder-owner executable passed **360 checks** outside CTest's fixed timeout, and the new observer suites passed **77/77** and **6/6** without sanitizer diagnostics.
- Exact rev0963 parent SHA-256 matched and the wrapper-aware parent verifier passed **41/41 checks**.
- Source patch reconstruction covers **5/5 changed active files** byte-for-byte and by mode.
- Active implementation projection: **567 files / 25687923 bytes**, SHA-256 `feb5974b52c3d85635a0019cb9a58f90748834a22ccf8782f5e5f5dcb0492a04`.
- Publication remains contingent on the exact manifest, wrapper-directory and ZIP verifiers, ZIP CRC/path/no-symlink policy, and clean-extraction path/byte/type/mode equality.

## Rev0963: restart-discoverable bounded diagnostic inventory

Rev0963 closes an operator-discoverability gap in the exact corrupt-payload
quarantine. Preservation and release were already safe, but status exposed only
the last action/result. A process restart or several retained incidents could
leave older exact digest pairs hidden in the private namespace even though
`quarantine-release` requires those pairs as selectors.

The shipping local protocol does **not** gain a list command. Instead, ordinary
complete writable payload-store scans and the existing exact preserve/release
namespace observer project their already-paid complete observations into one
fixed-width process cache. At most sixteen entries retain only expected SHA-256,
observed SHA-256, and size. The projection is canonical, overflow checked, and
published only after the supporting lease/root/fault cutpoints. Before a rename
or unlink, prior status is forgotten; the prepared exact successor publishes
only after final durability and authority reproof. A failure can therefore make
the view unknown, but cannot knowingly leave stale retained-set truth.

`SyncReplicaFilePayloadStore::quarantine_inventory_status()` is exact-owner-
thread and filesystem-cold: it acquires no payload-store lease, performs no
traversal, opens no file, and hashes no byte. A raw fresh store owner begins with
an unknown observation. The retained service deliberately takes one complete
payload-store snapshot during initial repair and moves that exact snapshot into
ordinary convergence. Its live readiness predicate requires the resulting
allocation-free observation-known witness, not merely the historical initial-
repair bit. Therefore every ready service exposes a complete empty or populated
inventory without query-time I/O. The shipping counters prove one initial
snapshot handoff and zero duplicate convergence observation. This strengthens
operator truth at a real startup cost: readiness pays one bounded payload-
namespace traversal, although exact unchanged payload metadata may still avoid
rehashing bytes. The monotonic age is time since that process observation, not
persisted creation or retention age.

Status advances to `anonsync.peer-service.status.v11`. The existing
`payload_quarantine` domain gains `inventory` with observation age, entry/byte
frontiers, exact totals, and canonical entries. Live and terminal rendering
share the same implementation. The real configured-service oracle proves a
known empty inventory after initial convergence that required payload work, one
exact entry after same-inode preserve, and an exact empty successor after
release in the same healthy PID. The folder-wake oracle proves that even an
empty watched folder reaches readiness only after one complete payload-store
observation, that the snapshot is handed into convergence without a second
observation, that status polling performs no traversal, and that restart repeats
that bounded cutpoint. The focused store oracle proves process-cold unknown
state, restart rediscovery, and immediate preserve/release successor publication
without another full scan.

The adjacent audit removed an unfinished `quarantine-list` branch that would
have widened the socket protocol and performed a fresh rooted traversal per
query. It also corrected the stale-I2P-control regression: close on one TCP
stream is not ordered before a marker on another, so the test now waits for an
acknowledged control FIN through Linux `TCP_INFO` before permitting reuse.
Existing complete observers already own the inventory work. This is discoverable
diagnostic evidence, not an Archive, user version history, restore operation,
retention policy, or garbage collector. See
`RESTART_DISCOVERABLE_QUARANTINE_INVENTORY_AUDIT_rev0963.md` and
`REVISION_NOTES_rev0963.md`.

### Rev0963 validation

The exact final source completed a fresh GCC 14.2 Debug **527/527-edge**
graph and exact-source no-work re-attestation. The complete GCC registry passed
**258/258 tests**, and the independent product lane passed **39/39 tests**.
Focused suites passed **84** resumable-SHA, **19** scrub-state, **26**
verification-index, **576** payload-store, **30/30** rooted-POSIX, **92**
network-model plus **41** generated-operation, **296** SQLite-owner, **360**
folder-owner, **110** sync-once, **2,043** TLS, **17** integrity-evidence, and
**92** local-status-socket checks. The structural audit passed **197/197**
checks.

Clang 17 ASan/UBSan completed a fresh **238/238-edge** product dependency
graph and exact-source no-work re-attestation. All **39/39 product tests**
passed in bounded serial shards with leak detection and undefined-behavior
halt-on-error. No retained compiler, linker, AddressSanitizer,
UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic remains.

The exact rev0962 parent SHA-256 matched and its archive passed **41/41**
wrapper-aware checks. The binary-aware source patch reconstructs **14/14**
changed active files exactly. The active implementation projection binds
**567 files / 25,657,014 bytes** at SHA-256
`5d066b7a91ac61fff7aa61016f03434af9c1ef9a988e513b0fa84d69b908df07`.
Final publication remains conditional on the release gate, exact manifest,
wrapper directory and ZIP verifiers, CRC and canonical path/no-symlink policy,
and clean-extraction equality for every path, byte, entry type, and permission
mode.

## Rev0962: exact diagnostic release and unrelated byte-proof reuse

Rev0962 completes the bounded operator lifecycle introduced by rev0961. After
ordinary authenticated convergence has restored the expected payload and
cleared the active integrity alarm, the owner may reclaim one exact diagnostic
image without editing AnonSync's private content store:

```text
anonsync_sync quarantine-release --socket ABSOLUTE_SOCKET \
    --expected LOWERCASE_SHA256 --observed LOWERCASE_SHA256
```

The operation kind is carried through the existing owner-only local action
lane. `quarantine` and `quarantine-release` share one mutex-linearized request
slot, generation, combined snapshot, wait predicate, and shutdown seal, but they
are distinct request identities: a pending preserve cannot be mistaken for a
release of the same pair. Admission uses the strict
`anonsync.local-quarantine-release.response.v1` schema and remains scheduling
evidence rather than a claim that bytes were removed.

Release is allowed only after all active process integrity evidence has cleared.
Under the exact reader-fenced identity lease, the payload store re-proves the
retained root and identity, completely validates the bounded quarantine
namespace, opens the exact canonical private regular file beneath the rooted
capability, requires its descriptor observation to match the scan, re-proves the
named inode, unlinks only that file, synchronizes the directory, proves exact
absence, and re-proves lease plus both root authorities. A missing exact image
returns `exact_quarantine_absent`; any active fault returns
`active_fault_present`; forensic `ReadOnlyInspect` cannot mutate.

The explicit release path does not hash bytes solely to discard them. Preserve
must hash because a canonical name cannot prove observed content. Release makes
a different, narrower claim: the owner selected this exact diagnostic pair and
the rooted operation removed only the exact bounded private inode just
observed. It does not claim the deleted bytes were authentic.

The adjacent audit corrected a large-store waste defect. Rev0961 discarded the
entire process payload-verification generation after preserving one corrupt
object. Rev0962 retains exact proof for unrelated payloads, while still forcing
the durable namespace checkpoint to refresh, invalidating stale publication-
capacity observation, and clearing active scrub continuation only when it names
the removed digest. Complete scans still enumerate current names, so a cached
entry for the removed digest grants no authority. Releasing a quarantine changes
only the non-authoritative diagnostic namespace and retains all authoritative
payload acceleration.

Status advances to `anonsync.peer-service.status.v9`; canonical live and
terminal JSON now expose `preserve` versus `release` and count images released
separately from images preserved. The focused storage regression proves zero
unrelated payload hashes after both preserve and release. The real process
oracle performs exact preserve, authenticated re-admission and recheck, then
exact release in the same healthy PID while requiring the authoritative payload
bytes and inode, recheck history, readiness, and recovery evidence to remain
unchanged.

This is explicit irreversible diagnostic-evidence release, not automatic
retention, restore, version history, reachability, quota eviction, or garbage
collection. See `EXACT_QUARANTINE_RELEASE_AND_PROOF_REUSE_AUDIT_rev0962.md` and
`REVISION_NOTES_rev0962.md`.

### Rev0962 validation

- Fresh GCC 14.2 debug graph: **527/527 build edges**, followed by exact-source no-work re-attestation.
- Complete GCC registry: **258/258 tests** in bounded serial shards.
- Independent GCC product lane: **39/39 tests**.
- Focused GCC checks: **84** resumable SHA-256, **19** scrub-state, **26** verification-index, **562** payload-store, **30/30** rooted POSIX resolution, **92** network-model checks with **41** generated operations, **296** SQLite-owner, **360** folder-owner, **110** sync-once, **2,043** TLS, **17** integrity-evidence, and **92** local-control checks.
- Fresh Clang 17 ASan/UBSan product graph: **238/238 build edges**.
- Clang ASan/UBSan product set: **39/39 tests** in bounded immutable shards with leak detection; the focused payload-store and local-control executables also passed **562** and **92** checks without sanitizer diagnostics.
- Structural payload-store authority audit: **186/186 checks** on the final source and documentation.
- Exact rev0961 parent archive SHA-256 and wrapper-aware release verification are bound in `REVISION_EVIDENCE/rev0962/validation/PARENT_RELEASE_VERIFICATION.json`.
- Source-patch reconstruction, active projection, manifest, directory/ZIP verification, CRC, and clean-extraction path/byte/type/mode equality are release-sealing preconditions recorded in `RELEASE_GATE.json` and `REVISION_EVIDENCE/rev0962/`.

## Rev0961: exact corrupt-payload quarantine and authoritative re-admission

Rev0961 closes the next operator-recovery gap left by current-byte recheck. A
retained service that has proven an exact payload-integrity mismatch now accepts:

```text
anonsync_sync quarantine --socket ABSOLUTE_SOCKET \
    --expected LOWERCASE_SHA256 --observed LOWERCASE_SHA256
```

The owner-only local request is process-local scheduling evidence, not a claim
that bytes moved. The supplied pair must exactly match the active allocation-
independent integrity witness. Under the existing exclusive reader-fenced
identity lease, the payload store rehashes current bytes, rejects stale, changed,
repaired, or absent content with typed outcomes, and only then may rename the
exact corrupt inode to the canonical non-authoritative name
`.anonsync-payload-quarantine-v1-<expected>-<observed>`.

The move is rooted and no-replace. It synchronizes the exact open corrupt file
before renaming it, then synchronizes the directory, proves the source name
absent, re-proves the destination pathname, and requires the open source
descriptor to retain the same device and inode across the rename. An
already retained exact destination is fully SHA-256 hashed before success; if
the same corrupt authoritative name has reappeared, that source is also hashed
and removed so repeated identical corruption cannot remain permanently blocked.
Its filename is never trusted as evidence. Non-mutating outcomes leave the
retained basename empty, so operator status cannot imply that a destination
exists when no byte image was preserved.

Canonical quarantines are outside payload inventory and targeted access, but
complete scans still validate their private single-link regular-file shape and
apply a fixed sixteen-entry, overflow-checked byte frontier no larger than the
active indexed-byte budget. Fresh bootstrap rejects unexplained pre-existing
quarantine bytes even on the standalone payload-adoption path; diagnostic
bytes cannot acquire a newly invented store identity. Reaching either ordinary
frontier returns a typed non-mutating
capacity result instead of terminating the retained daemon; a structurally
over-budget namespace still fails closed during complete observation. A
successful move revokes
process verification, checkpoint-publication, and active-scrub acceleration
while retaining the integrity alarm. Preservation is not recovery: authenticated
ordinary convergence must re-admit the expected digest and complete the normal
folder/catalog/replica cutpoints before readiness returns.

The local control-plane audit extends the existing
`SyncLocalStatusSocketActionSnapshot` instead of adding a command queue. Drain,
recheck, and at most one exact quarantine pair are ordered by one mutex, observed
through one combined snapshot, waited on by one predicate, and sealed together
at owner shutdown. Same-pair requests advance and coalesce; a different pair is
rejected while pending; owner completion cannot erase a later same-pair
generation; and post-drain requests do not advance state. The socket worker still
has no payload, folder, SQLite, TLS, route, or effect capability.

Status advances to `anonsync.peer-service.status.v8`. Canonical live and terminal
renderers expose requested/started/completed generations, the exact pending pair,
bounded retry, typed result, retained basename only when proved, requests,
coalescing, attempts, completions, images preserved, and observed-content
transitions. Quarantine has priority over recheck and automatic integrity
recovery, but respects newly established lease backoff.

The real-process oracle holds the exact writer lease, coalesces rechecks, changes
a stable corrupt byte image, invokes the shipping quarantine CLI, proves
same-PID same-inode preservation outside authority, requires authenticated
re-admission of correct bytes under a distinct inode, completes forced recheck
and ordinary convergence, restores readiness, retains exact history, and drains
cleanly. It also records the honest cost: because quarantine changes the payload
namespace, correct re-admission requires one mutation-authority full scan. That
cost is exposed rather than hidden behind rev0960's duplicate-scan-free handoff
claim.

This is not automatic quarantine, user-file versioning, restore, retention,
reachability, or garbage collection. See
`EXACT_CORRUPT_PAYLOAD_QUARANTINE_AND_LINEARIZED_LOCAL_ACTION_AUDIT_rev0961.md`
and `REVISION_NOTES_rev0961.md`.

### Rev0961 validation

The exact frozen source completed the fresh 527/527-edge GCC graph, 258/258
registered tests, an independent 39/39 GCC product replay, the focused matrix
listed in the revision notes, a fresh 238/238-edge Clang ASan/UBSan product
graph, and 39/39 sanitizer product tests with leak detection. The structural
audit passed 180/180 checks; the exact parent passed 41/41 package checks; the
source patch reconstructed 15/15 active changes; and the active projection is
567 files / 25,546,979 bytes at SHA-256
`b83dd20d24e0814451a7ebea063e8759905292c9fd9915b569d422971eaa002f`.

## Rev0960: owner-triggered current-byte payload recheck

Rev0960 gives the owner one direct recovery operation on the existing retained
service:

```text
anonsync_sync recheck --socket ABSOLUTE_SOCKET
```

The owner-only mode-0600 local socket admits exactly `recheck\n`, returns a
strict PID-bound process-local request generation, and leaves completion to the
ordinary service owner. `anonsync_sync status` now exposes requested, started,
and completed generations; pending and bounded retry state; exact hash work from
the last completion; snapshot handoff; duplicate complete-scan routes; and
whether the completion also recovered a retained integrity fault. Acceptance is
not completion, and the generation is not durable payload authority.

The action control plane was tightened at the same time. Drain and recheck are
serialized by one mutex, observed by the owner through one
`SyncLocalStatusSocketActionSnapshot`, and waited on through the same predicate.
The old split stop/generation getters and the now-redundant atomic shadow state
were removed. Before any terminal status is frozen, the owner atomically seals
action admission and captures the final accepted generation. A request ordered
before that seal is represented as completed or pending terminal work; one
ordered after it is rejected without advancing the generation. This also closes
the non-local shutdown race from signals, cycle limits, and runtime limits. A
request arriving around retry sleep cannot be lost. Multiple requests may
coalesce into one proof, but a request accepted after a proof starts remains
pending for the next proof.

The proof itself is not a metadata refresh.
`SyncReplicaFilePayloadStore::snapshot_rechecking_current_bytes_or_throw()`
runs the complete rooted scanner with both process-local and durable digest reuse
disabled. The returned snapshot asserts zero reused entries/bytes and exact
hashed entry/byte totals. That same move-only snapshot then enters the existing
folder-convergence implementation, avoiding an immediate second complete
payload namespace observation while preserving catalog, local-folder, remote-
work, replica, and terminal-cutpoint reproof.

Cooperative lease contention retains the same daemon, listener, control socket,
route, and request. The first pending generation may bypass an old automatic
retry cutpoint, but later requests do not erase backoff established by an actual
attempt. A stable digest mismatch enters the existing fail-closed integrity
state. After external repair, the pending operator recheck forces bytes again,
converges the exact snapshot, restores readiness in the same PID, and retains the
exact recovery history. Automatic integrity recovery and operator recheck share
one completion helper instead of owning subtly different restoration logic.

The real configured-service process regression holds the exact writer lease,
queues two CLI requests, proves coalescing and same-PID typed deferral, injects
and changes stable corruption, repairs it, and requires generation completion
with one snapshot handoff, zero second complete payload snapshots, and zero
mutation full scans. The local-socket regression separately proves exact request
bytes, generation/wakeup behavior, client-drain ordering, the owner shutdown
seal, post-seal rejection, PID binding, owner/mode/path reproof, and malformed-
response rejection. Real-process terminal JSON is parsed with duplicate-key
rejection so operator evidence cannot depend on permissive parser behavior.

The package-policy review also collapsed a duplicated rev0960 mandatory-file
branch in the release verifier and bound the structural audit to exactly one
revision policy block. This is small code, but it prevents copied release rules
from drifting into two apparent authorities with set-union behavior hiding the
mistake.

An adjacent refactor centralizes the live and terminal `payload_recheck` JSON in
one canonical renderer. Status schema advances to
`anonsync.peer-service.status.v7`. The structural audit follows the shared
implementation helpers rather than treating thin wrappers as authority, proves
that action admission has one mutex model, and binds the owner shutdown seal to
the terminal rendering cutpoint.

This remains a payload-store operation, not a claim of filesystem-wide scrub. It
has no durable request queue, subpath selection, live byte-progress stream,
cancellation, quarantine, restore, retention, reachability, or garbage
collection. See `OWNER_TRIGGERED_PAYLOAD_RECHECK_AUDIT_rev0960.md` and
`REVISION_NOTES_rev0960.md`.

### Rev0960 validation

The exact frozen source completed the fresh 527/527-edge GCC graph, 258/258
registered tests, an independent 39/39 GCC product replay, the focused matrix
listed in the revision notes, a fresh 238/238-edge Clang ASan/UBSan product
graph, and 39/39 sanitizer product tests with leak detection. The structural
audit passed 166/166 checks; the exact parent passed 41/41 package checks; the
source patch reconstructed 16/16 active changes; and the active projection is
567 files / 25,420,532 bytes at SHA-256
`61fed36a59412827b9aec3e5d6604c37fecf5107de647cadef28422bf4086788`.

## Rev0959: minimum-reader identity migration and cold downgrade fence

Rev0958 made `Prepared`/`Progress` a durable restart fence for current readers,
but rev0957-or-earlier binaries do not understand `Prepared = 4`. An older
reader could discard the unknown scrub record and then trust an exact stale
verification-index entry for metadata-hidden corrupt bytes. Rev0959 closes that
mixed-reader composition by raising the minimum payload-store reader generation
through the identity/lease-anchor basename rather than through another optional
sidecar.

The established standalone v2 and product v3 identity bytes remain unchanged.
Writable owners now use reader-fenced basenames. When exactly one legacy marker
is present, the new owner acquires an exclusive `flock` on that exact inode,
performs a complete rooted namespace and payload-byte scan with both process and
durable verification acceleration disabled, and only then atomically renames the
locked inode with Linux `RENAME_NOREPLACE`. It re-reads exact identity bytes,
accepts only the rename-permitted ctime transition, synchronizes the identity and
root directory, proves the legacy name absent and current name bound to the same
inode, and rebinds the live lease to the post-rename observation.

The successful cold scan is moved into the ordinary process verification
generation before the next snapshot, so migration does not reread payload bytes.
The pre-rename durable checkpoint is forced to refresh because its identity
observation cannot authorize the renamed marker. Corruption, cooperative lock
contention, conflicting marker bytes, or coexisting current and legacy markers
all fail before current-reader authority is accepted. `ReadOnlyInspect` remains
mutation-free and refuses a legacy-only root rather than migrating it.

An adjacent exact-name audit found that the remote-only payload lane probed the
four v2/v3 lease-capable names but omitted the unsupported v1 identity name.
That lane intentionally avoids a complete namespace walk, yet another identity
basename is lock authority rather than unrelated private-root debris. Rev0959
now separates the four selectable lease anchors from the five reserved known
identity names and probes all five whenever an identity inode is opened or
re-proved. A focused folder-convergence regression installs current plus v1
markers and proves rejection occurs before destination bytes or catalog state
are published, while both forensic markers remain untouched.

A separate restart audit found that a present checksum-invalid scrub record was
classified as unusable and then treated like clean absence. That was unsafe:
the damaged bytes may be the remains of committed `Prepared`/`Progress` intent,
yet corruption prevents the reader from recovering the one digest whose restart
acceleration must be revoked. Rev0959 therefore disables both process and durable
verification reuse for the complete payload namespace whenever the fixed-size
scrub record is present but unusable. Current bytes are hashed before snapshot
authority can return. Only a later exclusive state-reconciliation cutpoint may
replace the damaged record: ordinary scrub settlement does so after a complete
snapshot, while minimum-reader migration may do so under the still-held exact
legacy-inode lease before handing the cold process generation to the first
current-reader snapshot. A regression uses a one-byte optional scrub budget,
proving that same-size metadata-hidden corruption is detected by the complete
authority-producing scan rather than by an immediate scrub retry.

Setting both scrub work limits to zero now disables only bounded payload-byte
reads. It does not preserve damaged or non-idle write-ahead intent forever. Once
the complete scan has proved current bytes, the writable owner may publish a
metadata-only canonical settlement under the same root/identity/state cutpoint.
A fresh-process regression proves this costs one complete proof, then restores
durable restart reuse instead of rehashing the entire payload namespace on every
subsequent restart. The metadata-only lane does not advance the process-local
byte-scrub throttle; lease contention, stale observations, capacity refusal, or
publication failure leave the restart fence intact and immediately retryable.

The focused regression constructs a rev0958 `Prepared` record plus a forged
metadata-exact verification index over same-size corrupt bytes. It proves a
child-held legacy shared lock blocks migration, corruption leaves the old name
and inode unchanged, repair preserves exact `(st_dev, st_ino)`, the immediate
snapshot performs zero duplicate hashes, a fresh owner receives rebound durable
reuse, product v3 follows the same rule, and coexisting generations are retained
as fail-closed forensic evidence.

The same audit closed a second restart bug. Once a fresh complete scan has
hashed and proved the active `Prepared`/`Progress` payload, the optional scrub no
longer resumes an older partial SHA-256 checkpoint. It re-proves the frozen
state/root/metadata cutpoint, advances the fair cursor, and publishes `Idle`
without another payload read. This avoids both duplicate I/O and a false alarm
when a metadata-hidden repair made the current whole file good but the durable
partial checkpoint still represented old bytes. The final rev0959 status
schema v6 exposes `reverified_active_completed` separately from failure-witness
repair and versions the later cooperative-lease and ambiguous-network-outcome
evidence added to the same operator contract.

Sanitizer validation also exposed a test-authority defect: the configured-service
fault injection truncated a digest-named payload without first acquiring the
store's cooperative exclusive lease. Under slower instrumentation that write
could overlap a shared authoritative scan and exercise a generic unstable-
namespace exit instead of the intended stable corruption/recovery state machine.
The process regression now locks and re-proves the exact reader-fenced product
identity inode around every deliberate corruption and repair. The ordinary test
timeout remains sixty seconds, while sanitizer builds explicitly receive a
120-second folder-owner timeout rather than racing measured instrumentation
cost.

The now-correct corruption oracle exposed a separate production availability
bug at the cooperative boundary. A legitimate same-host writer can hold the
exact identity-anchor lease while the peer service reaches its payload store.
The store correctly reports typed nonblocking lease contention, but the service
previously allowed that retryable condition to escape and terminate the daemon.
Rev0959 retains the process, authenticated listener, mode-0600 control socket,
ingress state, and any active integrity alarm. Status records
`payload_store_lease_busy_deferred`, distinguishes a newly observed conflict from
a clock-only retry step, and exposes monotonic busy/backoff counters.

The retained service now owns one exact retry cutpoint rather than relying on the
outer daemon's 250 ms wake cadence. Initial repair and active integrity recovery
remain fail-closed and may perform only clock-only deferral until that cutpoint.
An established healthy owner gates local repair until the cutpoint but remains
available for bounded inbound work. Every observed conflict also schedules an
ordinary convergence pass at that same cutpoint: this moves an overdue repair
forward so it cannot starve ingress, and moves a distant periodic repair earlier
when an interrupted network session may have committed catalog or replica
progress before reaching the store.

The exception classification is phase-local rather than one global
state-preserving catch. Local repair contention preserves the current network
role. A payload-authority failure escaping an inbound or outbound network step
has no recoverable session result, so the step reports
`network_outcome_known=false` instead of fabricating peer or handoff evidence.
Unknown outbound outcome yields to inbound service for the full ordinary
successful-handoff horizon, preventing a duplicate turn; unknown inbound outcome
stays inbound. Both paths retain the same process and schedule bounded
convergence. The failed acquisition itself consumes no payload-store authority.
Because an enclosing convergence or network turn may already have committed
independent idempotent progress before reaching the store, the next authority
operation starts from fresh observation rather than claiming a pass-wide
rollback.

The real-process regression holds the exact exclusive lock, queries live status
before releasing it, proves the same PID remains ready in the healthy case,
accepts both truthful inbound and outbound ambiguity classifications, and then
observes the intended stable integrity alarm after the serialized corrupting
write.
That race also exposed a production availability boundary outside the
cooperative writer model. A same-UID repair tool that ignores the identity lease
can invalidate one complete descriptor-rooted payload observation without
changing the retained lock inode. Such finite drift previously escaped as a
generic terminal exception even though no replacement verification generation,
checkpoint observation, or snapshot authority had been published. Complete
store scans now classify only exact observation-staleness frontiers—truncation,
open/stat divergence, final pathname disappearance or metadata change, sidecar
traversal change, and root-directory drift—and restart once from a fresh
independent directory cursor after re-proving the live lease. A second stale
observation remains terminal, so external churn cannot create an unbounded scan
loop. A Linux regression changes and restores one byte after the first payload
read notification and proves the discarded attempt grants no authority while
the fresh attempt returns one exact current-byte snapshot.

This is an automatic one-way minimum-reader migration for a stopped old service,
not a seamless mixed-version rolling-upgrade or downgrade protocol. Cooperative
`flock` also does not protect against a hostile same-UID process that ignores the
store contract.

See `MINIMUM_READER_IDENTITY_MIGRATION_AUDIT_rev0959.md` and
`REVISION_NOTES_rev0959.md`.

### Rev0959 validation

The exact final source completed a fresh 527-edge GCC 14.2 Debug graph. The
complete registry passed 258/258 tests serially in 241.03 seconds, and a separate
product replay passed 39/39 tests in 121.76 seconds. Focused suites passed 84
resumable-SHA, 19 scrub-state, 26 verification-index, 515 payload-store, 30/30
rooted-POSIX, 92 network-model plus 41 generated-operation, 296 SQLite-owner, 360
folder-owner, 110 sync-once, 2043 TLS, and 17 integrity-evidence checks.

A fresh Clang 17 ASan/UBSan product dependency graph completed 238/238 build
edges. All 39/39 product tests passed serially with leak detection in 323.24
seconds; the touched payload-store suite separately passed all 515 checks under
the same sanitizer profile. No retained compiler, linker, AddressSanitizer,
UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic remains.

The structural authority audit passed 161/161 checks. The exact rev0958 parent
SHA-256 matched and passed 41/41 wrapper-aware ZIP checks. The binary-aware
source patch reconstructs 15/15 changed active files byte-for-byte and by mode.
The active implementation projection binds 567 files / 25358294 bytes at
SHA-256 `007228fcaf45dfeee48840793391f5342b0625ff6971ad4d760cdc76fc1d4d48`.
Directory, manifest, ZIP CRC, canonical-path, no-symlink, and clean-extraction
path/byte/type/mode checks remain publication gates and are recorded in the
sealed package evidence.

## Rev0958: scrub write-ahead restart fence and exact active witness

Rev0958 closes a restart composition gap between the durable payload
verification index and the optional rotating byte scrub. A scrub could detect
metadata-hidden corrupt bytes, lose its best-effort terminal failure record, and
then lose its allocation-free process witness at process exit. A fresh owner
could reuse the stale metadata-exact verification entry while its immediate
optional scrub was deferred by cooperative exclusive-lease contention.

A newly selected scrub target now publishes and exactly re-observes canonical
`Prepared` state before opening or reading the first payload byte. `Prepared`
and `Progress` are durable crash witnesses, not content proof. A fresh process
observing either state cannot use the durable verification index for that active
digest; its ordinary complete scan must hash current bytes before returning
authority, independently of whether the optional scrub is due or can acquire its
exclusive lease. An owner may reuse only its process-local verified entry after its own exact
commit/re-observation or a complete current-byte scan while the record is
frozen, bound to the full state value and the scrub-state file's canonical POSIX
observation.

The adjacent refactor changes scrub publication from a Boolean result to the
exact re-observed committed file metadata and centralizes transitions through one
owner. Newly selected work cannot read after uncertain publication. A completed
mismatch still installs the fixed-width process fault and now clears active
acceleration before any terminal allocation or best-effort failure publication.
The hard regression holds a cross-process shared lease that allows the complete
scan but mechanically blocks optional scrub, yet a fresh owner detects the
metadata-hidden corruption through the ordinary scanner.

The v1 record width and prior disposition encodings remain stable, but downgrade
compatibility is not claimed because older binaries do not understand
`Prepared = 4`.

See `SCRUB_WRITE_AHEAD_RESTART_FENCE_AUDIT_rev0958.md` and
`REVISION_NOTES_rev0958.md`.

## Rev0957: exact-owner payload-reproof handoff and evidence correction

Rev0956 made complete current-byte payload reproof and ordinary folder
convergence jointly mandatory before integrity recovery, but discarded the
completed payload snapshot between those operations. Convergence could therefore
enumerate the same payload namespace again immediately. Rev0957 moves that exact
snapshot into the existing convergence implementation. It does not create a
recovery-only synchronization path: ordinary and handed-off calls share one
implementation and retain the same catalog, scan-journal, rooted filesystem,
replica-effect, and terminal-settlement cutpoints.

The accepting folder owner validates the snapshot before any catalog or replica
work. Durable folder/root/identity equality is not sufficient because an
independently opened store handle owns a different process-local verification
cache and integrity epoch. The candidate must have been issued by the exact
retained store owner, remain current on its issuing thread and epoch, and still
pass both root authorities. A focused regression takes the proof, holds an
exclusive payload mutation lease that mechanically blocks any second complete
snapshot, and proves handed-off convergence still succeeds with one handoff,
zero new payload-root observations, and zero mutation full scans. A foreign
owner over the identical durable root is rejected without changing catalog or
replica state.

A follow-on cutpoint audit found that the first handoff implementation discarded
that frozen inventory only after a newly inserted payload. An append occurring
after the snapshot can instead make a local mutation put report
`AlreadyPresent`; retaining the older inventory would then falsely defer a ready
remote path using the same digest. Rev0957 now invalidates the pass-local
payload cutpoint after **any** mutation put and falls back to exact targeted
remote access. The regression constructs this interleaving and requires same-
pass remote publication with no duplicate complete namespace observation.

The adjacent audit corrected an operator-evidence defect. `failure_persisted`
was previously accumulated across all mismatches with the same expected digest,
so evidence for corrupt byte image A could be reported for changed image B.
Rev0957 scopes persistence to the exact expected/observed pair, resets it when
the observed digest changes, counts such transitions, and advances live and
terminal status to `anonsync.peer-service.status.v4`. Recovery also refreshes
capability-free native-I2P worker state while faulted and at the recovery
cutpoint so readiness cannot be restored from a stale pre-fault ingress view.

See `PAYLOAD_REPROOF_HANDOFF_AND_EXACT_OWNER_AUDIT_rev0957.md` and
`REVISION_NOTES_rev0957.md`.

## Rev0956: fail-closed same-process payload-integrity recovery

Rev0955 correctly revoked payload authority when current bytes disagreed with a
digest basename, but the retained peer service still treated that typed alarm
like every other command failure. The process exited and teardown removed the
only owner-only status/stop socket. Rev0956 makes the alarm an explicit state of
the reusable `SyncReplicaPeerServiceOwner` instead of a CLI-only exception
workaround.

While an integrity fault is active, the service schedules no ordinary filesystem
wake, repair, outbound pull, inbound application, or ingress event step. It can
only return a bounded backoff disposition or attempt complete current-byte
reproof. The network listener and owner-only control socket remain alive,
readiness is false, and `anonsync.peer-service.status.v3` exposes exact expected
and observed SHA-256 values together with durable-witness truth, detection count,
monotonic ages, retry delay, scrub bounds, and the latest bounded scrub report.
All unrelated exceptions retain their previous terminal behavior.

Recovery requires a complete leased payload-store snapshot followed by the
ordinary folder convergence pass. Only after both succeed does the owner clear
the active alarm and restore readiness eligibility. The first implementation
then erased the exact explanation for the outage; the adjacent audit corrected
that regression by retaining one process-local `most_recent_recovery` record with
the exact digest pair, persistence result, detection count, fault duration, and
recovery age. This history is operator evidence only and is never consulted for
payload or synchronization authority.

The real configured-service regression converges a file, corrupts its exact
digest-named payload, proves `faulted`/not-ready status and the same PID with a
live mode-0600 control socket, repairs the bytes in place, proves complete
current-byte reproof and readiness recovery, retains exact recovered evidence,
and drains cleanly. Rev0956 recorded one remaining performance debt: the explicit store reproof
could be followed by another payload-namespace observation in convergence.
Rev0957 addresses that immediate duplication by threading the immutable exact-
owner cutpoint through the existing folder pass; it does not remove the complete
store reproof or ordinary convergence requirement.

See `PAYLOAD_INTEGRITY_SERVICE_RECOVERY_AUDIT_rev0956.md` and
`REVISION_NOTES_rev0956.md`.

## Rev0955: restart-safe byte-bounded payload scrub and control-plane readiness

Rev0954 made exact unchanged metadata reusable across process restart, but it
intentionally did not detect storage corruption that preserved file metadata. A
complete fresh byte hash remained the only content proof. Simply hashing one
payload per pass would not fix that boundary: one payload may be many gigabytes,
a process-local cursor disappears on restart, and a large first object can
starve every later digest.

Rev0955 adds a durable rotating scrub whose work is bounded by both bytes and
distinct payload entries. The production payload store spends at most 4 MiB
across at most four payloads in one eligible attempt. Exact SHA-256 continuation
state, payload metadata, the active byte offset, a lexicographic fairness cursor,
completed-cycle count, and optional mismatch evidence are serialized in the
fixed-size checksum-framed `.anonsync-payload-scrub-state-v1` record. The record
is bound to the exact store identity marker and is published only through the
existing rooted atomic-file boundary.

The SHA-256 continuation is an independent C++ leaf rather than provider state
serialization. Its canonical checkpoint retains the eight chaining words,
64-byte partial block, total-byte count, and buffered-byte count; validation
rejects impossible modulo relationships, nonzero unused bytes, and the exact
SHA-256 message-length overflow boundary. Focused tests cover standard NIST
vectors, one million `a` bytes, every critical padding edge, process-style
checkpoint/restart cuts, malformed checkpoints, and comparison with the
existing OpenSSL-backed digest oracle. Partial hash state is scheduling evidence
only and never authorizes a payload.

The rev0955 audit also removes a binary-format drift risk inherited from rev0954.
The restart verification index and scrub state had separately encoded and
validated the same eleven-field POSIX regular-file observation. One shared
`sync_posix_regular_file_snapshot_codec` now owns the fixed 88-byte big-endian
projection, exact-width parser, and private mode-0600 single-link invariants.
Both v1 record widths and byte layouts remain unchanged; focused tests directly
exercise the shared negative-time round trip and reject short, extended, and
nonprivate projections.

The ordinary complete snapshot remains the namespace, capacity, and payload
authority. Scrub is attempted only after that shared observation lease is
released, after process throttling, and under a fresh fail-fast exclusive lease.
The owner re-proves the root, exact identity marker, frozen directory metadata,
state file, selected digest pathname, payload descriptor, and final pathname
before publishing progress. `ReadOnlyInspect` stays acceleration-cold: it
bypasses both verification caches, hashes every payload byte in each complete
forensic scan, and never advances the scrub schedule. Torn, malformed, stale, identity-rebound, or otherwise
disposable scrub state causes bounded work to repeat rather than granting trust.

A completed scrub mismatch raises the typed integrity error, but a digest
continued across several attempts is an exact-extent integrity alarm rather than
a point-in-time byte image. A persisted mismatch record is therefore not
corruption authority. It forces a current full-byte scanner reproof; a current
mismatch fails closed, while repaired bytes disprove and clear stale evidence.
The scanner's repair hash is reused so the optional scrub does not immediately
read the same bytes a second time. The store never deletes or silently
quarantines its sole payload copy.

The audit found a publication-loss gap around that best-effort record. A scrub
attempt advances its process throttle before I/O; without an independent
same-owner witness, failed or removed failure-state publication could leave an
unchanged warm metadata generation eligible until the next scrub window. An
adjacent exception-safety audit then found that the first process witness owned
its two digests as heap-allocating strings and advanced revocation state before
those allocations were guaranteed. Allocation failure at exactly that boundary
could therefore lose the witness or leave only a changed epoch; resetting the
scrub throttle was not fail-closed when the next optional attempt could defer on
lease contention. The witness now stores both canonical 64-character digests in
fixed inline arrays, and retention is mechanically nonthrowing. A deeper pass
found that caller-side retention was still too late because constructing the
typed integrity exception could allocate first. Fixed-width SHA-256 finalization
now reaches an allocation-free mismatch cutpoint, revokes older snapshots before
failure-record serialization or error construction, and forces every later
failure to escape instead of becoming an optional scrub deferral. Revocation
state changes only together with an allocation-independent diagnostic witness. The
shared process cache retains the expected/observed mismatch, forces complete
scan and mutation-preflight hashing for that digest, rejects targeted access to
it, and suppresses restart-checkpoint publication. Only a final leased complete
scan proving current good bytes or absence clears the witness. Each newly
observed mismatch also advances a non-wrapping owner-local integrity epoch.
Every future method call on a still-live snapshot issued under an older epoch is
permanently rejected, including its metadata-only inventory and digest
methods; repair authorizes only a newly completed snapshot and cannot resurrect
an older snapshot. Values or references already returned and a descriptor
already moved out of a snapshot remain explicit non-revocable capability
boundaries. A regression deliberately deletes the durable failure record,
proves repeated fail-closed behavior, repairs the file, and proves
warm reuse resumes only after one current full hash. A calibrated
allocation-fault sweep additionally proves that failures in the durable
publication and typed-error tail cannot return a post-alarm snapshot. Another
retains a live snapshot across mismatch and repair and proves that only replacement snapshot
authority becomes usable. A third ordered two-payload regression proves that a
newly observed earlier-path mismatch cannot evict the older unresolved witness.
Because the epoch shares the deliberately mutex-free owner cache, the snapshot's
central state gate now performs a cheap exact-process/thread authority proof
before every epoch read. Pass-scoped targeted access does the same before
consulting an active fault. This closes a foreign-thread metadata-only race
without turning ordinary snapshot getters into filesystem reproofs; a compiled
regression calls the canonical-digest getter from a foreign thread and proves it
is rejected before cache authority is touched.

The cyclic audit found a real restart-liveness defect in the first implementation.
For a one-payload namespace, entering a new cycle retained the completed-cycle
cursor while selecting the same digest as active work. Canonical state correctly
rejected `active == cursor`, so each fresh owner could reread the same prefix
forever. Rev0955 clears the prior cursor at cycle entry; bounded restart tests
prove progress through offsets 10, 20, and 30, exact completion of a 37-byte
payload, and progress in the following cycle.

An adjacent process-harness audit found a second readiness frontier. The retained
service owner can expose its authenticated network listener before its configured
owner-only status socket has completed construction. The provisioning proof had
used listener visibility as permission to issue `stop --socket` and could race a
not-yet-published socket after unusually fast convergence. Its first repair then
left a subtler stale-witness window: startup proved the socket, but a bounded
24-second convergence wait ran inside a 30-second service lifetime, so loaded
validation could reach the drain after orderly runtime shutdown removed the
socket. A centralized helper now proves each startup control endpoint, the test
uses a bounded 60-second service horizon, and the source endpoint is re-proved
immediately after convergence at the owner-only drain cutpoint. Every proof
requires a live process and an exact non-symbolic mode-0600 Unix socket. Public
data-plane readiness is not local control-plane readiness, and readiness evidence
is not durable authority across an intervening wait.

A second process-oracle audit found that the retained I2P ingress test gave its
blocked-direct probe only three seconds for both the local repair pass and the
connector attempt. Under an otherwise valid concurrent compiler load, the
bounded command could expire before pull began and emit no reconciliation
record, making the oracle inconclusive rather than proving the route boundary.
The test-only horizon is now eight seconds with a 15-second process guard. It
still requires typed reconciliation evidence, a nonzero command result, and no
completed direct TLS handshake; only scheduling margin changed.

The rotating check is deliberately not instant detection, a point-in-time
multi-attempt byte snapshot, a coverage-age SLO, quarantine, repair, hostile
same-UID defense, or a replacement for filesystem checksums. The state checksum is not a MAC and `flock(2)` remains advisory. The
complete namespace scan still performs O(total indexed namespace) metadata work.
The first named Resilio uninstall workload, operator-visible scrub age/progress,
retention and restore, safe garbage collection, changed-block reuse, rename and
directory semantics, many-share ownership, and cross-platform qualification
remain open. Exact frozen-source compiler, runtime, sanitizer, audit, and package
results are bound in `REVISION_EVIDENCE/rev0955/`.

## Rev0954: restart-durable payload verification and capacity-aware checkpointing

Rev0953 removed whole-payload-namespace work from the remote-only exact-digest
lane, but every fresh process still paid a complete SHA-256 read of every
retained payload when a full snapshot or mutation segment was required. The
process-local verification generation survived only until exit. At the 64 GiB
production indexed-byte default, an unchanged service restart could therefore
read tens of gigabytes before ordinary convergence work.

Rev0954 adds one private fixed-width checkpoint named
`.anonsync-payload-verification-index-v1`. It checksum-seals the exact store
identity marker plus sorted digest-name metadata: device, inode, type/mode, link
count, owner/group, size, mtime, and ctime with nanoseconds. A restarted owner
still enumerates every namespace entry and rooted-opens every admitted payload.
It may skip that payload's byte hash only when the live identity marker and every
payload metadata field exactly reproduce a valid checkpoint record. Missing,
malformed, oversized, checksum-invalid, identity-mismatched, or stale entries
fall back to complete SHA-256 verification.

The complete scanner remains the sole payload-root health, capacity, and
inventory authority. `ReadOnlyInspect` deliberately ignores process and durable
acceleration and hashes every payload. Canonical snapshot identity is unchanged;
new process-versus-durable hashed/reused counters are diagnostics only. The
binary parser is a small linked leaf with exact fixed-width length, generation,
checksum, sorted-unique digest, private-metadata, count/byte, and overflow
validation.

Publication is non-authoritative and crash-conservative. A shared snapshot never
writes. Only after returning its complete result and releasing the shared lease
may a fail-fast exclusive refresh re-scan and atomically create or expected-
replace the checkpoint. Mutation batches and completed range receivers already
own an exclusive lease and a complete exact index, so they can checkpoint without
a third scan. Writes are geometric—256–4,096 added entries or 64 MiB–1 GiB added
bytes, plus one graceful tail—and the exact fixed-width writer residue must fit
the existing transient protocol budget before an O(namespace) record is built.

The audit found that this capacity fence initially remained wasteful: a known-
impossible checkpoint could make the authoritative restart scan, the optional
exclusive refresh, and graceful teardown each walk the complete namespace.
Rev0954 retains the complete scan's exact negative capacity result as process-
local scheduling evidence. Ordinary refresh and close skip the known-doomed scan
until a later complete observation replaces the result or a payload mutation
invalidates it. A 128-byte-budget fixture proves cold hashing, repeated warm
reuse, durable deferral diagnostics, and absence of the checkpoint file.

The same audit found a smaller restart amplification after an exact warm-owner
repair. A process-local cache miss correctly rehashed a payload whose metadata
changed but whose bytes remained valid, yet the durable checkpoint was left
stale because the warm scan had intentionally not reread its body. The next
process then repeated the hash. Any process-cache-backed complete scan that
hashes an entry—or observes exact entry-count or indexed-byte drift from the
durable baseline—now forces one best-effort checkpoint refresh. A regression
proves one same-process exact repair is immediately reusable by a fresh owner.

A thread-affinity audit found a separate correctness boundary in three
best-effort paths. The verification cache is intentionally mutex-free and owned
by the process/thread incarnation captured by the rooted directory authority,
but refresh and teardown could inspect scheduler state before proving that
owner. Rev0954 adds a cheap internal owner-only gate before every such cache read;
full rooted and lease proofs still guard publication, while a clean no-op close
does not pay for an unnecessary filesystem reproof. The structural audit binds
all three orderings.

A wider namespace review also caught an integration defect in the first port.
The complete scanner understood the new internal file, while the lightweight
staged-prefix range observer still rejected it as unexpected. Both production
`fdopendir` loops now recognize, bind, and finally re-prove the exact checkpoint
without letting the range hot path read unrelated payload bytes.

Reconstruction over the exact sealed rev0953 project found two branch/build
hazards. First, stale Ninja objects masked a source-level mutation-batch
constructor mismatch after process-versus-durable counters were added. Final
validation therefore starts from fresh build directories. Second, an older
unsealed checkpoint branch had deleted rev0953's settlement requirement that the
pass's published remote fairness cursor equal the final durable `sync-once`
cursor. Rev0954 restores the sealed parent predicate, public contract, structural
check, and compiled scheduling-only movement regression before layering the
payload work.

The first fresh Clang ASan/UBSan product build then found a third graph defect:
the new checkpoint test consumed instrumented static code but was absent from
the explicit sanitizer final-link inventory. Rev0954 now binds both compile and
link inventories structurally, so the focused driver links the required runtime
instead of failing only in the release sanitizer lane.

The release audit also rejected a late one-payload-per-pass scrub experiment.
An entry bound is not an I/O bound: one retained payload may be many gigabytes,
and a process-local cursor can repeat the same prefix after restart. Rev0954
ships no such scrub or integrity claim. A later scrub owner must be byte- and
entry-bounded, durably fair across restart, and explicit about quarantine and
recovery.

Fresh GCC 14.2 Debug completed all 515 configured build steps. All 255 registered tests passed across deterministic 60/60, 60/60, 60/60, 60/60, and 15/15 shards; the explicit product lane passed 36/36 in 51.88 seconds. Focused executables passed 92 network-model checks with 41 generated operations, 30 POSIX-resolution checks, 21 verification-index checks, 213 payload-store checks, 296 SQLite-owner checks, 347 folder-owner checks, and 110 sync-once checks. The structural audit passed 87/87. A fresh Clang 17 ASan/UBSan product graph completed all 226 configured steps from an empty build directory after one external interruption and same-directory resume; all 36 product tests passed serially with leak detection in 132.44 seconds, and the same focused suites passed without a sanitizer diagnostic.

This checkpoint is restart acceleration, not permanent corruption detection.
Ordinary writes normally change mtime/ctime, but silent storage corruption or a
privileged/same-UID actor can preserve or reconstruct metadata. A checksum is not
a MAC. A durable rotating content scrub remains necessary, and optional Linux
fs-verity would require explicit filesystem qualification. Payload history is
still append-only; retention, restore, reachability pins, quarantine, garbage
collection, block-level changed-file reuse, rename/metadata semantics, selective
sync, many-share ownership, cross-platform qualification, and the first named
Resilio uninstall workload remain open.

## Rev0953: targeted payload access and terminal cross-owner settlement

Rev0952 bounded descriptor-rooted remote inspection but an ordinary remote-only
file candidate could still force a complete private payload snapshot. That scan
enumerates and validates every retained payload entry and hashes restart-cold or
changed payload bytes. Delivering one known digest could therefore cost work
proportional to all retained payload history.

Rev0953 adds a deliberately narrow exact-name lane. One move-only, pass-scoped
`SyncReplicaFilePayloadStoreTargetedAccess` performs identity reconciliation and
root setup once. Every digest probe and selection still takes a fresh fail-fast
shared lease, re-proves the exact identity marker and rooted authority, and opens
only the lowercase SHA-256 basename. Missing payloads remain unresolved bounded
scheduling work and do not block a ready suffix. No store lease spans planning
or destination publication.

The selected descriptor crosses the existing atomic publication boundary, where
bytes are streamed and SHA-256 checked before visible or catalog state advances.
The point lookup is explicitly not complete namespace authority: it does not
enumerate unrelated entries, attest payload-root capacity, or validate staged
objects. A regression places an invalid unrelated name beside a valid digest;
targeted apply succeeds while the complete snapshot still rejects the store. A
same-size corruption of the selected digest fails at publication with no visible
or catalog effect.

The first targeted implementation repeated identity reconciliation and root
setup for every probe and selection. The final pass-scoped refactor amortizes
that work without extending lease lifetime. Required and optional POSIX regular-
file component opens now share one implementation; optional mode maps only
`ENOENT` to absence. Symlinks, non-regular objects, unsafe components, mount
crossings, permission failures, and inode races remain fatal. Telemetry exposes
targeted access births, probes, selections, and selected operation bytes
separately from complete snapshots and missing-payload deferrals.

A separate completion audit found that a clean remote sweep needed a real final
replica observation. Rev0953 adds a complete visible-projection guard backed by
replica `BEGIN IMMEDIATE`. While that guard keeps the matching visible digest
stable, one catalog `BEGIN IMMEDIATE` transaction exactly re-proves the terminal
catalog, authenticated local-scan journal, and previous remote-work singleton
before scheduling progress is published. Any movement reports
`authority_cutpoint_changed` and withholds settlement. Ordinary and speculative-
idle completion use the same replica-then-catalog helper.

The final audit closed a smaller scheduling-only gap. After a pass returned, a
second process could move the durable remote fairness cursor without changing
catalog content or replica-visible digests. The centralized `sync-once`
settlement predicate now requires the pass's published cursor to equal the final
durable cursor, as well as matching terminal catalog and visible-state digests,
completed scan/sweep state, empty deferred remainder, and inactive continuation
journals.

Fresh GCC 14.2 Debug completed all 511 build steps, then all 254 registered tests passed in one uninterrupted 63.45-second CTest run and the explicit product lane passed 35/35 in 26.69 seconds. Focused executables passed 92 network-model checks with 41 generated operations, 30 POSIX-resolution checks, 164 payload-store checks, 296 SQLite-owner checks, 347 folder-owner checks, and 110 sync-once checks. The structural audit passed 75/75. A fresh Clang 17 ASan/UBSan product graph completed 222/222 steps; all 35 product tests passed serially with leak detection in 104.58 seconds, and the same focused suites passed under the sanitizers with no retained diagnostic.

This is bounded steady-state work and truthful classification, not an
incremental payload or remote index. Large projections still perform one exact-
name probe per candidate and reopen selections; local/snapshot lanes still walk
the complete payload namespace after restart; the verification cache is process-
local; history remains append-only; and changed files transfer as whole
payloads. The terminal fence is one writer-serialized observation, not atomicity
across two databases, payload storage, and filesystem effects. A durable metadata
index/change sequence, rotating scrub, retention/restore/garbage collection, and
multi-process fault/soak qualification remain the next scale boundaries.

## Rev0952: bounded rooted remote inspection and linear grouped projection

Rev0951 made remote effects cyclic, but it still opened and classified every
sole-visible remote pathname in one convergence pass before it could report the
projection settled. The apply-count frontier bounded effects, not rooted
inspection. A large stable projection could therefore hold the service in one
long descriptor walk, and restarting that walk from the fairness cursor did not
provide an authenticated completion witness.

Rev0952 adds an independent `maximum_remote_inspection_paths` frontier, default
4,096, and catalog schema v5 persists a cutpoint-bound inspection sweep. The
journal records the exact basis digest, the path after which the sweep began,
the acknowledged path count, the last acknowledged fairness cursor, and whether
any inspected path was unresolved. The basis binds the exact catalog digest and
the replica visible-state digest. A changed catalog or remote projection retires
old sweep progress; a same-basis restart must reproduce the cursor implied by
origin plus count or fail closed before effects.

Every pass still restores and hard-validates the complete remote projection
before rooted work. It then inspects only the unacknowledged cyclic remainder,
acknowledges safe no-ops and explicit deferrals, applies a separately count/byte-
bounded candidate segment, and publishes scheduling progress only after every
selected rooted apply owner completes. Selecting any effect invalidates the
pre-effect partial sweep because the catalog cutpoint changes. `sync-once` is
settled only when the final pass completes both the local scan epoch and the
remote inspection sweep, reaches `end_of_projection`, and carries no unresolved
or deferred work.

The configuration, provisioning, status, pass-report, and one-shot JSON surfaces
now expose the independent inspection limit and sweep state. Schema v4→v5
migration preserves and re-proves the authenticated local scan journal and the
existing cyclic cursor while initializing the new sweep fields to an inactive
state. Restart tests cover bounded continuation, unavailable payloads, stable
settlement, stale basis replacement, and tampered origin/count/cursor refusal.

A separate model audit found a scale defect in `SyncReplicaModel::visible_paths()`.
The bulk projection copied every distinct path and then called `visible_path()`
for each path; each call rescanned every active operation. A one-operation-per-
path replica therefore performed repeated full active-set scans. The model now
groups borrowed immutable operation pointers by borrowed canonical path once,
shares one path-view constructor with the single-path API, and materializes the
same canonical conflict projection without duplicate path ownership. A 512-path
reverse-insertion regression binds sorted output and exact primary identities.

Validation on the exact source completed the fresh 511-step GCC 14.2 graph. The
aggregate registry passed 253 other entries before the runner window closed as
it started inherited test 60; that isolated test then passed with 611/611
internal checks, covering all 254 registered tests without claiming one
uninterrupted run. The GCC product lane passed 35/35. Focused executables passed
92 network-model, 321 folder-owner, 99 sync-once, and 164 payload-store checks;
the structural audit passed 74/74. Clang 17 ASan/UBSan rebuilt all 20 affected
product steps, re-attested with no pending work, and all 35 product tests passed
as isolated leak-detecting invocations with no sanitizer diagnostic.

The work is bounded liveness and projection efficiency, not an incremental
remote index. Every pass still reconstructs and hard-validates the complete
visible projection; conflict maximality remains pairwise within each path;
rooted inspection is an asynchronous sweep rather than a filesystem snapshot;
local scan segments replay their skipped root prefix; immediate directories are
fully buffered and sorted; cold payload inventory is a complete namespace walk;
and retained history still has no coordinated restore/garbage-collection owner.

## Rev0951: cyclic remote fairness, scan-independent predecessor reproof, and one payload inventory

Rev0950's bounded remote prefix removed zero-progress rejection, but sustained
churn at an early canonical path could still consume every pass and starve a
later successor. Rev0951 persists a path-validated scheduling cursor in catalog
schema v4, moves every remote file/tombstone effect into one cyclic planner, and
starts each selection strictly after the last successfully selected path. The
whole visible projection is still hard-validated before effects. Count and byte
frontiers select at most one wrapped segment, and the cursor advances only after
all selected rooted apply owners complete.

A deeper crash-order audit found that the first fair planner still required a
present catalog predecessor to be hashed by the current local scan invocation.
That made remote liveness depend on scan-journal lifetime. Incomplete journals
survive restart, but completed epochs reset and delete their seen rows, so a
remote successor could wait for a whole new rooted epoch after a crash or remote
frontier.

The final owner decouples these responsibilities. A current-pass hash remains
the strongest nomination. Otherwise a durable catalog `File` predecessor may
enter candidate planning only after fresh rooted descriptor metadata reproduces
its source-snapshot digest. That metadata cannot authorize bytes: immediately
before publication, the exact apply owner reopens and fully hashes the local
file, reloads the catalog predecessor, and proves the remote successor again. A
same-metadata edit therefore fails closed. The scan journal remains resumable
local traversal and complete-epoch absence authority, not a remote-apply gate.

The pass also no longer snapshots the entire private payload namespace once per
selected file. One frozen verified payload inventory is shared by all remote
file readiness checks and applies, and is refreshed at most once if local
publication inserted bytes earlier in the pass. Visible file evidence whose
payload is not yet present becomes deferred scheduling work; it does not throw or
block ready cyclic suffixes. Every selected payload is still reopened and
exactly re-proved before rooted atomic publication.

Pass, status, and service JSON expose payload snapshot observations/entries,
missing-payload deferrals, catalog-predecessor metadata revalidations, and the
cyclic cursor. `sync-once` keeps missing-payload remainder unsettled. The idle
path now re-proves the authenticated local scan journal as well as catalog,
replica, payload, and cursor cutpoints.

Restart tests cover both incomplete and completed/reset scan epochs, late-path
service before a new epoch reaches that path, stale local-edit refusal, cyclic
fairness under renewed early-path churn, one-inventory multi-file application,
and missing-payload suffix progress. The final source passed all 254 GCC tests,
the 35/35 product lane, 292 folder-owner checks, 95 sync-once checks, the 70/70
structural audit, the fresh 222-step Clang ASan/UBSan product graph, and all 35
sanitizer product tests with leak detection and no diagnostic.

This remains bounded correctness, not target-scale efficiency. Every pass still
reconstructs the complete remote projection; local segments replay rooted
prefixes and sort complete immediate-directory name sets; restart-cold payload
inventory remains a complete namespace observation; and retained history has no
coordinated restore/GC owner. The next scale boundary is one crash-consistent
metadata/subtree, remote-work, and payload index with monotonic sequence and a
rooted rebuild/rotating-scrub oracle.

## Rev0950: bounded remote prefixes and truthful settlement

The shipping remote planner had a liveness contradiction with the fair local
scan. It collected every missing remote file and rejected the whole pass when
the aggregate crossed the byte budget. Since every retry saw the same sorted
projection, a valid set that fit only across multiple turns could make zero
progress forever. Zero-byte files and tombstones had the opposite defect: they
spent no file bytes and could drive effect work and candidate retention toward
the full 100,000-path admission ceiling in one pass.

Rev0950 retains complete-projection hard validation, then selects one stable
sorted prefix under independent aggregate-byte and 4,096-operation frontiers.
The first non-fitting candidate and its suffix are deferred. Committed prefix
values become exact no-ops on the next pass, allowing later work to advance. The
candidate vector is reserved only to the remaining effect allowance. Reports,
folder and sync CLIs, service status, and `check-config` expose the operation
count, deferred candidate count, and exact byte/count/end stop reason. The
4,096 value is a fixed production scheduling contract, not a new persisted user
knob.

The audit found two reporting errors around that correction. First, bounded
progress could still be classified as settled because the terminal classifier
looked only at conflicts. Settlement now requires the final folder pass to
complete its authenticated scan epoch, leave no deferred apply or absence work,
and reach the end of the remote projection. Second, a scan cursor/journal can
commit real crash-surviving progress without changing catalog or replica
content. The process cutpoint now includes the validated scan epoch, cursor,
counts, and chain digest, so scan-only continuation is not mislabeled a no-op.
The three owner snapshots remain sequential, not cross-database atomic.

A real two-process test forces three 42-byte files through a 42-byte aggregate
frontier. One cycle materializes one file and remains unsettled; the next
materializes the suffix but remains unsettled behind local scan continuation; a
third scan-only cycle completes the epoch and settles. Focused tests also prove
two-pass byte progress, a `2 + 2` zero-byte/tombstone count frontier, fail-fast
limit composition, and rejection of a valid selected prefix when a later path
violates a hard bound.

This revision bounds effects, not projection CPU. Every pass still inspects the
complete visible remote set, no durable remote apply cursor exists, early-path
churn can delay a suffix, local scan continuation still replays the root prefix,
and immediate directory names are still fully buffered and sorted. The next
scale owner remains a crash-consistent exact metadata/subtree and remote-work
index with monotonic sequence and a rebuild path; the rooted scanner should stay
as repair and rotating-scrub authority.

The frozen source passed the complete GCC 14.2 graph; all 254 registered GCC
tests; the 35/35 GCC product lane in 16.04 seconds; 260 focused folder-owner
checks; 94 focused sync-once checks; the 65/65 structural audit; a fresh 222-step
Clang 17 ASan/UBSan product graph; and 35/35 sanitizer product tests across seven
completed serial shards in 87.20 cumulative seconds with leak detection and no
diagnostic.

## Rev0949: independent namespace/file capacity and bounded idle entry

Rev0946 correctly bound the production catalog and payload owners to 100,000
regular-file identities, but the traversal field named `maximum_entries` still
carried two incompatible meanings. It counted every classified namespace object
while service composition also constrained it to file/payload capacity. A
directory, symbolic link, unsupported object, or reserved publication residue
therefore consumed the same quota as a synchronizable regular file. Valid nested
trees could be rejected before their durable file owners were full.

Rev0949 separates those contracts. `maximum_entries` now bounds all classified
namespace work and defaults to 262,144. `maximum_regular_files` independently
bounds synchronizable regular files and defaults to the 100,000-row production
catalog/payload contract. Both retain a 1,000,000 hard validation ceiling. Every
namespace object spends the first allowance; only a regular file spends the
second. The whole-walk regular-file counter includes a resumable segment's
replayed prefix and the first frontier candidate, so a persisted cursor cannot
bypass the folder-wide cap. The service JSON, `check-config`, provisioning,
share setup, status output, and relevant CLI paths now carry the new field. A
100,001 namespace-entry configuration is accepted when the regular-file ceiling
remains 100,000, while a 100,001 regular-file production request is rejected
before owner mutation.

The scan audit also found that rev0948's idle optimization could do the wrong
kind of bounded work. For a catalog known to exceed the 4,096-path segment
frontier, it could first take a replica snapshot and attempt a complete idle
proof, then fall back to the durable segmented scan. An unchanged large folder
could therefore pay for a whole speculative pass before the authoritative
continuation pass, and a tombstone-heavy catalog could trigger similar
whole-history projection work. Rev0949 gates the optimization on total retained
catalog mappings before replica projection, file counting, or traversal. Known-
large catalogs now enter the durable segmented path directly. A restart-backed
test proves this for five live rows and again after all five become tombstones.

Traversal reports now expose an exact diagnostic stop reason: end of namespace,
aggregate-file-byte frontier, or regular-file-count frontier. This value is
operator evidence only; it does not authorize a cursor, epoch completion, or
deletion. Root and opened-directory re-attestation still precede every returned
segment, and completed authenticated epochs remain the only absence authority.

This revision is capacity truth and duplicate-work removal, not huge-tree
qualification. Each immediate directory is still fully buffered and sorted,
every segment still replays the root prefix, completed-epoch absence adjudication
still inspects retained catalog history, and append-only catalog/payload history
still has no guaranteed churn headroom at the 100,000-current-file boundary. A
crash-consistent exact metadata/subtree index remains the next scale owner, with
the rooted scanner retained as rebuild and rotating-scrub authority.

The frozen source passed the complete GCC 14.2 target graph; every one of 254
registered GCC tests across bounded evidence shards; the 35/35 GCC product lane
in 25.75 seconds; 70/70 focused observer checks; 250 focused folder-owner
checks; the 59/59 structural audit; the complete fresh Clang 17 ASan/UBSan
222-step product graph; and all 35 sanitizer product tests across seven completed
fresh serial shards with leak detection and no diagnostic.

## Rev0948: count-bounded scan segments and idle-set refactor

Rev0947's durable continuation fixed semantic starvation, but its productive
segment was bounded only by classified file bytes. Zero-byte and very small
files could therefore drive one segment all the way to the 100,000-entry hard
namespace ceiling, retaining one acknowledgement string per path and publishing
one correspondingly large scan-journal transaction.

Rev0948 adds an independent internal delivered-regular-file frontier. The
shipping folder owner defaults to 4,096 paths per segment while preserving the
existing byte frontier. Cursor-skipped paths do not spend that allowance. The
next eligible path is left untouched when the count is full, and a cursor is
returned only after the same descriptor-rooted directory rebinding and retained-
root verification used by rev0947. Path effects still commit first and join the
journal only afterward, so a crash loses scheduling progress rather than
synchronized state.

A restart-backed fixture proves five zero-byte files converge as `2 + 2 + 1`
segments. The first segment emits exactly two seen-path INSERTs and one progress-
head UPDATE. A separate substitution test replaces an opened directory at the
count cutpoint and proves that the traversal throws before publishing success.
The old resumable observer overload remains source-compatible and keeps its
aggregate-byte-only behavior; production explicitly selects the stronger bound.

The unchanged-folder fast path is also refactored. It no longer copies and sorts
one observed-path vector and a second catalog-path vector. Every observed path
must prove unique `File` catalog membership; after a complete traversal, equal
observed and catalog file cardinalities prove set equality. Tombstone paths are
still inspected explicitly. This removes an O(number-of-files) duplicate path
allocation and sort without weakening idle authority.

This is a callback/journal scheduling bound, not huge-tree qualification. Each
directory is still fully read and sorted before processing, every resumed
segment re-enumerates and `lstat`s the root prefix, and the path-local fallback
still performs substantial durable attestation. The next scale owner remains a
crash-consistent metadata/subtree index with the current rooted scanner retained
as rebuild and rotating-scrub authority.

The exact source passed all configured GCC 14.2 Debug targets, 254/254 registered GCC tests in 34.05 seconds, the 35/35 GCC product lane in 16.83 seconds, 64/64 observer checks, 232 folder-owner checks, the 55/55 structural audit, the complete Clang 17 ASan/UBSan product target, and 35/35 sanitizer product tests in five fresh bounded CTest shards with leak detection and no diagnostic.

## Rev0947: durable fair scan epochs and conservative absence authority

Rev0947 removes deterministic-prefix starvation from the shipping local repair
scan. A pass may now stop before the next regular file would cross its aggregate
byte frontier, persist an exact continuation cutpoint, and resume after restart.
The cursor follows the observer's real component-wise depth-first order rather
than a flat path-string order, which would skip cases such as a directory
subtree preceding a similarly named sibling file.

The folder catalog schema is now v3. One bounded progress row and an ordered,
domain-separated SHA-256 seen-path journal preserve the epoch, cursor, count,
path bytes, and exact adjudicated prefix. Deletion inference requires a complete
walk and a full journal rehash. A cataloged path omitted from the journal but
still physically present restarts the epoch instead of becoming a false
tombstone. Exact v1 and v2 catalogs migrate transactionally; contaminated
near-matches fail closed.

The first prototype committed one SQLite transaction per visited file. The final
owner keeps path effects independently committed and replayable, then publishes
the whole completed traversal segment with one prepared INSERT loop and one
compare-and-swap progress-head update. A failed journal commit loses only
scheduling progress and safely replays effects.

Audit found and corrected a second race: a file visited in an early segment
could be deleted before the epoch completed, remain in the journal, and then be
restored immediately from the exact old remote predecessor. An absent local
path now fences that exact predecessor until a later epoch adjudicates the
absence. A distinct remote successor still follows the existing conflict/apply
rules. Remote tombstones likewise do not generically erase an unadjudicated
local regular file.

This is a deletion-safe asynchronous sweep, not snapshot isolation. Already-seen
changes are handled by a later epoch. Each segment still re-enumerates and
`lstat`s its skipped prefix, the hard traversal ceiling counts directories and
other namespace entries as well as regular files, while rev0948 now caps
delivered callbacks and journal rows independently of file bytes. The next scale owner should be a durable metadata/subtree index
with the current rooted scanner retained as rebuild and rotating-scrub
authority.

The exact source passed the complete 254-test GCC registry, including the 35
product tests; 49 observer checks; 225 folder-owner checks; the real process
continuation/restart test; the 51-check structural audit; and a clean 35/35
Clang 17 ASan/UBSan product lane with leak detection.

## Rev0946: capacity composition and scale-truth audit

Rev0946 corrects a production composition failure between three independently
bounded owners. The folder catalog and convergence pass defaulted to 100,000
current paths, while the production payload-store helper inherited the generic
4,096-entry default. A valid many-small-file tree could therefore exhaust the
append-only durable payload store long before reaching the accepted folder
boundary.

The production payload owner now explicitly admits 100,000 identities, the
content-inventory hard ceiling is aligned, and compile-time checks bind the
default catalog/local/remote path capacities. Each pass validates requested
local and remote counts against the actual retained catalog and payload store
before work; the linked service rejects over-capacity configuration through the
real `check-config` process. The higher ceiling keeps a 4,096-entry initial
vector reserve so small stores do not pay the maximum allocation eagerly.

This is capacity truth, not garbage collection. The store remains append-only;
a 100,000-current-payload tree has no guaranteed version-churn headroom. A
collector will require catalog/history/in-flight reachability, snapshot pins,
quarantine/revalidation, and an ordinary-user retention/restore policy.

The audit also identifies a more urgent scale semantic: full passes traverse
bytewise-sorted paths from the root and charge every classified file against one
aggregate byte budget. A stable oversized prefix can be serviced repeatedly
while suffix paths never run, and deletion repair cannot occur because absence
authority requires a completed walk. The next C++ scale slice should add durable
fair continuation and completed scan epochs, followed by a persistent payload
metadata index with rotating byte scrubs and scanner rebuild.

Repository/process inspection found that the 24-MiB active implementation is
wrapped in roughly 55 MiB of revision evidence plus an 18.8-MiB nested historical
archive. The default all-target graph also compiles the 15,167-line legacy
`sync_domain.cpp` and its 9,601-line selftest body even though the shipping
`anonsync_sync` does not link them. The existing product lane should remain the
ordinary edit loop; complete inherited assurance belongs in scheduled/release
gates. Historical evidence should move gradually toward deduplicated,
content-addressed checkpoints rather than being copied forever.

## Rev0945: reconciled lineage, warm batch publication, and shorter exclusion

Rev0945 began by repairing a source/test provenance split. Two unfinished trees
claimed the same revision while old build-directory names pointed at different
`CMAKE_HOME_DIRECTORY` values. Their status reports had accidentally combined
features and validation from both. The final source was selected by file-level
diff against rev0944, and every retained build is bound to that exact source.
A later bootstrap/code audit caught that the draft prose claimed pre-hash batch
release before the C++ owner actually performed it. Packaging stopped; the owner,
runtime proof, structural audit, and complete exact-source gates were corrected
and rerun together.

One discarded branch exposed payload-batch count and byte frontiers through CLI,
linked-service configuration, provisioning, and share setup. Rev0945 rejects
that premature product contract. The current 256-put and 256-MiB exact-work
frontiers remain internal scheduling choices until the first real Resilio
uninstall workload measures what operators actually need.

The retained branch makes successful payload mutation batches publish their
complete already-verified index into the process-local warm cache at teardown. A
move-only batch owns a shared cache capability, so it can safely outlive the
store handle that created it. Publication is best-effort acceleration only; a
failed cache update cannot alter durable put success. The old cache vector is
reclaimed after the exclusive lease is released, avoiding a metadata-destruction
tail inside the lock horizon. Cold process owners, changed observations,
forensic scans, and exceptional recovery still hash complete bytes.

The folder owner now carries one exact payload cutpoint from its idle attempt
into the authoritative fallback. An unchanged path or a new pathname reusing
existing content reopens and re-proves that retained payload without beginning a
mutation batch. Only a genuinely missing digest enters exclusive mutation. The
pass reports exact mutation source bytes, work bytes, batch scans, puts, and peak
segment cost as diagnostics.

A focused lease-horizon audit found that a changed path could leave its batch
live while the following catalog no-op was opened and fully hashed. The owner
now releases the unrelated batch before preparing a likely same-size catalog
no-op. A same-size edit simply reacquires after exact proof. This is a scheduling
hint only and grants no synchronization authority.

Important limits remain. Every new batch still walks, opens, and stats the whole
private payload namespace. The cache is restart-cold. New bytes are read once
for stable observation and again for durable insertion. There is no durable
incremental payload index, rotating scrub, reachability/GC owner, production
changed-block promise, or target-scale lease qualification. Those are product
gaps, not invitations to create another daemon or policy plane.

## Rev0944: batched payload admission and exact warm verification

The authoritative restart page is the release-root `BOOTSTRAPROSE.md`. This
hidden README preserves deeper implementation history; it does not define a
second mission.

Rev0944 removes two related payload-store costs left after rev0943. The shipping
folder pass now lazily retains one move-only mutation batch across sequential
local publications. Construction acquires one exclusive cooperative lease,
validates the identity marker, scans and classifies the complete bounded private
namespace once, removes only exact stale publication residue, and freezes one
sorted capacity/index view. Each successful create-new payload is independently
hashed by the publication path, reopened, and inserted into that live index; it
does not trigger another scan of all older payloads.

The folder owner releases the batch before remote payload snapshots/apply,
network waits, and the post-traversal absence phase. A mixed local/remote pass may
create another batch after applying a remote successor. The one-put store APIs
remain compatibility/oracle surfaces and delegate to one-element batches rather
than retaining a second mutation implementation. Exceptional publication
recovery performs a cold namespace reconciliation; an unclassifiable failure
poisons the batch.

A retained payload-store owner also keeps an in-memory index of payload
observations already completely SHA-256 verified under the cooperative lease. A
later scan may skip re-reading an immutable payload only when its digest name and
exact `dev`, `ino`, type/mode, link count, owner/group, size, mtime, and ctime
still match, and only while the exact payload-store identity-marker inode remains
the lease anchor. New files, replacements, metadata-changed files, new process
owners, and every `ReadOnlyInspect` snapshot perform complete hashing. Cache
replacement occurs only after the whole namespace scan and final lease/root
proofs. Diagnostic hashed/reused counters do not enter canonical snapshot
identity.

The combined runtime matrix proves one construction scan across many puts,
move-only/busy/release behavior, a 32-file shipping folder pass, same-inode
mutation, guaranteed atomic inode replacement, exact repair, marker replacement,
restart-cold verification, and forensic-cold verification. The merge also caught
an old-signature recovery call; the fix deliberately supplies no warm cache to an
exceptional recovery scan.

Directional measurements from the exact rev0944 source: 256 distinct 4 KiB
payloads took about 1.14 seconds through one retained batch and about 3.23 seconds
through one-element batches. A 64 MiB-plus-4 KiB snapshot took about 0.243 seconds
cold and 0.0022 seconds warm, with zero warm payload bytes hashed. These are
cloudtainer observations, not broad product qualification.

Important limits remain. Every new batch or snapshot still walks, opens, and
stats the complete namespace. A large bounded local pass retains the exclusive
cooperative lease until its local segment ends. Batch-created payloads are
conservatively hashed once by the next retained scan before entering the
store-wide warm cache. The cache is process-local and there is no persistent
exact metadata index or rotating full-byte scrub. New local content is still read
once by the folder observer and again during durable insertion. This revision
does not add changed-block reuse, payload/partial reclamation, rename, directory
semantics, multi-share ownership, or live public-overlay qualification.


## Rev0943: descriptor-streamed local admission and remote publication

The authoritative restart page is the release-root `BOOTSTRAPROSE.md`. This
hidden README preserves deeper history and implementation detail; it must not be
used to infer a different mission.

Rev0943 removes complete-file C++ strings from the shipping folder observation,
payload-store insertion, and remote materialization path. A local regular file
is opened beneath the retained root and hashed with bounded positional reads.
The same descriptor survives through pathname reproof and is copied into the
private content store while SHA-256 is independently recomputed. Remote apply
opens the exact digest-named durable payload and streams it through the existing
rooted atomic publication state machine.

The public publication interface is deliberately descriptor-specific. It accepts
one borrowed regular-file descriptor, its exact observed metadata, and expected
SHA-256. It preserves the caller's file offset, verifies the source before and
after the copy, verifies the destination extent, and stops before namespace
publication on mutation or identity mismatch. A draft generic public writer
callback was rejected because it would have admitted arbitrary code while the
publisher retained a private temporary descriptor and root authority.

Ordinary share setup still defaults to 64 MiB. A deployment may explicitly
select up to 4 GiB, independently of the 4 MiB wire-range and 64 MiB response-page
limits. The real reconciliation process test transfers 64 MiB plus 4 KiB across
sixteen ranges and a fresh-process continuation, then materializes exact bytes
without a whole-file C++ allocation. Four GiB remains an unqualified policy
ceiling, not a performance or reliability claim.

The audit also corrected a cloudtainer validation defect: the unfinished revision
had split into two source trees, with GCC validating one branch and ASan another.
Rev0943 consolidates the actual implementation and independent tests into one
canonical tree and reruns every release gate there. Results from sibling trees
are diagnostic only.

Important limits remain. New local bytes are read once for observation and again
for durable insertion. Payload-store snapshots and mutation admission still
traverse and hash durable content, which can amplify many-small-file work. A
one-byte edit still retransmits the complete file as sequential ranges. Sparse
layout is not preserved. Multi-gigabyte ENOSPC/quota/restart behavior, live public
Tor/I2P operation, reachability/garbage collection, rename/directory semantics,
and ordinary-user conflict/restore UX remain unqualified or absent.


## Rev0908: Resilio replacement mission, Tor SOCKS5, and I2P SAM

The shipping C++ sender no longer assumes that every peer is a numeric TCP
endpoint. One typed stream-routing boundary now establishes a reliable byte
stream by one of three explicit routes and then hands that stream to the existing
mutual-TLS file-delivery protocol:

- `direct`: numeric IPv4 or unscoped IPv6 TCP;
- `tor`: a checksum-valid Tor v3 `.onion` service through local SOCKS5; or
- `i2p`: an I2P destination through a retained SAM 3.1 STREAM session.

`send-one` and `send-batch` expose the same route grammar. The TLS client no
longer owns raw TCP dialing, while the former numeric endpoint API remains a
compatibility wrapper over a one-shot direct connector. A bounded I2P batch
retains one SAM session and creates fresh STREAM sockets; a bounded Tor batch
uses a command-scoped isolation token with Tor's current `<torS0X>0` SOCKS
username format. Remote onion and I2P names are never submitted to the process
resolver.

Inbound operation is also explicit. A Tor receiver profile validates the exact
v3 onion identity and virtual port and requires the real TLS listener to be on
loopback; the Tor daemon remains the onion-service publication owner. An I2P
receiver natively retains a SAM session and `STREAM FORWARD` control socket for
the bounded command lifetime. The forward target and SAM bridge must be
loopback, and `SILENT=true` prevents SAM from injecting a remote-destination line
in front of the TLS record stream.

The transport audit corrected several failures that would have undermined an
anonymous-network product:

- a syntactically plausible 56-character onion label now has its Tor v3 version
  and checksum verified before SOCKS authority is spent;
- Tor SOCKS and I2P SAM endpoints are loopback-only because those control
  protocols are plaintext by default and AnonSync does not yet own authenticated
  remote-proxy transport;
- a persistent SAM destination no longer receives the TRANSIENT-only
  `SIGNATURE_TYPE=7` option;
- a dead retained SAM control socket is detected, discarded, and rebuilt only by
  a later caller-authorized batch session rather than poisoning every remaining
  session or triggering a hidden retry;
- I2P stage deadlines default to and may not be shorter than 180 seconds, because
  tunnel construction and stream establishment can legitimately consume roughly
  a minute or more;
- long-term I2P private destinations must be read from an effective-user-owned,
  single-link, exact-mode-0600 file through a descriptor-based bounded reader;
- route tokens are bounded and protocol-injection characters are rejected;
- route secrets and private destinations are omitted from JSON telemetry; and
- an existing duplicate `transport` JSON key in `send-one` was removed.

A new C++ connector test exercises direct TCP, Tor method negotiation,
format-zero circuit isolation, checksum rejection, SAM session creation and
reuse, stale-session recovery, persistent-destination option construction,
absolute deadline expiry, and inbound SAM forwarding. A new multi-process test
runs the shipped executable through modeled SOCKS5 and SAM bridges while carrying
the real TLS 1.3 mutual-authentication and exact file-delivery protocol. It
proves outbound Tor, outbound I2P, validated inbound Tor publication, and native
inbound I2P forwarding with exact destination bytes.

This revision materially improves route readiness but does **not** yet make
AnonSync a Resilio replacement. The largest product gaps remain a continuous
folder daemon, recursive scanning and filesystem watching, bidirectional
multi-file reconciliation, directory/delete/rename/symlink semantics, blockwise
large-file resume and delta transfer, peer discovery and NAT/relay behavior,
multi-peer scheduling and backoff, selective-sync placeholders, permissions and
platform metadata, bandwidth controls, invitations/key lifecycle, and desktop or
service administration. Tor publication is configured externally rather than
owned through the Tor control protocol; I2P identity generation/rotation and
route discovery are also not yet productized.

The next C++ vertical slice should be a durable long-running folder supervisor
that owns configured folders and peers, combines watcher hints with periodic full
scans, enqueues changes, schedules multiple routes, survives restart, and exposes
clear service state. The existing evidence and crash rules should constrain that
supervisor without becoming a substitute for it. See
`RESILIO_REPLACEMENT_TOR_I2P_TRANSPORT_BOUNDARY_AUDIT_rev0908.md` and
`REVISION_NOTES_rev0908.md`.

## Rev0907: absolute command budgets, exact idle closure, and safe lease horizons

`send-batch` and `serve-batch` now require both a finite session count and a
finite whole-command runtime. One absolute steady-clock cutpoint begins before
manifest, store, listener, membership, and TLS preflight; each new session's
connect, handshake, request, receipt, and shutdown deadlines is clamped to it.
The boundary is cooperative rather than a hard preemptive kill: poll-driven
network work is bounded, while elapsed synchronous SQLite/filesystem/crypto work
is charged at the next observation.

The policy is no longer embedded only in the 3,600-line CLI translation unit. A
new typed C++ session-supervisor owner validates bounds, creates deadline plans,
classifies sender/receiver terminal states, and derives the necessary durable
claim-lease horizon. Single-session commands use the same executors with one
session; batch commands cannot become an implicit daemon, sleep loop, or retry
engine.

The real process spine exposed a composition defect: after all ready deliveries
settled, the sender could authenticate, find no work, emit zero application
bytes, and close cleanly, while the receiver treated that exact session as
failure. The receiver now reports `authenticated_peer_closed_idle` only when
peer identity is authenticated and every request, inbound, and receipt frontier
remains untouched. This means no durable delivery authority was spent; it does
not prove the peer queue or catalog was empty.

A second deadline audit found that the client could authenticate after consuming
its request budget and still begin a durable claim. The client now re-observes
the request-admission deadline before the first claim. A real TLS regression
proves clean expiry creates no operation ID, claim, prefix, frame, body, receipt,
or dispatch attempt. A later transactional check immediately before prefix
acceptance remains future work for synchronous claim work that starts before but
finishes after the cutpoint.

The former 30-second default claim lease also contradicted the protocol: the
default 10-second staged session permits receipt waiting through 40 seconds, even
before durable clock movement is considered. The sender now derives the minimum
from the receipt horizon plus the exact outbox clock policy. Current defaults
require 641 seconds for 5-second stages and 661 seconds for 10-second stages. An
explicit shorter lease is rejected before deployment, database, payload, or TLS
authority opens. These are necessary lower bounds, not completion guarantees;
process descheduling, SQLite waits, local application work, and suspend remain
explicit gaps.

Clean GCC 14 and Clang 17 Debug registries each pass **227/227**. A focused
Clang 17 ASan+UBSan lane passes the supervisor, real TLS transport, SQLite owner,
file-delivery service, and multi-process CLI spine **5/5**. The next product
frontier is a deadline-aware transactional claim-to-prefix guard followed by a
durable typed supervisor across scan, reconcile, schedule, transfer, apply,
repair, and retention.

## Rev0906: bounded causal session supervision and oldest-ready dispatch

The product executable can now drain or accept more than one authenticated
conversation without becoming an unbounded daemon. `send-batch` and
`serve-batch` require an explicit `--max-sessions` bound in `[1, 256]`. The
single-session commands delegate to the same executors with a bound of one, so
there is no parallel database, payload, TLS, clock, claim, effect, or receipt
path. The sender freezes one manifest/store/TLS/payload cutpoint and creates
fresh staged deadlines for each session; the receiver retains one listener and
refreshes anchored membership between sessions. Aggregate JSON reports every
session and the exact bounded stop reason.

The new two-delivery process test exposed a serious liveness flaw. Canonical
outbox storage order—destination plus SHA-256 operation ID—was also being used as
dispatch priority. A causally later operation could sort before its predecessor,
receive an authenticated `receiver_evidence_pending` receipt, be released, and
be chosen first again. Dispatch now selects the oldest available durable intent
by `enqueued_generation`, with destination and operation ID only as tie-breakers.
Canonical hash order remains unchanged for attestation. Permanent wire and
payload policy is still validated for every matching candidate before any lease;
the full suite caught and prevented an initial refactor that weakened that rule.

One bounded sender and receiver invocation now settles two causally ordered files
through real TCP/TLS processes, exact request/receipt frames, durable receipts,
and exact destination bytes. Clean GCC 14 and Clang 17 Debug registries each pass
**226/226**. A focused Clang 17 ASan+UBSan lane passes the SQLite owner,
file-delivery service, and multi-process TLS spine **3/3**. This remains a
bounded transport supervisor, not a daemon or complete synchronization product:
continuous scanning, a durable scheduler with fairness/backoff/shutdown,
directory/tombstone/rename semantics, indexed anti-entropy, retention/GC,
cross-store cutpoints, key lifecycle, and a formal anonymity/metadata threat
model remain open.

The repository remains on bundled SQLite 3.53.3. SQLite 3.53.4 and its official
hashes were identified, but trusted archive bytes could not be imported through
the cloudtainer's permitted media bridge; the dependency was intentionally left
unchanged. See
`BOUNDED_CAUSAL_SESSION_SUPERVISOR_AND_OUTBOX_PRIORITY_AUDIT_rev0906.md` and
`REVISION_NOTES_rev0906.md`.

## Rev0905: forensic observation, valid SQLite filename families, and one dependency trust record

`status` is now an observation capability rather than a disguised maintenance
operation. Earlier product status constructed the same mutable SQLite owners as
operational commands. Merely asking what was present could acquire write-capable
connections, run durable profile reconciliation, create or remove sidecars,
checkpoint or recover WAL state, and `fsync` payload bytes and directories. That
violated the product rule that observation must not fabricate a newer cutpoint.

Rev0905 adds an explicit read-only descriptor-rooted VFS mode and exact-schema
observer transactions for the replica, file-effect, membership, and membership-
anchor stores. A forensic connection remains publicly `SQLITE_OPEN_READONLY`,
`query_only`, and unable to write, truncate, persist shared memory, map pages,
delete deployment files, or delegate mutating file controls. For WAL databases,
the retained `-wal` is copied under before/after inode-and-metadata checks into a
bounded anonymous `memfd`; SQLite may mutate or retire that private copy while
the deployment bytes remain untouched. Exclusive locking keeps the WAL index in
connection-local memory, and the public I/O surface is deliberately version 1 so
`xShmMap` and `xFetch` are structurally unreachable. Payload inspection similarly
uses a shared lease without marker creation or durability synchronization.
Process adversaries preserve and compare the main, journal, WAL, SHM, payload,
and directory metadata before and after status, and reject attempts to escape the
forensic capability.

The sanitizer audit then found a severe VFS-composition defect in both normal and
forensic paths. The wrapper delegated `xOpen` with an ordinary
`std::string::c_str()`. SQLite's Unix VFS retains that pointer and later treats it
as an `sqlite3_filename`, whose hidden filename-family storage is used by
`sqlite3_uri_*()` and `sqlite3_filename_*()`. WAL initialization therefore read
past the string allocation under ASan. Adding extra NUL bytes would have copied
an undocumented representation rather than satisfying the API contract.

Each private registration now owns one `sqlite3_create_filename()` family for
the descriptor-rooted main, rollback-journal, and WAL names, caches the exact
`sqlite3_filename_database()`, `sqlite3_filename_journal()`, and
`sqlite3_filename_wal()` views, and passes only those views to the delegated Unix
VFS—including pre-open inspection. The family is freed only after every wrapped
file is closed and the VFS is unregistered. The source-policy audit rejects a
return to plain-string delegation. Focused strict ASan/UBSan tests now pass the
same product and WAL/shared-memory lanes that exposed the overflow.

This revision also removes a separate build-integrity split. One strict bundled-
SQLite profile now selects the vendor tree, binds semantic and source identity,
requires an exact five-file regular non-symlink inventory, hashes all retained
files, drives native configure and always-run pre-build verification, generates
private C++ constants, and attests the live linked runtime. The first runtime
evidence object was refactored from repeated heap-backed copies to process-
lifetime `std::string_view` fields. Active implementation projection v3 now
includes `cmake/`, so build authority is part of the release's advertised source
identity; rev0905 and later must declare v3 while historical packages preserve
their original projection semantics.

The clean GCC 14 and Clang 17 Debug registries each pass **226/226**, and the
focused GCC 14 ASan/UBSan lane passes **4/4**. The database-open policy audit
passes **37/37**;
bundled profile, native build-gate, and projection adversaries are registered in
the same full registry. This remains a Linux-specific, self-attested release,
not a hostile-root-proof immutable snapshot, a cross-store transaction, or a
complete synchronization/anonymity product. The bundled engine remains SQLite
3.53.3; the 3.53.4 update should remain an isolated dependency revision with all
VFS, process, crash, corruption, sanitizer, and package lanes repeated. See
`FORENSIC_STATUS_AND_SQLITE_FILENAME_FAMILY_AUTHORITY_AUDIT_rev0905.md`,
`BUNDLED_SQLITE_SINGLE_PROFILE_ATTESTATION_AUDIT_rev0905.md`, and
`REVISION_NOTES_rev0905.md`.

## Rev0904: descriptor-rooted SQLite authority without lock revocation

The selected SQLite path is now carried into one private descriptor-rooted VFS.
Main, rollback-journal, WAL, and SHM names are mediated relative to a retained
deployment directory; anonymous spill, multiply linked family members, named
delete-on-close, VFS substitution, hostile cleanup replacement, and context or
namespace escape fail closed. Every accepted connection proves its exact VFS
object and wrapped live main-file handle before evidence reads or durability
synchronization.

The audit corrected a severe flaw in the first version of that design. It had
retained a second descriptor for the main database inode. Traditional POSIX
record locks are process-associated, and closing any descriptor for the file can
release locks held through SQLite's own descriptor. Rev0904 removes that
auxiliary lifetime. Pre-open inspection for one product authority delegates its
short-lived read to the same bundled Unix VFS before that authority opens its
connection; SQLite can therefore apply its process-wide deferred-close lock
workaround even when another same-inode connection is live. Post-open reads and
syncs use the authority's existing `sqlite3_file` under the connection mutex. A
fork adversary proves a real RESERVED lock survives inspection and VFS teardown.

Mount-namespace identity was also insufficient: a file bind mount can replace a
family member inside the same namespace while preserving `st_dev`. The VFS now
freezes the parent `statx` mount identity and requires each existing family
member to remain on that mount using an allocation-free observer that opens no
lock-bearing inode. The cloudtainer exercised an actual same-namespace bind
mount over the WAL name; VFS access/open rejected it and preserved the foreign
bytes. A second witness bind-mounted the approved main inode onto its own name,
preserving device, inode, and bytes while changing only mount identity; the
public namespace proof rejected that subtler substitution too.

Focused checks pass 25/25 and 90/90; source audits pass 61/61 and 34/34.
Clean GCC 14 and Clang 17 Debug registries each pass 221/221, the focused
ASan/UBSan lane passes 2/2, and a Clang-discovered readiness-publication race in
an inherited-process test now passes 64/64 parallel stress runs. This is still
not hostile-root proof, cross-store atomicity, or a complete
synchronization/anonymity product. See
`SQLITE_DESCRIPTOR_ROOTED_LOCK_AND_MOUNT_FAMILY_AUTHORITY_AUDIT_rev0904.md` and
`REVISION_NOTES_rev0904.md`.

## Rev0901: complete SQLite genesis images and identity-first recovery admission

SQLite store birth no longer exposes an empty or partially initialized selected
main-file pathname. Each role is now created as a private, filename-free,
schema-empty in-memory database; exact deployment binding and complete role
genesis are committed there first. SQLite's serialized main image is then
captured, bounded, sealed, and published at the selected pathname with immutable
create-new/no-replace semantics. The published image is re-opened as an exact
bound bootstrap candidate, reconciled to file-and-parent durability, promoted
from its self-contained rollback image to the operational WAL profile, and
re-attested before use.

`init-resume` now classifies present SQLite candidates before ordinary role
ownership. A rollback-mode image must be a complete SQLite main file with no
`-journal`, `-wal`, or `-shm` sidecar; a WAL candidate may retain its WAL family
but may not carry a rollback journal. Every present store proves exact
record-selected deployment identity on retained handles before any candidate is
promoted, any role state is inspected, or any missing store is created. The
process corpus covers twelve crash/recomposition scenarios, including sealed
rollback-image recovery, contaminated sidecar refusal, and rejection of an
unbound but otherwise valid SQLite main file.

The audit also narrowed detached TLS membership owners to genesis construction:
anonymous images cannot publish membership policy or advance the trusted
anchor. The detached deployment-binding primitive itself now requires a
writable, schema-empty database using MEMORY journaling; an empty SQLite
filename alone is insufficient because anonymous disk-backed temporary
databases also have no exposed filename. A redundant five-second busy timeout
was removed from the private single-connection genesis path.

The clean GCC 14 Debug registry passes **221/221**, the deployment-binding audit
passes **26/26**, and a separate focused ASan/UBSan lane passes **4/4**. The
largest remaining local-authority gap is a descriptor-rooted capability that
binds preflight, open, SQLite sidecars, and owner lifetime to one live deployment
directory; hostile directory-entry replacement remains outside the current
proof. Separate WAL databases are still not atomic as a set, and the bundled
SQLite 3.53.3 should be advanced to the 3.53.4 patch release in an isolated,
fully revalidated dependency revision. See
`ATOMIC_SQLITE_GENESIS_IMAGE_AND_RECOVERY_ADMISSION_AUDIT_rev0901.md` and
`REVISION_NOTES_rev0901.md`.

## Rev0900: durable bootstrap record and exact idempotent resume

Initialization now has explicit authority before the final deployment manifest
exists. Fresh `init` publishes a deterministic hidden bootstrap record before
mutating any selected store. Its payload is the byte-exact canonical future
manifest, still self-bound to the exact final manifest path and existing
self-digest. Record reads are bounded, no-symlink, namespace-checked, and
reconciled to exact file-and-parent durability before they can authorize work.

`init-resume --manifest ABSOLUTE_JSON` uses only that record-selected deployment.
It identity-attests every present store before role-state inspection or missing
creation, and it can fill a partial set only while every present resource and
the files root remain at bootstrap genesis. A complete advanced deployment can
regain a lost final manifest; an advanced partial set cannot be recomposed.
Once the final manifest exists, resume is deliberately identity-only: it refuses
missing stores and cannot initialize schema or reconcile membership under the
name of idempotence.

The audit also corrected an initially weak restart boundary: a visible record or
final manifest after an indeterminate parent-directory sync is now accepted only
after immutable-file reconciliation proves exact bytes and directory durability.
Source audits were refactored around the shared authority frontier, and a stale
bounded-reader allowlist failure was retained as intermediate evidence. The
clean GCC 14 Debug registry passes 221/221, a focused authority lane passes
12/12, nine adversarial resume scenarios pass, and a separate ASan/UBSan focused
lane passes.

The largest remaining bootstrap defect is precise: SQLite main-file birth and
deployment binding are not one durable publication, so a crash between them can
strand an unbound main file. Descriptor-rooted deployment authority,
cross-resource coordination, a forensic bootstrap inspector/quarantine flow,
and the broader supervisor/synchronization/privacy product remain open. See
`CRASH_RECOVERABLE_BOOTSTRAP_RECORD_AND_IDEMPOTENT_RESUME_AUDIT_rev0900.md` and
`REVISION_NOTES_rev0900.md`.

## Rev0899: store-attested common birth and fresh-only bootstrap

The product manifest is no longer the sole witness that a store set belongs
together. Fresh bootstrap now mints a checked 256-bit deployment ID, computes
the exact canonical manifest digest before store creation, and persists that
same identity inside every selected SQLite role and the product payload lease
anchor. A canonical manifest over independently valid stores is therefore not a
committed deployment.

The deployment manifest is version 2 and commits role-specific SQLite
application IDs, required store-internal binding, and fresh-only adoption. Every
SQLite database carries an exact STRICT singleton binding row for deployment,
manifest, role, database path, folder, local actor, application ID, and a
length-framed digest. Replica, file-effect, TLS-membership, and membership-anchor
databases also have distinct header-level application-ID fences. Every normal
open proves the exact opened filename, header, schema, temporary-shadow absence,
singleton row, fields, and digest before constructing the role owner.

Init now preflights the complete selected namespace before its first mutation:
manifest, database main files, and `-journal`/`-wal`/`-shm` sidecars must be
absent, while payload and delivery roots must be empty. The product payload root
uses a v3 identity marker binding deployment ID, manifest digest/path, folder,
actor, and lease protocol; product bootstrap refuses to legitimize pre-existing
payload bytes. This intentionally fails closed rather than adopting rev0898
stores.

The process proof independently recomputes manifest and binding digests and now
covers canonical manifest forgery, same-role and cross-role database swaps,
foreign payload-root substitution, orphan sidecars, and pre-seeded roots, in
addition to clock recovery and real mutual-TLS file delivery/settlement. The
new deployment-binding audit passes 20/20; database-open, bootstrap, and payload
source audits pass 16/16, 19/19, and 33/33. The complete GCC 14 Debug registry
passes 219/219.

Interrupted init can still leave correctly bound but uncommitted resources and
has no inspect/resume/quarantine workflow. Freshness preflight has races against
noncooperating writers, WAL is not atomic across the separate databases, the
unkeyed binding does not resist a hostile local writer, path authority is not
fully descriptor-rooted, and status is not a forensic read-only export. The
product still lacks a bounded supervisor, causal filesystem semantics,
chunking/resume, GC/indexing, at-rest encryption, and an anonymity threat model.
The full audit and primary-source research are in
`STORE_SET_BIRTH_ATTESTATION_AND_FRESH_BOOTSTRAP_AUDIT_rev0899.md`; exact changes
and nonclaims are in `REVISION_NOTES_rev0899.md`.

## Rev0898: explicit store-set bootstrap and manifest-bound operation

The product spine now has one named bootstrap authority. `anonsync_replica
init` validates a complete store set, prepares an immutable deployment-manifest
name, initializes the selected replica, payload, effect, membership, and anchor
owners, and publishes the manifest last. Every normal command requires that
manifest and derives all local paths, folder identity, actor identity, and
payload ceiling from its exact canonical bytes. Raw store-path and local-identity
options can no longer be mixed into status, clock, enqueue, membership, send, or
serve operations.

The manifest has a bounded exact schema, a domain-separated SHA-256 self-digest,
opened-path binding, strict UTF-8 and duplicate-key rejection, exact field and
policy closure, and byte-for-byte canonical re-encoding. Its writer proves both
the 16 KiB read ceiling and its own strict-JSON/UTF-8 contract before any store
is created. Copied, tampered, noncanonical, policy-incompatible, or path-mixed
configuration therefore fails before store access. The manifest is a
last-published operational commit marker and explicitly does not claim that the
individually durable resources form one cross-resource transaction.

Operational SQLite and payload opens are now uniformly existing-only. The
payload store has an explicit, non-defaulted open disposition, so status,
enqueue, and send cannot mint a folder identity marker by pointing at an empty
directory. Only `init` retains creation authority. Every command result names
the exact deployment-manifest digest.

The strict JSON parser was extracted into a small shared leaf so the manifest
and broad runtime codec use one parser without pulling the runtime monolith into
a narrow authority boundary. The process proof now covers bootstrap collision,
path overlap, copied and tampered manifests, detached stores, empty replacement
payload roots, profile mismatches, clock recovery, real mutual TLS, exact file
publication, receipt, and settlement. The complete GCC 14 Debug registry passes
217/217.

The manifest still binds configuration more strongly than common birth. Stores
do not yet persist one shared deployment identifier, and interrupted `init`
needs inspect/resume/quarantine semantics. Ancestor symlink and mount rebinding,
write-capable WAL status observation, a bounded supervisor, causal filesystem
semantics, GC/indexing, at-rest encryption, and a real anonymity threat model
remain open. The full assessment and primary-source research are in
`EXPLICIT_STORE_SET_BOOTSTRAP_AND_MANIFEST_AUTHORITY_AUDIT_rev0898.md`; exact
changes and nonclaims are in `REVISION_NOTES_rev0898.md`.

## Rev0897: explicit clock recovery and fail-closed database targeting

The product spine can now inspect and recover its owned outbox clock without
claiming delivery work. `clock-observe` samples under the replica SQLite
writer lock and publishes only the exact clock cutpoint; a newly detected
rollback, source change, boot change, namespace change, synchronization gap, or
drift violation is returned as durable quarantine state rather than being
hidden behind a work-path exception. `clock-recover` requires the exact current
observation generation and binds one fresh owned observation as the new anchor.
The same exact-CAS update and staged re-attestation path is shared with lease
operations, so the CLI does not mint a second recovery authority.

The database-open boundary was also corrected. Observation, recovery, status,
and send operations no longer carry implicit `SQLITE_OPEN_CREATE`; a mistyped
path fails without creating a main file, WAL, or shared-memory sidecar. File
existence is not treated as authority either: an existing zero-byte placeholder
is refused instead of being initialized, and an existing-only open verifies
that the persistent journal profile is already WAL rather than silently
rewriting a wrong SQLite target before exact schema attestation. SQLite usually
returns a diagnostic connection handle even when open fails, so the product now
keeps that handle in a distinct exception-safe candidate owner, closes it on
every rejection path, proves the successful connection is writable, and only
then adopts it. This removes a severe unwind path in which a failed open could
be misread as a live owned transaction and trigger the process fail-stop
instead of the intended diagnostic exit.

`serve-one` now proves its TLS identity, listener, and both existing membership
authorities before it may create receiver replica or effect stores. The process
proof covers typo/no-create behavior, refusal of pre-existing empty genesis,
byte-preserving rejection of an unrelated DELETE-mode SQLite target through
both observation and bootstrap-capable paths, prevention of the paired-store
creation on that failure, normal failed-open exit, preflight without orphan
bootstrap, healthy clock publication, durable source-change quarantine,
generation-fenced recovery, repeated-recovery rejection, real mutual TLS
delivery, exact receiver publication, and terminal sender settlement. A new
source audit pins every product database call site's explicit creation and
persistent-profile policy.

The largest remaining product gap is still a bounded durable supervisor loop,
but rev0897 changes what that loop can safely build upon: it can distinguish a
clock block from empty work and can invoke an exact recovery transition instead
of relying on manual SQL or process replacement. Bootstrap is not yet a single
atomic store-set operation; `enqueue-file`, `membership-publish`, and receiver
genesis still retain explicit-in-code creation capability. A future `init`
command should make that authority operator-explicit and bind the related store
identities in one durable deployment manifest.

## Rev0896: attested product status surface

The bounded product executable now has a `status` command. It opens the same
owning surfaces as `enqueue-file`, `send-one`, `serve-one`, and
`membership-publish`, restores durable state through those owners, and emits a
flat JSON condition report for the operator-facing cutpoints: causal evidence,
active and visible operations, outbox lease/clock state, retained payloads,
receiver file effects, and anchored TLS membership.

The process proof now observes the sender before delivery, the sender after the
receipt settles, and the receiver after publication. This closes a product gap
without creating a daemon: a one-shot spine can now report whether work is
queued, whether the outbox is settled, whether payload bytes remain retained,
and whether receiver effect and membership anchors agree. The audit/refactor in
`src/anonsync_replica.cpp` keeps status subordinate to durable owners rather
than adding raw schema queries, and factors paired-option validation plus status
summaries into narrow helpers.

This remains a bounded one-command-at-a-time product surface. It does not yet
implement a durable scheduler, peer discovery, causal directories, tombstones,
renames, reachability/GC, chunking, at-rest encryption, or anonymity.

## Rev0895: first bounded product spine

The newer causal replica owners are now invokable without linking the diagnostic
self-test implementation corpus. `anonsync_replica` exposes bounded one-shot
commands to derive a certificate SPKI, publish anchored membership, enqueue a
durable file operation, send one authenticated delivery, or serve one
authenticated delivery. The production sender proves durable payload
availability, completes numeric-address connect and mutual TLS 1.3, verifies the
expected SPKI/actor, and only then may claim SQLite work. Once the guarded
request-prefix frontier is crossed, transport uncertainty leaves the claim live
and ambiguous; only the exact authenticated receipt can settle it.

A registered process test invokes separate sender and receiver processes with
independent databases, durable payload storage, anchored membership, real TCP,
mutual TLS, receiver filesystem publication, and terminal receipt settlement.
It found and corrected fresh-membership bootstrap, request-frame-ceiling, and
container clock-authority composition defects that library-only tests had not
exposed.

`send-one` uses the fail-closed system clock by default. The paired
`--operator-clock-authority-id` and `--operator-clock-uncertainty-ns` options
are an explicit deployment assertion for containers where clock discipline is
owned externally but hidden from the process; they are not measurement or
attestation. Destination parent directories must already exist because causal
directory/tombstone/rename semantics are not yet implemented.

This remains a one-conversation spine, not a daemon. It does not claim
continuous scheduling, discovery, GC/indexing, at-rest encryption, anonymity,
unlinkability, private-interest overlap, endpoint hiding, or traffic-analysis
resistance. The full mission/gap analysis is in
`MISSION_PRODUCT_SPINE_ASSESSMENT_rev0895.md`; sender cutpoints and nonclaims are
in `PRODUCT_SPINE_TLS_CLIENT_AUDIT_rev0895.md`; exact changes are in
`REVISION_NOTES_rev0895.md`.

## Rev0892: independently anchored membership and owned payload availability

Rev0891 made TLS membership an append-only SQLite authority and accepted an
optional caller-retained chain anchor. That still left the rollback witness as
free input to the same API that served membership, without executable crash
ordering or a separately owned persistence path. Rev0892 adds a second SQLite
owner and a coordinator with an explicit two-commit protocol: membership commits
first, no resulting capability escapes, and the independent anchor store must
cover that exact generation/digest cutpoint before a move-only accepted-session
authority can be emitted. Restart reconciliation closes the intentional crash
gap; exact compare-and-swap, append-only transition history, whole-history
reconstruction, and final current-state reproof prevent a stale capability from
being knowingly returned after a concurrent publisher wins.

The accepted TLS server now requires the anchored capability type. Every
terminal result binds the exact membership generation and chain plus the durable
anchor generation, transition sequence, and transition digest. Composition
rejects identical database names and distinct names that resolve to the same
filesystem object, including hard-link aliases. This is a useful accidental-
misconfiguration fence, not proof of separate media or administration. Joint
rollback of both stores, malicious same-process mutation, signed enrollment,
hardware monotonicity, and live revocation remain unclaimed.

Rev0892 also retires the last production outbound file-payload callback.
`SyncReplicaFilePayloadSnapshot` owns bounded content-addressed bytes behind
immutable shared state. A separate `SyncReplicaFileContentInventory` owns,
validates, sorts, deduplicates, and folder-scopes only the available digests.
The SQLite owner receives that value, never borrowed caller views, and selects
the first policy-compatible outbox intent whose content is present inside the
same `BEGIN IMMEDIATE` claim transaction. Missing content is skipped without
creating an attempt, claim ID, lease, retry release, or generation change, so an
unavailable canonical head cannot repeatedly consume claim authority and starve
later available payloads. Post-selection contradictions exact-release the same
claim before failure propagates.

The durable TLS-policy connection/backend implementation was also extracted into
one shared profile used by membership and anchor owners. This removes duplicated
SQLite authority policy while retaining complete schema, exact serialized-handle
generation, transaction, journal, and synchronous-mode re-attestation. Both
owners retain the cube's shared `SqlitePathFamilyGuard`, so ordinary live
main-file rename/replacement, symlink-family drift, and SQLite-reported movement
fail closed before policy authority is returned. This is live process-local
namespace evidence, not storage-media or reboot provenance.

Detailed invariants, failure matrices, research, resource analysis, and
nonclaims are in `TLS_DURABLE_MEMBERSHIP_ANCHOR_AUDIT_rev0892.md`,
`FILE_PAYLOAD_SNAPSHOT_AUTHORITY_AUDIT_rev0892.md`, and
`REVISION_NOTES_rev0892.md`.

## Rev0891: durable membership history and retained TLS context

Rev0890 made post-handshake membership a pure lookup in a canonical immutable
snapshot, but the snapshot itself remained freely constructible configuration.
Rev0891 adds the missing durable source: an append-only SQLite owner binds one
folder/local actor, reconstructs every retained generation, requires exact
compare-and-swap publication under `BEGIN IMMEDIATE`, and emits a move-only
accepted-session capability only from committed state. Every TLS terminal result
now names the exact generation, snapshot digest, prior chain digest, and current
chain digest.

A separately retained `(generation, chain_digest)` anchor detects whole-database
rollback or a fork through that point. The internal chain is deliberately
unkeyed and no external anchor store is claimed. The owner is a complete
O(history + retained entries) correctness oracle, not yet the scalable
production reader.

The database boundary was tightened during audit. Exact schema closure catches
arbitrary-named indexes/triggers attached to authority tables and connection-
local TEMP triggers. A dedicated connection profile disables unsafe schema
execution, extensions, attachments, dirty reads, and ignored CHECK constraints,
and is re-attested inside every transaction. WAL requires `FULL`; rollback
journals require `EXTRA`, without overclaiming the underlying VFS or hardware.

The review also found and fixed a severe ceiling edge: the crossing append could
previously commit beyond a restoration hard limit and brick all later reads.
Admission is now checked against exact retained totals before insertion. Return-
authority allocation also occurs before commit, so allocation failure rolls the
candidate policy back.

The accepted server no longer borrows a raw `SSL_CTX*`. A move-only wrapper
retains the OpenSSL reference with `SSL_CTX_up_ref`/`SSL_CTX_free`; lifetime is
owned while concurrent context mutation remains explicitly unsupported.

Detailed invariants, failure matrices, research, and nonclaims are in
`TLS_DURABLE_MEMBERSHIP_AUTHORITY_AUDIT_rev0891.md`,
`TLS_SERVER_CONTEXT_RETENTION_AUDIT_rev0891.md`, and
`REVISION_NOTES_rev0891.md`.

## Rev0890: immutable membership authority at the live TLS frontier

Rev0889 completed the first accepted TCP/mutual-TLS/file-delivery session but
left the final certificate-key-to-actor decision in a caller-supplied
`std::function`. That callback ran after cryptographic authentication while the
accepted descriptor and `SSL` object were live, immediately before application
authority was minted. A comment requiring stable backing state could not make
arbitrary callback code pure, bounded, or non-reentrant.

Rev0890 replaces that seam with `SyncReplicaTlsMembershipSnapshot`: a validated,
canonical, immutable value for one folder, local actor, positive policy epoch,
and complete exact SPKI-to-actor set. It sorts and deduplicates pins, permits
explicit multi-pin rotation overlap, rejects receiver-device reflection, caps
entry count, and binds the complete set to a domain-separated digest. The server
takes the snapshot by value, checks its service identity before `accept4`, uses
pure exact lookup after verified SPKI derivation, re-proves the accepted socket
before channel construction, and records policy epoch/count/digest in every
terminal result.

Real TLS tests now cover canonical digesting, malformed and duplicate policy,
moved-from misuse, cross-folder/cross-actor pre-accept rejection, valid-certificate
unknown-member rejection, and complete publication/receipt/settlement under the
exact snapshot. Two source audits guard the immutable composition and inventory
every remaining explicit callback boundary. OpenSSL trust callbacks remain part
of the caller-owned handshake configuration; the removed callback is the
separate AnonSync post-handshake membership decision.

The deep analyses are in
`TLS_IMMUTABLE_MEMBERSHIP_SNAPSHOT_AUDIT_rev0890.md` and
`CALLBACK_AUTHORITY_BOUNDARY_AUDIT_rev0890.md`. The next required authority is a
durable, provenance-checked, anti-rollback membership configuration owner that
publishes these snapshots only after commit. Revision scope and nonclaims are in
`REVISION_NOTES_rev0890.md`.

## Rev0889: pre-byte accepted TLS authority and exclusive one-run receiver

Rev0888 completed exact nonblocking request/receipt framing once a caller had
already supplied an authenticated `SSL*`. Two authority gaps remained on either
side of that correctness island. The receiver could consume a complete
application frame before discovering that its selected service had no file-
effect role, and successful one-conversation exchange left the local channel
capability reusable. Outside the exchange, no production C++ owner proved the
listener, atomically accepted a child, bounded the mutual-TLS handshake, or
mapped a verified certificate key to an authorized actor epoch.

Rev0889 closes both seams. `preflight_inbound_channel_or_throw` revalidates the
exact live authenticated channel and receiver effect role before the first
application byte is reserved. The service repeats that preflight at the complete-
frame durable frontier; early admission never becomes a lease over later SQLite
or filesystem authority. `SyncReplicaFileTlsReceiverSession` then freezes exact
request/receipt cutpoints and owns one channel through one run. Move, success,
timeout, peer close, exception, explicit discard, destruction, and replacement
all leave exactly one truthful owner and terminalize the local application
capability. A real TLS fixture queues ciphertext and proves invalid receiver
configuration consumes zero bytes, mutates no durable cutpoint, and emits no
response.

The outer `serve_one_sync_replica_file_delivery_tls_session_or_throw` owner starts
from a move-only capability for one exact Linux listening socket lifetime. It
uses `accept4(SOCK_NONBLOCK | SOCK_CLOEXEC)`, owns the accepted descriptor and
`SSL` object, drives a bounded nonblocking TLS 1.3 mutual-authentication
handshake, derives the verified peer SPKI, requires explicit SPKI-to-actor-epoch
membership, constructs the authenticated channel, and transfers it into exactly
one receiver session. Accept expiry, a silent peer, plaintext on the TLS port,
and a certificate-valid but unmapped peer all terminate before durable receiver
authority. The complete loopback path composes real TCP accept, mutual TLS,
membership, canonical request, SQLite evidence/effect ownership, atomic file
publication, exact receipt, sender settlement, and canonical digest convergence.

Socket policy was refactored rather than duplicated. `FD_CLOEXEC` is a separately
re-proved mutable policy in the generic socket-lifetime leaf, and one absolute-
deadline `poll` owner is shared by accept, handshake, and shutdown. Post-mint
`O_NONBLOCK`/`FD_CLOEXEC` mutation fails before accept. A moved-from listener is
ordinary local misuse and throws before process fail-stop, while an active
capability inherited across a process boundary still fail-stops. Poll wakeups
remain advisory; only the subsequent exact kernel/OpenSSL operation classifies
progress, close, or error.

Transport shutdown remains subordinate to application settlement. Only a
complete local receipt permits the accepted owner to attempt bounded
`close_notify`; timeout or failure cannot erase `ReceiptSent`, and transport
closure never claims that the sender received or durably applied the receipt.
The inner session still does not own raw transport; the outer accepted-session
owner supplies that lifecycle explicitly.

The detailed ownership and failure analyses are in
`TLS_RECEIVER_SESSION_OWNERSHIP_AUDIT_rev0889.md` and
`TLS_ACCEPTED_SESSION_AUTHORITY_AUDIT_rev0889.md`. A separate deep audit found a
major remaining liveness gap: staged and published payloads permanently consume
finite admission budgets, and enough enrolled identities or normal long-lived
churn can still exhaust the folder. The safe reservation/fairness/reclamation
design is in `RECEIVER_STAGING_FAIRNESS_AUDIT_rev0889.md`.

Rev0889 completes a narrow durable isolation slice rather than only telemetry.
Exact schema v3 re-derives and binds actor/device usage, persists per-device
count/byte policy across actor epochs, deterministically applies folder then
device limits, migrates exact v2 under one rollback-tested SQLite transaction,
and keeps device-specific diagnostics receiver-local behind the generic wire
capacity receipt. The review also removes redundant full-payload/canonical and
O(history) public-projection copies from internal mutation paths. See
`FILE_EFFECT_CAPACITY_ACCOUNTING_AUDIT_rev0889.md` and
`FILE_EFFECT_DEVICE_ISOLATION_MIGRATION_AUDIT_rev0889.md`. This does not create a
stable membership principal, total disk quota, fair scheduler, pre-transfer
reservation, or reclamation authority. Revision scope and nonclaims are in
`REVISION_NOTES_rev0889.md`.

## Rev0888: exact first-prefix backpressure and one write state machine

Rev0887 added a receiver-owned conversation from complete authenticated request
through durable idempotent file publication and terminal receipt. One important
transport asymmetry remained: the receipt body was resumable, but its encrypted
8-byte record-length prefix was synchronously driven inside the begin factory.
A genuine nonblocking WANT at that first operation was fail-closed, yet it became
an exception rather than exact typed state.

Rev0888 unifies prefix and body in one heap-stable, move-only
`SyncReplicaTlsRecordWriteContinuation`. The new preparation factory validates
bounds, freezes exact prefix/body bytes, reserves the authenticated stream, and
returns before any `SSL_write_ex`. Each advance performs at most one 64 KiB
operation, retains exact arguments across WANT, accepts partial-write progress,
and exposes prefix completion before any hidden body operation. An untouched
prepared owner releases cleanly; abandonment after any attempted operation,
including a zero-byte WANT, poisons the stream.

The sender's guarded dispatch API remains compatible: it drives only through the
complete prefix while SQLite claim authority is held, commits that cutpoint, and
releases before body backpressure. The receiver uses the pre-prefix owner after
its durable effect decision, so first-prefix WANT is now retained through the
shared absolute-deadline poll loop without holding SQLite authority.

Receiver diagnostics now distinguish no attempted write, attempted zero-byte
prefix WANT, partial prefix, accepted prefix, partial body, and complete local
receipt. A real TLS test saturates the response path after durable publication,
forces first-prefix `WANT_WRITE`, expires the receipt deadline with zero accepted
prefix/body bytes, preserves exactly one visible effect, leaves the sender claim
live, and makes the old application stream unusable.

The retired synchronous prefix helper and stale body-only lexical assumptions
were removed. Exact invariants, failure matrix, OpenSSL retry constraints,
rejected alternatives, and nonclaims are in
`TLS_PREFIX_WRITE_CONTINUATION_AUDIT_rev0888.md`.

The first complete suite also exposed a separate validation race: the SQLite
connection-authority retirement probe could publish ticket one before its worker
started, copy that already-published value into `atomic::wait`, and block until
the external timeout. The worker now advances from completed tickets, and a
deterministic pre-start-ticket regression exercises the former deadlock schedule.
That audit is in
`SQLITE_CONNECTION_AUTHORITY_TEST_SYNCHRONIZATION_AUDIT_rev0888.md`; revision
scope and remaining production gaps are in `REVISION_NOTES_rev0888.md`.

## Rev0887: receiver-owned request, durable effect, and receipt cutpoints

Rev0887 introduced one strict-nonblocking receiver composition owner. It reads a
complete bounded authenticated request, invokes the file-delivery service only
at the complete-frame frontier, preserves the durable idempotent decision, then
re-attests the live channel and emits the exact receipt under an independent
absolute deadline. Malformed requests, abandoned responses, and post-effect
failures destructively discard the application stream rather than allowing the
next record to inherit ambiguous conversation state.

It also froze the exact OpenSSL record-I/O policy observed at authentication so
later option, mode, read-ahead, verification, quiet-shutdown, or shutdown-state
mutation cannot borrow old peer/exporter authority. See
`TLS_RECEIVER_EXCHANGE_CUTPOINT_AUDIT_rev0887.md`,
`TLS_RECORD_IO_POLICY_AUTHORITY_AUDIT_rev0887.md`, and
`REVISION_NOTES_rev0887.md`.

## Rev0886: authentication-time transport anchor and exact resumable writer

Rev0885 proved the exact Linux socket lifetime only when strict record I/O
began. The authenticated `SSL*` itself remained mutable: a caller retaining the
raw handle could replace its BIOs after authentication and let the new
transport inherit peer-SPKI/exporter authority from the old channel. Retaining
only a descriptor proof also missed in-place `BIO_set_fd` mutation.

Rev0886 makes the authentication-time transport part of the channel capability.
The shared state retains both exact read/write BIO objects with `BIO_up_ref` and,
for direct Linux socket BIOs, directional `SOCK_STREAM` lifetime identities.
Every later channel-authority use rechecks BIO pointer, in-place descriptor, and
kernel socket lifetime before trusting session, record, poll-target, delivery-
service, or durable-owner authority.

Retained BIOs are released with `BIO_free_all`, not head-only `BIO_free`. This
matters for the supported caller-managed path where the exact top BIO can own a
filter chain; the final anchor release now destroys the complete detached chain
instead of leaking downstream BIOs. A counted filter-over-socket fixture proves
both objects survive SSL replacement while retained and are later freed exactly
once.

The generic socket leaf is refactored into immutable
`SyncSocketLifetimeIdentity`. `O_NONBLOCK` is mutable readiness policy, not
object identity. Strict mode uses a lifetime–`F_GETFL`–lifetime sandwich; a
blocking direct socket rejected before I/O does not poison caller-managed reuse,
while policy loss after framing progress or pending WANT poisons.

Rev0886 also adds an exact incremental write continuation at the accepted-prefix frontier. The parent continuation kept
only a length promise and accepted caller-owned body bytes later, so a different
same-length frame could cross the durable prefix/body cutpoint. It also poisoned
a healthy nonblocking stream on routine `SSL_ERROR_WANT_READ` or
`SSL_ERROR_WANT_WRITE` because no exact retry capability existed.

`SyncReplicaTlsRecordWriteContinuation` now owns the exact bounded frame in one
heap-stable private state before the prefix can succeed. Each
`advance_or_throw()` issues at most one 64 KiB body request, retains the exact
pointer and length across WANT, exposes a typed advisory readiness target in
strict mode, accepts successful partial-write progress, and releases the
exclusive Write reservation only after the complete body succeeds. Moving the
wrapper cannot relocate pending storage; abandoning it after prefix acceptance
poisons the stream. The one-shot writer and file-dispatch path delegate to this
single state machine.

The compiled TLS 1.3 matrix forces `SSL_set_fd`, in-place `BIO_set_fd`, socket
close/`dup2` ABA, lost `O_NONBLOCK`, same-length caller mutation, pre-WANT and
caller-managed target queries, and two-megabyte nonblocking backpressure through
WANT, wrapper move, bounded resume, and exact peer-byte completion.

The revision now also owns the wait between exact WANT frontiers. One shared
`anonsync_sync_replica_tls_poll` leaf composes both read and write continuations
with an absolute `steady_clock` deadline, target reproof after `EINTR`/`EAGAIN`,
upward-rounded bounded `poll(2)`, a post-wakeup cutpoint check, and at most one
OpenSSL operation per wakeup. `POLLERR`, `POLLHUP`, and `POLLNVAL` remain advisory;
OpenSSL and the continuation own close, truncation, retry, and poison semantics.
A real TLS matrix proves deadline retention, prefix/body separation, clean close,
signal interruption, saturated write retry, bounded write-poll progress, and exact
two-megabyte peer bytes.

The release verifier was also corrected at its own authority boundary. It now
rejects actual `build/`, `build-*`, and `cmake-build-*` directory components while
allowing legitimate evidence basenames such as `build-shape-observation.json`.
An executable CTest policy matrix prevents recurrence of both the false rejection
and the previously accepted real build tree.

This still does not authorize concurrent raw SSL/BIO/fd mutation, prove hidden
transport inside custom/filter BIOs, provide strict non-Linux lifetime evidence,
turn local TLS write completion into peer receipt, or supply the missing bounded
receiver/event-loop/effect owner. Exact final build, sanitizer, stress, audit,
lineage, and package evidence is under `REVISION_EVIDENCE/rev0886/`.

Primary-source constraints, state machines, failure matrices, rejected
alternatives, and deliberate nonclaims:

- `TLS_TRANSPORT_ANCHOR_AUTHORITY_AUDIT_rev0886.md`
- `TLS_INCREMENTAL_WRITE_AUDIT_rev0886.md`
- `TLS_DUPLEX_POLL_AUTHORITY_AUDIT_rev0886.md`

`CLOUDTAINER_BUILD_RETENTION_AUDIT_rev0886.md` records the build-tree
retention failure that exhausted the cloudtainer, the conservative cleanup
boundary, and the quota/expiry policy needed to keep validation viable.

## Rev0885: exact socket-lifetime authority at TLS readiness frontiers

A file-descriptor number is a reusable table slot, not the identity of the
kernel socket that an authenticated TLS session was established over. Rev0884
rechecked that strict TLS BIO descriptors still named nonblocking sockets, but
a close followed by `dup2()` could replace the occupant with another
nonblocking stream socket at the same integer. The old check would pass while a
pending `SSL_read_ex()` retry or a post-prefix body write crossed onto the wrong
transport lifetime.

Rev0885 adds an OpenSSL-independent, opaque
`SyncSocketReadinessIdentity`. On Linux it binds the descriptor number, socket
type, `fstat` device/inode/mode, and a mandatory nonzero `SO_COOKIE`; observation
double-checks stat identity and cookie across the capability capture. Exact
reproof rejects closure, descriptor reuse, object substitution, loss of
`O_NONBLOCK`, non-sockets, and unavailable evidence. Unsupported platforms fail
closed rather than silently accepting a weaker tuple. Only the advisory
descriptor is public, so callers cannot compare a convenient subset or promote
process-local kernel evidence into protocol identity.

The authenticated TLS state now owns one readiness proof beside its exclusive
`Idle/Read/Write` record reservation. A pending WANT retry performs system-call
reproof only, preserving the exact OpenSSL retry frontier. A fresh read step
revalidates the peer/session binding and recaptures the current BIO/socket proof.
The strict writer performs the same live recapture between accepted prefix and
body. `pending_readiness_or_throw()` returns a typed readable/writable poll
target only after WANT, re-proves before disclosure, and the later retry proves
again. A stale target makes the pending operation impossible to resume and
poisons the stream.

The read continuation also caps each public body request at 64 KiB. This bounds
application-requested progress per event-loop step without claiming a bound on
OpenSSL internals or wall-clock time. The socket proof was refactored into its
own small library and runtime test rather than leaving Linux syscalls duplicated
inside the OpenSSL adapter.

The final compiled matrix includes exact descriptor-reuse rejection after WANT,
at poll-target lookup, after successful prefix/body progress, and between the
writer's accepted prefix and body. It also retains the existing TLS 1.3 pin,
exporter, process/thread affinity, stable-buffer retry, close, truncation,
duplex-reservation, and file-dispatch cases. Exact build, test, stress,
sanitizer, audit, projection, lineage, and package evidence is under
`REVISION_EVIDENCE/rev0885/`.

This is still not the production receiver. Raw descriptor mutation must be
serialized by a higher-level owner; `SO_COOKIE` is process-local kernel evidence,
not a cryptographic credential. There is no poll/epoll service, resumable
write-WANT state machine, authenticated accept/connect owner, durable
receive/effect composition in `anonsync_core`, terminal effect receipt,
exactly-once remote execution, or implemented anonymity property. The next
useful slice is one bounded event-loop owner carrying a canonical operation
through receiver SQLite admission, atomic visible effect, authenticated
terminal receipt, and sender settlement.

Primary-source constraints, failure matrix, refactor rationale, adversarial
cases, and deliberate nonclaims: `TLS_SOCKET_LIFETIME_AUTHORITY_AUDIT_rev0885.md`.

## Rev0884: heap-stable incremental TLS receive and duplex ownership

A nonblocking TLS read is not stateless merely because no application byte was
returned. OpenSSL can report `SSL_ERROR_WANT_READ` or `SSL_ERROR_WANT_WRITE` and
require the same read arguments on retry. The previous one-shot reader had no
continuation owner for that frontier; a naïve movable reader with inline prefix
storage could also relocate the buffer that OpenSSL expects to remain exact.

Rev0884 adds a move-only `SyncReplicaTlsRecordReadContinuation` whose private
state lives in one heap allocation. Prefix bytes, body bytes, offsets, limits,
terminal state, reservation, and the authenticated channel owner therefore keep
one stable identity while the public wrapper moves. Each advance performs at
most one `SSL_read_ex`, immediately classifies failure with `SSL_get_error`, and
returns typed progress for ordinary bytes, WANT_READ, WANT_WRITE, complete
frame, or clean pre-frame peer close. WANT does not advance offsets; the next
advance reconstructs the same pointer and length.

The cleanup frontier is explicit. Destruction before any attempted read releases
the reservation cleanly. Abandonment after any attempted read, including WANT,
poisons the channel because the pending operation cannot truthfully be replaced.
A close-notify before any frame byte yields `PeerClosed` and permanently closes
the channel without fabricating a frame. Close after prefix/body progress is
truncation and poisons. Empty and over-limit prefixes fail before body
allocation. Strict mode proves direct socket BIOs and `O_NONBLOCK` at begin and
every retry.

The transport owner is also simplified. A write-only active boolean is replaced
by one duplex `Idle/Read/Write` reservation. Reads, writes, generic record I/O,
and the delivery-authority live verifier cannot re-enter the same `SSL*` while
a continuation owns it. This intentionally gives up concurrent full-duplex use
until AnonSync has a serialized two-direction owner capable of proving it safe.
The legacy one-shot reader delegates to the same incremental state machine and
fails rather than spinning on nonblocking readiness.

The compiled TLS 1.3 matrix covers wrapper moves after prefix and body WANT,
fragmented records, clean and ambiguous abandonment, duplex exclusion,
readiness loss, clean close, truncation, bounds, non-socket descriptors,
foreign-thread fail-stop, and legacy delegation. The exact final build, test,
stress, sanitizer, source-audit, and package results are recorded under
`REVISION_EVIDENCE/rev0884/`.

This is not yet a production receiver. There is no poll/epoll service, bounded
complete-frame queue, authenticated accept/connect owner, durable receive/effect
composition in `anonsync_core`, peer receipt from transport completion, or
exactly-once remote execution. The next valuable step is to place this reader
and the exact first-prefix writer under one bounded event-loop owner and carry a
canonical operation through receiver SQLite/effect authority to a terminal
effect receipt.

Primary OpenSSL research, state machine, failure matrix, audit/refactor, and
deliberate nonclaims: `TLS_INCREMENTAL_RECEIVE_AUDIT_rev0884.md`.

## Rev0883: no-throw continuation affinity and destructor fail-stop

Rev0882 made an unfinished TLS record a move-only, state-owned capability, but
one no-throw path still escaped the authority model. An active continuation
could be moved into another C++ thread and abandoned there. Its destructor
called `poison_noexcept()` and silently changed the shared stream's poison and
reservation flags before any process/thread owner check. Final `SSL_free()` was
fenced, but the first foreign mutation had already occurred.

Rev0883 centralizes the authenticated state's no-throw process/thread proof and
requires it before completion, poison/abandonment, or final SSL release. A
foreign-thread finish, destructor, or move-assignment over an active target now
fails stopped before it can mutate shared TLS state. Same-owner abandonment
still poisons the stream because a complete prefix without its exact body cannot
be reused safely.

The compiled TLS matrix now transfers an active continuation into a foreign
`std::thread` inside an isolated child process. The foreign-thread destructor
must terminate with the exact capability-violation exit code; surviving the
thread join is a test failure. The focused executable reports 75/75 checks. The
structural audit grows to 32 checks and requires the centralized fence,
process-then-thread ordering, mutation ordering, public contract, runtime case,
package surface, and explicit nonclaims.

This review also rejected an unrelated 578-line nonblocking receive prototype
that appeared in a mutable workspace. It failed its first clean compile, changed
public APIs, and supplied no matching runtime matrix. Rev0883 was reconstructed
from the independently verified rev0882 archive instead of granting that branch
authority by presence. The receive direction remains the next major engineering
need, but it should arrive as an explicit event-loop state machine with partial
prefix/body offsets, WANT_READ/WANT_WRITE ownership, backpressure tests, and
clear crash semantics.

OpenSSL's own documentation warns that most objects are not safe for
simultaneous use and that `SSL_free()` may release the SSL object, BIOs, cipher
lists, and session references. This supports the conservative rule that cleanup
is live owner mutation, not bookkeeping exempt from affinity. It does not prove
race freedom. ThreadSanitizer, a receiver loop, resumable WANT-state ownership,
durable body progress, shipped-executable integration, peer receipt, and
exactly-once remote effect are not claimed.

Fresh rev0883 evidence records 192/192 registered tests, 61/61 audit-named
tests, and 5,199/5,199 focused checks in GCC Debug, Clang 17 Release with C++
`-Werror`, and GCC ASan/UBSan with leak detection and bundled SQLite
instrumented. Repeated gates add 5,940/5,940 mixed authority checks and
7,500/7,500 targeted TLS checks. Seventeen selected source audits pass
509/509 checks, including the corrected exact inventory of 15 inherited-process
consumer translation units and 27 spawn sites.

Primary design, online-source audit, failure matrix, rejected-scope record, and
deliberate nonclaims: `TLS_CONTINUATION_AFFINITY_AUDIT_rev0883.md`.

## Rev0882: exact first-prefix authority and exclusive TLS record ownership

Rev0881 returned a canonical file-delivery frame only after re-attesting its
claim under a SQLite writer. The returned C++ value could nevertheless wait in
an ordinary queue while that exact claim expired, was released, was settled, or
was replaced. The generic TLS writer did not know which durable attempt had
once authorized those bytes. This was a real authority gap: historical proof
that a frame was constructible is not live permission to begin that attempt.

Rev0882 adds a narrow composition owner between the file-delivery service and
the authenticated TLS transport. It freezes and reconstructs the bounded
outbound request, frame, and digest outside SQLite; reacquires the exact claim
under `BEGIN IMMEDIATE`; re-proves the live channel and claim-derived request;
then writes only the complete encrypted eight-byte application-record length
prefix while the writer guard excludes competing sender transitions. Once that
prefix has been accepted by OpenSSL, the guard commits and releases before the
potentially large immutable frame body is transferred.

The cutpoint is deliberately truthful. OpenSSL completion is not peer receipt,
receiver admission, durable evidence, filesystem effect, or sender settlement.
A failure before successful prefix return poisons the stream and exact-releases
the claim because no body was supplied through a reusable capability. A commit
or body failure after the prefix leaves the exact claim live and ambiguous;
only a terminal receipt, explicit exact transition, or owned-clock expiry may
retire it.

The TLS writer is now one state machine. `begin_sync_replica_tls_record_write_`
`or_throw()` returns a private, move-only continuation that exclusively owns the
unfinished record. The authenticated SSL owner rejects a second begin, an
ordinary record write, or a record read until the continuation finishes or is
abandoned. Wrong body length, readiness loss, failed live-session reproof, or
abandonment permanently poisons the stream. This corrected a serious defect in
the first rev0882 draft, where exclusivity existed only as caller convention and
a same-thread operation could interleave another record.

The SQLite/TLS composition refuses blocking or opaque BIOs. It requires direct
`BIO_TYPE_SOCKET` read and write BIOs, observable descriptors, successful
`getsockopt(SOL_SOCKET, SO_TYPE)` socket proof, and `O_NONBLOCK` on both
directions immediately before prefix progress and again before body progress.
Descriptor visibility or `O_NONBLOCK` alone is insufficient: a descriptor BIO
can wrap a non-socket object. A readiness contradiction therefore fails before
stream bytes and exact-releases the claim. The generic caller-managed TLS API
remains available outside this database critical-section policy.

A refactor removes two security-sensitive duplicate implementations. Generic
and file delivery now share one exact claim-to-request constructor, including
destination, operation, actor, kind, claim ID, and attempt checks. The one-shot
TLS writer delegates to the same begin/continuation machinery as the composed
path. The new composition remains a separate small library, so the file service
does not absorb OpenSSL and the TLS transport does not absorb SQLite or effect
policy.

Fresh evidence includes one complete 192/192 CTest invocation, the complete
61/61 audit block, 5,198/5,198 focused checks under GCC Debug, Clang 17 Release
`-Werror`, and GCC ASan/UBSan with bundled SQLite instrumented, 5,920/5,920
checks across 100 repeated authority executions, a separate 100-run/7,400-check
TLS cutpoint stress gate, and 505/505 selected lexical audit checks. Lexical
audits remain architecture and package hygiene, not semantic proof.

The largest remaining gap is liveness and restart ownership after prefix
progress. Rev0882 intentionally poisons on `SSL_ERROR_WANT_READ` or
`SSL_ERROR_WANT_WRITE`; it has no event-loop continuation that preserves the
same immutable OpenSSL write arguments, no durable `dispatch_started` state,
and no lease heartbeat while a large body is in flight. The shipped executable
also still does not use the newer causal, file-effect, receipt, and TLS
composition stack. The next valuable milestone is a small replica service with
a real receiver loop and crash injection across prefix, body, receiver commit,
publication, receipt, and settlement frontiers.

Primary design, audit, research, failure matrix, and deliberate nonclaims:
`TLS_FIRST_PREFIX_DISPATCH_AUDIT_rev0882.md`.

## Rev0881: local path capability, exact retry release, and live namespace context

A canonical AnonSync path is global evidence; a destination filesystem's
component ceiling is local effect capability. Rev0880 allowed those two layers
to meet too late. A portable operation whose component exceeded the retained
root's `{NAME_MAX}` could consume payload storage, effect generation, causal
evidence, and repeated sender leases before publication finally failed with
`ENAMETOOLONG`.

Rev0881 moves that proof before effect authority. The file-effect owner first
validates exact operation and payload bytes, then applies a receiver-local
encoded-byte ceiling derived conservatively from the retained root's frozen
`statvfs().f_namemax` and positive `_PC_NAME_MAX` observations. A provably
unrepresentable path returns `DestinationPathBlocked` from an unchanged,
attested transaction. It inserts no effect row, retains no payload, advances no
generation, admits no causal evidence, and touches no namespace entry.

The outer file-delivery protocol explicitly advances to version 2 and adds the
typed `EffectPathBlocked = 9` disposition. Pre-effect denials carry the exact
request and unchanged receiver effect cutpoint, but neither an effect ID nor an
inner causal receipt. Version-1 readers reject the frame version rather than
silently interpreting an outcome they never negotiated.

Validated nonterminal receipts no longer leave a live attempt idle until lease
expiry. The sender releases the exact destination/operation/claim through the
outbox owner's clock and a local, strictly positive, bounded retry policy. The
same transition handles callback, channel-reproof, validation, encoding, or
digest failures after claim minting but before frame escape. Missing, stale, or
expired claim identity fails closed and cannot fabricate release provenance.

Retained directory capability now also freezes the calling thread's live Linux
mount-namespace context. `SyncPosixMountNamespaceAuthority` retains
`/proc/thread-self/ns/mnt`, compares its documented `st_dev`/`st_ino` identity
with a fresh current-thread handle on every proof, and sticky-revokes after any
contradiction. Capture occurs before pathname traversal, so a later
`unshare()`/`setns()` cannot use a descriptor from one namespace as authority in
another.

An audit/refactor consolidated the process-identity and outbox-clock boot-ID
readers into one strict, bounded `sync_system_epoch_identity` leaf. Missing or
permission-hidden procfs evidence is typed at that boundary. The current clock
codec still requires a concrete 36-byte boot UUID, however, so unavailable boot
identity throws before the SQLite owner can durably quarantine it. Likewise,
the arbitrary payload callback is followed by channel reproof but not yet an
exact post-callback outbox-claim attestation. Both gaps are named rather than
hidden.

The file-effect schema remains version 2. Boot UUID and mount ID were
intentionally rejected as mandatory permanent root identity because they are
runtime-ephemeral and would lock an exact database after an ordinary reboot
without an authorized rebind ceremony. Legacy rev0878-rev0880 staged rows whose
names were already impossible are not silently deleted; they require a future
repair protocol.

Primary design and research record:
`FILE_EFFECT_PATH_CAPABILITY_AUDIT_rev0881.md`.

## Rev0880: observed mount-boundary authority and shared resolution owner

Rev0879's descendant fence compared `st_dev`. That blocks another filesystem
but cannot distinguish a same-device bind mount. Rev0880 classifies the actual
running POSIX resolution capability and, on Linux, combines `openat2` with
`RESOLVE_NO_XDEV` and descriptor `statx` mount identity. No kernel version is
used as capability evidence. The exact observed mode is frozen in the retained
root authority, re-proved before use, and carried with every verified duplicated
root descriptor.

The cloudtainer supplies a concrete witness: `/proc` and `/proc/bus` have the
same `st_dev`, but `/proc/bus` is a distinct mount. The focused runtime test
proves that this crossing is rejected when the host exposes either the
`openat2` or `statx` fence. Systems without those observed interfaces retain the
portable device/inode baseline and its explicit same-device-mount nonclaim.

This revision also consolidates the absolute authority, rooted publication, and
legacy absolute publication component loops into one exception-safe POSIX
syscall owner. Domain-specific owner/mode and member-file rules remain in their
callers. A separate audit found and corrected a descriptor leak: when the
post-duplication authority reproof failed, the untransferred duplicate was not
closed.

Mount IDs remain live, runtime-ephemeral evidence and are intentionally absent
from the durable v1 root-attestation digest. A live rebind is detected, but
restart-stable mount-object identity requires a future boot-epoch and authorized
root-rebind protocol. The shipped executable still does not use this newer
effect path.

Primary design and research record:
`MOUNT_BOUNDARY_AUTHORITY_AUDIT_rev0880.md`.

## Rev0879: retained root authority for effect-terminal File publication

Rev0878 composed live authenticated delivery, exact causal projection, bounded
payload staging, immutable publication, and effect-terminal receipts for one File
operation. Its file-effect owner still persisted only normalized root-path text.
A same-path directory replacement between calls could therefore redirect a later
publication into a different tree while the database retained the same spelling.

Rev0879 closes that POSIX boundary. The effect owner now retains one move-only,
process/thread-affine root directory capability, freezes device/inode,
credentials, mode, filesystem and mount observations, persists the canonical
attestation digest in exact file-effect schema version 2, and performs
reconciliation/publication from a duplicated root descriptor plus a strict
canonical relative path. Root replacement revokes a live owner, and restart
against a different root object fails before existing effect authority is
accepted.

The focused path is now:

`live channel authority → exact active-primary cutpoint → bounded staged payload`
`→ retained root capability → descriptor-relative descendant policy → immutable`
`create-new publication → file/directory durability → rooted reconciliation →`
`root-bound effect cutpoint → effect-terminal receipt → sender settlement`

Every descendant parent must remain on the retained root device, be owned by the
retained effective UID, grant owner read/write/search, and deny group/other
write. These checks occur before temporary inode reservation. The absolute-path
and rooted callers share one atomic publication state machine and one restart
reconciliation state machine.

This revision also removes duplicated security machinery: the local JSONL replay
directory class now delegates to the same generic `SyncDirectoryAuthority`.
Automatic migration from path-only file-effect schema v1 is intentionally
refused because old rows contain no evidence of which directory object owned the
prior effects.

This remains a correctness slice, not a complete sync product. The retained-root
path is POSIX-only, does not yet reject same-device bind mounts, has no authorized
root-rebind protocol, and is not used by the shipped executable.

## The central correction: projection authority must survive until effect proof

An earlier composition checked whether an operation was the active visible
primary in one SQLite snapshot, released that snapshot, and then wrote the file.
A second owner could change causal projection between those steps. The receiver
could therefore publish bytes and construct a terminal receipt from a stale
projection decision.

`SyncReplicaSqliteProjectionGuard` closes that check/use gap. It:

- opens `BEGIN IMMEDIATE` on the causal owner;
- fully restores and re-attests exact state;
- requires the exact generation and cutpoint named by the inner evidence receipt;
- requires the exact retained File operation to be Active, the sole visible
  primary, and free of preserved alternates;
- retains the writer-serializing transaction across filesystem materialization,
  effect-owner re-attestation, and canonical receipt construction; and
- commits only after the exact effect receipt bytes and digest exist.

A changed cutpoint returns no authority and produces `ProjectionBlocked`; it is
not silently upgraded to whatever state happens to be current. A runtime test
uses an independent SQLite connection with zero busy timeout to prove that a
competing causal writer is blocked while the guard is live, succeeds after the
guard commits, and cannot make an old cutpoint mint effect authority.

The guard does **not** pretend that SQLite and the filesystem are one
transaction. A rename or fsync can complete before a later exception or process
exit. The effect owner therefore uses immutable no-replace publication and exact
restart reconciliation. A retry may recognize the exact private durable file and
finish the database transition; it never guesses from a syscall return alone.

SQLite documents that `BEGIN IMMEDIATE` starts a write transaction immediately
and may fail with `SQLITE_BUSY` when another writer is active. SQLite permits
multiple readers but only one simultaneous writer. These properties support the
local serialization point; they do not create a transaction across two SQLite
databases and a filesystem.

- https://sqlite.org/lang_transaction.html
- https://sqlite.org/isolation.html

## Payload and lease authority

The file service now requests only `SyncReplicaValueKind::File` work and gives
the owner both the complete delivery model and the maximum payload size before a
lease can be minted. A canonical File whose committed size exceeds the local
wire/effect policy throws inside the preclaim transaction while attempt number,
claim ID, worker, lease, and cutpoint remain unchanged.

This fixes a concrete liveness waste: an oversized operation could previously be
claimed, fail request construction, remain leased until expiry, and repeat the
same impossible cycle.

The payload callback still runs after a valid durable lease exists. A callback,
post-callback channel proof, request validation, encoding, or digest failure now
releases the exact attempt under the sender owner's clock before rethrowing. The
release delay must be positive and within the fixed retry budget, preventing an
idle lease and a caller-configured immediate spin.

This is still an ambient-authority boundary: a payload callback that can also
reach the outbox owner could mutate the claim and then return valid bytes. The
service re-proves channel authority but does not yet hold an exact dispatch guard
or re-attest the claim after arbitrary code. A production payload-store
capability should remove that overlap rather than relying on a loose O(history)
snapshot check.

## Receiver effect ownership

`SyncReplicaFileEffectSqliteOwner` owns a separate database containing exact
canonical operation bytes, exact payload bytes, effect identity, state
generations, aggregate limits, redundant fields, and a complete structural
cutpoint. Every public operation restores and re-attests the full retained set.
It is deliberately an **O(history) correctness oracle**, not a scalable
production index.

The receiver stages exact bytes before causal admission. This prevents an
operation from becoming evidence-terminal when the receiver cannot retain the
payload required for its effect. It also creates an availability obligation:
authenticated but pending or quarantined work can consume staging capacity. The
current aggregate limits do not yet provide per-peer quota, expiry, reclamation,
or dead-letter authority.

For publication, the effect owner classifies the namespace as:

- absent: create one private immutable file;
- exact and directory-synced: reconcile a prior or concurrent successful effect;
- conflicting: preserve the existing entry and return a nonterminal conflict.

Exact means stable bytes, same effective UID, mode 0600, link count one, regular
file type, file synchronization, directory synchronization, and identity
revalidation. File `fsync()` alone does not necessarily persist the directory
entry, so terminal proof includes the containing directory boundary.

- https://man7.org/linux/man-pages/man2/fsync.2.html

## Live channel authority remains load-bearing

Every file-service entry point accepts
`SyncReplicaDeliveryChannelAuthority`, not public
`SyncReplicaDeliveryChannelContext`. The file orchestrator is an explicit friend
of the nonforgeable capability so it can fail closed before staging, claiming,
or settlement without exposing a public “validate” or “mint” API.

The same opaque authority is passed to the nested evidence service. The outbound
path revalidates it after the arbitrary payload callback and before returning
bytes that claim the original channel binding. Production linkage excludes the
deterministic test mint; the test executable alone links that factory.

The inherited TLS adapter requires TLS 1.3, successful peer verification, exact
ALPN, actor/SPKI pinning, a fresh non-resumed session, no early-data attempt, and
an RFC 9266 exporter binding. It owns an OpenSSL reference, is process- and
thread-affine, and permanently poisons record authority after uncertain partial
I/O or invalid framing.

This remains same-process domain separation. It is not a sandbox against
arbitrary code execution, memory corruption, debugger control, or malicious code
already holding the capability.

## Heart of the mission

The mission is a chain of authorities:

1. **Observation authority:** preserve provenance, capability, and uncertainty
   before any physical observation influences identity or liveness.
2. **Canonical identity:** freeze exact operation bytes and derive one immutable
   ID from them.
3. **Exact causality:** name immediate predecessors; summaries may locate work
   but cannot replace parent evidence.
4. **Actor and membership authority:** authenticate actor/key epochs and define
   enrollment, rotation, revocation, recovery, rollback, and old-epoch treatment.
5. **Durable publication:** bind operation bytes, parent edges, projection,
   payload commitment, dispatch ownership, clock evidence, receiver admission,
   visible effects, and receipts to explicit transitions.
6. **Deterministic projection:** retain evidence independently of active and
   visible state so trust and dependency changes can be re-evaluated.
7. **Bounded dissemination:** own CPU, bytes, identities, dependencies, storage,
   time, retries, and wake work under explicit limits.
8. **Receiver effect ownership:** let a terminal receipt mean one exact,
   idempotent, crash-reconciled visible effect—not merely message receipt.
9. **Privacy authority:** state the adversary and observable metadata before
   claiming anonymity, unlinkability, or traffic-analysis resistance.

The compact invariant is:

> Given the same authorized canonical evidence and trust state, replicas must
> derive the same state; no untrusted input, crash cutpoint, duplicate, missing
> dependency, resource claim, stale projection, schema mutation, stale receipt,
> fabricated channel description, reused TLS object, clock movement, retry
> response, namespace race, migration shortcut, or local pressure decision may
> silently gain authority.

## Cross-store boundary and lock order

Rev0878 has three independent durable domains:

1. the sender/receiver causal SQLite owner;
2. the receiver effect SQLite owner; and
3. the receiver filesystem namespace.

The receive path stages in the effect database and releases that transaction,
performs causal admission, then acquires causal projection guard authority before
materializing through the effect owner. The live overlapping order is therefore
**causal database → effect database → filesystem**. Current effect-owner methods
do not call back into the causal owner, so the implementation has no inverse
nested path. Future composition must preserve one declared lock order; adding an
effect-to-causal callback would create deadlock risk.

Holding the causal writer slot across full-history effect restore and file and
directory fsync is conservative and potentially expensive. It is appropriate for
this reference oracle. A production design should authorize a narrower immutable
projection lease or signed projection token, keep the full-history owner as a
differential oracle, and prove that the indexed path derives the same terminal
cutpoints.

## Root identity is retained; live mount context is now fenced

`SyncDirectoryAuthority` opens an absolute root component by component without
following symlinks, retains the terminal descriptor, and re-proves both that
object and the configured path before authority-bearing work. Any observed
identity, mode, credential, filesystem, mount, or mount-namespace contradiction
permanently revokes the live object. The effect owner binds its normalized path
and frozen durable attestation digest into complete database and publication
cutpoints.

Destination parents are opened relative to a duplicated root descriptor. Linux
uses runtime-observed `openat2(RESOLVE_NO_XDEV)` and, when available, `statx`
mount identity to reject same-device mount crossing. Rev0881 additionally
retains `/proc/thread-self/ns/mnt` before traversal and re-proves the current
thread remains in that namespace. Runtime tests cover root replacement, sticky
revocation, restart against a replacement root, shared-writable descendants,
`/proc` versus the same-device `/proc/bus` mount witness, and a mount-namespace
transition when the host permits unprivileged `unshare()`.

The live mount namespace inode and mount ID are deliberately excluded from the
durable root-attestation digest. They are useful runtime evidence but are not
restart-stable storage identity. An explicit operator/device-authorized root
rebind protocol remains absent; changed durable roots and schema-v1 databases
fail closed.

- https://man7.org/linux/man-pages/man7/namespaces.7.html
- https://man7.org/linux/man-pages/man2/openat2.2.html
- https://man7.org/linux/man-pages/man2/statx.2.html

## Audit and refactor work

Rev0879 adds a 31-check retained-root source inventory covering capability shape,
component traversal, frozen policy and digest, sticky reproof, JSONL delegation,
strict relative paths, descendant policy, shared publication/reconciliation,
schema-v2 binding, SQLite cutpoint ordering, adversarial runtime cases, CMake
ownership, and package inventory. It is explicitly **lexical hygiene, not
semantic proof**.

The local JSONL directory authority is now a thin compatibility facade over one
generic owner. This removes a duplicated syscall and revocation state machine
instead of adding a second security boundary. Neighboring atomic-publication and
JSONL audits were updated to follow the new shared verifier/delegation shape
without weakening their runtime expectations.

Rev0881 adds a dedicated file-effect path-capability inventory and updates the
file-delivery, mount-boundary, process-identity, and outbox-clock audits to track
positive bounded retry policy, pre-effect denial, live mount-namespace context,
and the shared boot observer. The refactor removes two divergent procfs readers;
the audit also records the two unsolved composition gaps instead of treating
source vocabulary as proof. The fresh sanitizer lane caught and corrected a
separate CMake policy-list drift: the new epoch test was instrumented for
compilation but initially omitted from sanitizer runtime linking. The dedicated
audit now requires both entries.

The build graph remains wasteful. CMake now contains 79 library declarations,
98 executable declarations, and 193 `add_test` occurrences, yet semantic centers
still include
approximately 15,167 lines in `sync_domain.cpp`, 9,601 in
`sync_domain_selftests.cpp`, 4,529 in `sqlite_replay_ledger.cpp`, and 3,713 in the
causal SQLite owner. The full rebuild spends far more time compiling these older
monoliths than the new authority slice. Target count has outpaced semantic
modularity.

Correction should proceed by authority boundary rather than arbitrary file size:

- split restore/attestation, transition, serialization, and storage ownership;
- generate repetitive target, sanitizer, and test wiring through CMake helpers;
- retain a fast affected-authority gate plus one complete periodic registry;
- measure header and link fanout before choosing cuts; and
- keep the full-history owners stable as differential reference implementations.

`REVISION_EVIDENCE/` already contains more than 4,500 files and roughly 41 MB
before rev0878 evidence. Each new revision therefore keeps compact in-tree
lineage, source delta, audits, summaries, and hashes. A future externally signed,
content-addressed artifact store should hold bulk logs and historical corpora.

## Historical rev0881 product gap (superseded)

This paragraph is retained as revision history, not current product status.
Rev0881 had no production caller in the then-shipped `anonsync_core` executable
for `SyncReplicaFileDeliveryService`, the newer causal owner, or the TLS channel.
Later revisions composed the shipping `anonsync_sync` service spine described at
the top of this README. The current product gaps are the rev0955 nonclaims above,
not this older correctness-island assessment.

The next product milestone should be one narrow executable with:

`configured folder + pinned peer + stable root capability + TLS 1.3 framed`
`transport + bounded request queue + causal/effect owners + one File operation +`
`terminal response + restart injection at every durable frontier`

Only after that path is operable should the project expand to updates,
tombstones, discovery, relays, group membership, compaction, and privacy
mechanisms.

## Historical rev0881 gap inventory (superseded)

At rev0881, the most important absent authorities were:

- explicit root epochs/rebinding, schema-v1 migration receipts, and repair of
  legacy locally impossible staged effects;
- ordinary update, rename, tombstone, and deletion effects;
- immutable content-object storage separated from mutable path projection;
- per-peer staging quota, expiry, garbage collection, and dead-letter policy;
- payload-store availability classification and exact post-callback claim
  authority before frame escape;
- durable signed/offline-verifiable receiver effect receipts;
- response journaling across sender crash after transmission;
- membership enrollment, monotonic epochs, rotation, revocation, and recovery;
- durable boot-source-unavailable clock evidence, reconnect/event-loop
  transport, negotiation, jitter, attempt limits, permanent rejection,
  dead-letter authority, and wake scheduling;
- third-party gossip, anti-entropy, causal stability, compaction, and rejoin;
- indexed production owners differentially checked against the O(history)
  oracles;
- an explicit privacy/adversary model; and
- externally trusted signed build provenance.

The name “AnonSync” remains an aspiration. Mutual TLS and payload confidentiality
do not hide endpoints, timing, direction, volume, certificates, or all
application metadata, and therefore do not establish anonymity or unlinkability.

## Historical rev0881 evidence and nonclaims

`FILE_EFFECT_PATH_CAPABILITY_AUDIT_rev0881.md` contains the deep defect,
capability split, protocol-v2, retry, namespace, refactor, primary-source
research, rejected-design, and remaining-gap analysis. `RELEASE_GATE.json` and
`REVISION_EVIDENCE/rev0881/` are the authority for compiler, sanitizer, stress,
registry, projection, manifest, and package results.

Rev0881 does not claim use by the shipped executable, normal mutable-file
convergence, deletion, repair of legacy staged poison, restart-stable mount or
boot identity, authorized root migration, Windows path/retained-root parity,
exact post-callback claim authority, durable clock quarantine when boot ID is
unavailable, exactly-once behavior against a privileged or same-UID local
writer, fair hostile-peer staging, independently signed receipts, complete
membership/key lifecycle, complete retry/dead-letter scheduling, nonblocking
transport, production-scale indexed ownership, anti-entropy, compaction,
anonymity, malicious-host defense, full-project
Clang/sanitizer/ThreadSanitizer coverage, externally trusted provenance, or
formal proof.
