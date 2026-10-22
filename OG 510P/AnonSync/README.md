# AnonSync

## Keep folders converging without making a route into an identity

AnonSync is a C++ peer-to-peer folder-synchronization project: keep useful files converging across a person's machines and chosen peers, including after disconnection, interruption and restart. Its intended first setting is a Linux/headless service for large media trees, where retransmitting a nearly unchanged file or loading every historical operation to process one renamed file can make an otherwise correct design impractical. Direct networking, Tor and I2P are alternative routes to the same authenticated peer and synchronization protocol, not three unrelated products.

The supplied rev1020 is a substantial pre-alpha implementation, not yet the drop-in Resilio Sync replacement it aims to become. Its strongest explanatory thread is the connection between ordinary use and exact state: which bytes are present, which operation they belong to, which local copy may change, and what an interrupted action actually established. Start with the [product entrance][bootstrap], then the mechanisms below; the version shelf preserves the longer history.

## From an observed change to a synchronized file

Consider a media file edited on one machine while another is offline. A watcher notification makes the folder worth checking; it does not prove the file's final contents or authorize a remote overwrite. The early [design stance][early] already distinguishes watching from knowing durable state. The later implementation combines watcher wakeups with periodic repair scans, a durable folder catalog, causal replica operations and a private payload store. The [watcher source][wake] treats queue overflow and watch invalidation as reasons to rebuild observation, rather than interpreting an incomplete event stream as complete history.

These layers answer different questions. The catalog relates an observed local pathname to the synchronized state. Replica operations describe file values, deletions and causal succession across peers. Payloads supply the bytes associated with file content identities. A remotely learned operation does not by itself make those bytes available; for selected files, the transfer path establishes the payload before admitting the operation through its ordinary payload-before-metadata boundary. Rooted file publication then has its own checks. A received message, a retained operation and a changed visible file are not interchangeable acknowledgments.

The point is usable recovery, not merely a larger log. A service must distinguish work still needed from work already committed, and uncertainty from success. The archive's [rev0648 local kernel][kernel] explores that distinction through authorization, one-time reservations and outbox recovery. That snapshot is a local library/CLI and adapter harness, not evidence that every external recipient performed an effect. The later folder product should be read as a further construction with its own owners and failure boundaries, not as a new name for that kernel.

## Selective synchronization is a policy about bytes, not a fake file

A small device need not keep every large media file locally. AnonSync distinguishes materializing a file from retaining its causal metadata without acquiring or publishing its payload. A bounded policy combines a default with component-prefix exceptions; the longest matching path prefix wins. Thus a broad metadata-only branch can contain a smaller included subtree. The actual [policy implementation][policy] walks component boundaries rather than treating every textual prefix as a directory relationship.

The [selective-sync design and implementation account][selection] gives this distinction consequences in both directions. Excluded operations can travel without payloads; reselecting a file uses ordinary reconciliation to acquire the missing bytes. Exclusion does not create a placeholder that looks like a locally available file. Nor should changing selection mint a deletion operation for everyone else.

For an already materialized file, removing the rooted copy is more demanding than changing a flag. The implementation binds policy, catalog, causal state and exact rooted bytes, retains an independently verified private payload, and checks the displaced file again before unlinking. Changed or untracked local files do not become disposable merely because a policy now excludes their path. This reclaims space in the synchronized folder, not necessarily in the whole application: retained private payloads are a separate storage obligation. The design also records a crash window that can leave private recovery residue. Automatic storage-pressure eviction and polished placeholders remain different, unfinished product work.

## Reuse content after an insertion, not just at the same offset

A small insertion near the start of a large file defeats naive fixed-offset reuse: later unchanged bytes move. AnonSync's [content-defined delta design][delta] instead chooses chunk boundaries from the byte stream. Its [gear-hash chunker][chunker] enforces a minimum size, looks for a mask-selected boundary and forces a cut at the maximum, with a finite chunk-count frontier. A boundary hash selects a possible division; it is not the integrity proof for the bytes.

Chunk records carry exact lengths and SHA-256 digests, and completed payloads still face whole-file verification. A receiver can reuse matching predecessor chunks at different offsets rather than download them again. Later revisions extend discovery to currently visible cross-file content and bound the work of projecting, copying and verifying those pieces. A plausible use is revising a large container or media file while retaining most of its content. This explains why the mechanism matters without promising that every media encoding yields good reuse: a change that alters most bytes offers little to reuse, and canonical chunk geometry has its own resolution and capacity limits.

The bounded buffers, durable progress and terminal checks serve different needs. Bounded work lets a retained service resume other duties between expensive steps; durable progress supports restart; terminal verification prevents a collection of apparently useful pieces from being mistaken for the completed target. None alone establishes dense multi-terabyte throughput.

## A rename is inferred conservatively, then recorded causally

