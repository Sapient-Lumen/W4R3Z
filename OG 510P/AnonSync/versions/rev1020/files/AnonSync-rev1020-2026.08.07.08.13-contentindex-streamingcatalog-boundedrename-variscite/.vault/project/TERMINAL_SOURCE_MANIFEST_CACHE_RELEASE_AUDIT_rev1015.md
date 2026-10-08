# Terminal source-manifest cache release and in-place checkpoint publication audit — rev1015

## Product reason

AnonSync's first supported workflow is Linux/headless synchronization of multi-terabyte media trees. A completed content-defined source manifest is useful while a ranged transfer is active, but retaining it forever after the terminal range wastes memory. At the hard 8,192-chunk frontier the compact sequence reserves exactly 327,680 bytes. The durable checkpoint already contains the same exact sequence and can rehydrate it after a lost response without rereading source bytes.

Rev1015 therefore makes the completed manifest an active-transfer cache rather than dormant process-lifetime state. It also removes a second avoidable O(chunk count) copy from every durable checkpoint publication.

## Previous shape

The source service retained at most one completed compact manifest. Once built or restored, that vector stayed resident until unrelated source identity displaced it. A terminal range did not release it.

Checkpoint publication also copied the entire pending `SyncReplicaSourceManifestCheckpoint` before calling the payload store. At maximum shape that copy alone requested 327,680 bytes for 8,192 fixed 40-byte records. Publication then still needed the canonical encoded record and an independently parsed committed reproof.

## Retained design

### Caller-owned checkpoint publication

`SyncReplicaFilePayloadStore::publish_source_manifest_checkpoint_or_throw` now accepts a non-const lvalue reference and mutates only the caller-owned bounded candidate with the exact store identity and successor generation. The reconciliation service passes its pending optional in place.

Typed store-lease or atomic-publication deferral leaves that same candidate available for a later owner turn. The durable frontier advances only after exact committed-record reproof. Identity, codec, rooted-reproof, and logic failures remain terminal.

This removes the publication-only candidate copy. It does not remove the canonical encoded record or the independently parsed post-publication reproof.

### Exact terminal release

A terminal ranged response records the exact retained operation whose next offset reaches its total size. Release occurs only after:

1. canonical generation-9 frame assembly has finished, so no borrowed manifest view remains live;
2. every opened source descriptor has been released;
3. the pending complete checkpoint has been published or was already durably exact;
4. the resident cache binds the same operation id, canonical path, content digest, size, and manifest digest; and
5. the process durable witness binds the same complete operation, final byte frontier, and manifest digest.

If checkpoint publication is deferred, if content was merely reused across another operation, or if any exact witness differs, the cache remains resident.

The release counter and released-capacity counter are prepared before cache mutation, preventing diagnostic-counter overflow from reporting failure after the cache was already destroyed.

### Lost-response replay

Destroying process acceleration does not revoke source authority or transfer evidence. A duplicate range request loads the exact checksum-framed complete checkpoint, reconstructs the one compact vector, reopens and re-proves the digest-named payload, and serves the response without source-byte hashing or a new manifest scan.

The cache can therefore be absent while no transfer is active and present again only while replay or continued range service needs it.

### Filesystem-cold observability

`source_manifest_cache_status()` reports whether the cache is resident, its exact causal/content identity, chunk count, retained vector capacity, exact durable-checkpoint availability, complete-checkpoint restorations, and terminal release totals. The accessor performs no filesystem traversal, payload open, checkpoint load, hash, or scheduler advance.

## Executable proof

The ranged reconciliation regression proves one completed manifest is resident and durably discardable before the final range; the terminal direct frame releases exactly its retained capacity; the response still decodes and applies normally; a later duplicate request rehydrates the complete checkpoint; source manifest scan count remains one; and hashed bytes remain the exact original payload size.

The test-only friend also compile-time binds checkpoint publication to a by-reference signature. Existing maximum-shape checkpoint memory tests independently establish that copying 8,192 fixed records requests 327,680 bytes.

## Authority and memory nonclaims

Rev1015 does not eliminate the one active-transfer 327,680-byte sequence, checkpoint encoding, or postpublication parse/reproof memory. It does not measure whole-process RSS, allocator fragmentation, page-cache pressure, or concurrent multi-share growth. It does not add a global chunk index, reduce cold 4 TiB hashing below 131,072 bounded 32 MiB pulses, or reduce the successful durable checkpoint interval below 1 GiB. Identity-preserving rename/move, directory semantics, conflicts, selective-sync UI, ENOSPC policy, Android, and live Tor/I2P qualification remain open.

The next decision remains measurement-driven. If active-transfer cache capacity is immaterial beside frame buffers, page cache, and concurrent services, product priority should return to rename/move and directory semantics rather than building a global index.

## Validation and release

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