Suppose a synchronized file disappears at one path and the same content appears at another. Rev1019 can preserve a causal identity continuation instead of treating every such observation as unrelated deletion and creation. It requires a uniquely matching regular-file source in both the catalog and current replica, an absent old materialized name and a destination with neither a prior catalog entry nor causal heads. It publishes a destination File followed by a causally linked source Tombstone and can reuse the retained payload. There is no special rename-only wire message or durable watcher cookie carrying identity. Read the [rename design][rename] alongside the source-linked bounded-planning account below.

Identical content is not sufficient to prove the user's action. Copying a file and deleting the original can look the same as a rename; multiple same-content candidates introduce ambiguity. AnonSync falls back to ordinary create/delete convergence rather than inventing uniqueness. Its claim is conservative causal continuity, not proof that the operating system executed a particular rename call.

The replica pair and catalog pair commit atomically within their respective databases, not in one cross-database transaction. Remote application is not an atomic filesystem rename either. A crash between the database commits is therefore a real state to reconcile. Restart inference adopts the already-published pair rather than treating the interrupted process's missing final acknowledgment as permission to create another pair.

## What rev1020 makes smaller, and what it does not

[Rev1020's bounded-planning audit][indexed] addresses a concrete scaling mistake: processing one file previously materialized the whole catalog and reconstructed retained replica history. The replacement uses path-local lookups and exact-content indexes returning at most two rows. Zero, one and ambiguous matches are distinct answers; two rows are enough to reject uniqueness, not a complete enumeration of all conflicts. Normalized index values are checked against the underlying immutable operation or catalog value before they influence a rename.

Catalog commits now stream canonical rows rather than retain whole-catalog vectors. That removes catalog-sized row memory, but still reads the catalog globally before and after mutation to recompute its digest. Actual identity-preserving rename publication also streams the current visible projection to check its integrity. A corrupted index that silently omitted a duplicate must not manufacture a unique identity.

The resulting distinction is important: ordinary one-file planning is indexed and avoids complete history reconstruction; publication still pays global integrity I/O; cold owner opening still reconstructs retained authority. “Bounded” names particular memory and work frontiers, not a claim that the entire service is constant-time or independent of history. The [revision notes][revision] explicitly retain this tradeoff rather than presenting a source-size or allocation change as a throughput result.

## Privacy routing and practical readiness

The [transport-boundary design][transport] separates establishing a byte stream from authenticating the peer above it. Numeric direct TCP, Tor through a local SOCKS connector and I2P through SAM have different connection and lifetime rules. A route address is not the peer's cryptographic identity. The latest [product contract][bootstrap] requires a route locked to Tor or I2P to fail rather than silently switch to direct traffic. That requirement is stronger than the earlier transport seam alone: the rev0908 audit still listed a complete anonymity profile as missing. Neither a connector nor this product requirement establishes a blanket anonymity guarantee; the supplied release leaves live public-network qualification open.

The most useful scale evidence is equally specific. The [rev1018 sparse-tree exercise][sparse] describes two retained processes classifying more than 4 TiB of logical sparse-file extent, with the files metadata-only and outbound peers intentionally unreachable. It crosses a directory batching boundary and checks service responsiveness and process memory. It does not transfer 4 TiB of dense media, demonstrate fast delta synchronization or qualify a million-file workload. Read that result for the problem it actually addresses: a very large logical file must not force the program to retain its absent payload in memory.

The remaining product gaps are substantial but concrete: complete and empty-directory semantics, directory moves, understandable conflict handling, storage-pressure recovery, broader platform adapters and polished setup. The Linux daemon's rooted POSIX and lifecycle assumptions do not automatically become Android support. AnonSync is valuable here both as an evolving synchronization implementation and as a record of how difficult it is to keep exact recovery machinery subordinate to ordinary file use.

## Read the history without flattening it

- [Rev0004][early] proposes an invite-only, privacy-oriented appliance with durable indexing and rescans.
- [Rev0648][kernel] concentrates on effect authorization, idempotency and honest local recovery. Those are real engineering concerns, but not yet a usable folder service.
- [Rev1020][bootstrap] makes continuous folder synchronization the governing purpose and explains the latest indexed-rename and streaming-catalog correction.

Read beside [Micromax](../Micromax/README.md) for another investigation of the distance between trust machinery and an ordinary usable workflow, and [BrowserRT](../BrowserRT/README.md) for a different storage setting where a rejected call, preserved bytes and an application-level commit must also be distinguished. These are related problems, not the same implementation.


[bootstrap]: versions/rev1020/files/AnonSync-rev1020-2026.08.07.08.13-contentindex-streamingcatalog-boundedrename-variscite/BOOTSTRAPROSE.md
[early]: versions/rev0004/files/AnonSync-rev0004-2026.03.08.01.18-resiliouimirrorkeepingwatch/README.md
[kernel]: versions/rev0648/files/README.md
[wake]: versions/rev1020/files/AnonSync-rev1020-2026.08.07.08.13-contentindex-streamingcatalog-boundedrename-variscite/.vault/project/src/sync_replica_folder_wake.cpp
[policy]: versions/rev1020/files/AnonSync-rev1020-2026.08.07.08.13-contentindex-streamingcatalog-boundedrename-variscite/.vault/project/src/sync_replica_selective_sync_policy.cpp
[selection]: versions/rev1020/files/AnonSync-rev1020-2026.08.07.08.13-contentindex-streamingcatalog-boundedrename-variscite/.vault/project/BOUNDED_SELECTIVE_SYNC_AND_DEMATERIALIZATION_AUDIT_rev0987.md
[delta]: versions/rev1020/files/AnonSync-rev1020-2026.08.07.08.13-contentindex-streamingcatalog-boundedrename-variscite/.vault/project/CONTENT_DEFINED_DELTA_AND_INSERTION_RESYNCHRONIZATION_AUDIT_rev0994.md
[chunker]: versions/rev1020/files/AnonSync-rev1020-2026.08.07.08.13-contentindex-streamingcatalog-boundedrename-variscite/.vault/project/src/sync_replica_content_defined_chunker.cpp
[rename]: versions/rev1020/files/AnonSync-rev1020-2026.08.07.08.13-contentindex-streamingcatalog-boundedrename-variscite/.vault/project/IDENTITY_PRESERVING_REGULAR_FILE_RENAME_AUDIT_rev1019.md
[indexed]: versions/rev1020/files/AnonSync-rev1020-2026.08.07.08.13-contentindex-streamingcatalog-boundedrename-variscite/.vault/project/BOUNDED_RENAME_CONTENT_INDEX_AND_STREAMING_CATALOG_AUDIT_rev1020.md
[revision]: versions/rev1020/files/AnonSync-rev1020-2026.08.07.08.13-contentindex-streamingcatalog-boundedrename-variscite/.vault/project/REVISION_NOTES_rev1020.md
[transport]: versions/rev1020/files/AnonSync-rev1020-2026.08.07.08.13-contentindex-streamingcatalog-boundedrename-variscite/.vault/project/RESILIO_REPLACEMENT_TOR_I2P_TRANSPORT_BOUNDARY_AUDIT_rev0908.md
[sparse]: versions/rev1020/files/AnonSync-rev1020-2026.08.07.08.13-contentindex-streamingcatalog-boundedrename-variscite/.vault/project/SPARSE_MULTITERABYTE_SELECTIVE_MEMORY_AUDIT_rev1018.md


## Version shelf and preservation

### Supplied snapshots

The reading route above is selective. This shelf retains every supplied snapshot and its original identity.

- [rev0004](versions/rev0004/README.md): 70 preserved members; `AnonSync-rev0004-2026.03.08.01.18-resiliouimirrorkeepingwatch.zip`.
- [rev0107](versions/rev0107/README.md): 157 preserved members; `AnonSync-rev0107-2026.03.18.10.44-previewsufficiencytruthharbor.zip`.
- [rev0212](versions/rev0212/README.md): 619 preserved members; `AnonSync-rev0212-2026.03.21.05.20-ciphertextcustodyrecoverypages.zip`.
- [rev0316](versions/rev0316/README.md): 1,228 preserved members; `AnonSync-rev0316-2026.03.22.13.58-referencebundlefidelity.zip`.
- [rev0413](versions/rev0413/README.md): 1,896 preserved members; `AnonSync-rev0413-2026.03.24.18.58-burstborrowpaybackloom.zip`.
- [rev0504](versions/rev0504/README.md): 2,541 preserved members; `AnonSync-rev0504-2026.03.28.08.48-survivorselfroutingreclosurepath.zip`.
- [rev0648](versions/rev0648/README.md): 381 preserved members; `AnonSync-rev0648-2026.06.18.18.28-relay-authority-preflight-claim-gate-cairn.zip`.
- [rev0700](versions/rev0700/README.md): 1,116 preserved members; `AnonSync-rev0700-2026.07.06.16.31-scheduler-executor-boundary.zip`.
- [rev0799](versions/rev0799/README.md): 979 preserved members; `AnonSync-rev0799-2026.07.15.13.58-finitework-statefusion-readfence-stagingtruth.zip`.
- [rev0904](versions/rev0904/README.md): 6,281 preserved members; `AnonSync-rev0904-2026.07.26.05.38-locksafevfs-mountfamily-readinesscutpoint-jasperbridge.zip`.
- [rev1020](versions/rev1020/README.md): 9,350 preserved members; `AnonSync-rev1020-2026.08.07.08.13-contentindex-streamingcatalog-boundedrename-variscite.zip`.

[Original identities](PROVENANCE.json) · [Back to OG 510P](../README.md)

