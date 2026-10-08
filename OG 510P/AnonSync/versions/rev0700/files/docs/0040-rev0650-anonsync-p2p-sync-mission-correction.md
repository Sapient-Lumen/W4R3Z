# rev0650 AnonSync P2P sync mission correction

## Scope of this linked revision

This revision fixes the cube's mission and roadmap. It intentionally makes no C++ source, binary, capability, fixture, or runtime behavior change. The active executable and active capability manifest remain:

- `bin/rev0648/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3`
- `gateway/rev0648-cpp-ledger-backend-capabilities.json`

Rev0650 exists because rev0649 answered the wrong question. It treated the existing authorization/idempotency machinery as the product. The product is AnonSync itself: a C++ peer-to-peer file synchronization system.

## Heart of the mission

AnonSync is a **Resilio Sync-style peer-to-peer folder synchronization engine** written in C++.

The mission is:

> Given one shared folder and a set of authorized devices, converge those devices on the intended file tree by authenticating peers, comparing content manifests, transferring missing chunks, applying creates/updates/deletes idempotently, preserving conflicts honestly, and recovering after interruption without depending on a central server as the ordinary source of truth.

The core product loop is:

1. **Index:** scan local files safely and produce stable manifests.
2. **Identify:** bind device, folder, peer, and session identities to trusted material.
3. **Compare:** exchange manifest summaries and compute deltas.
4. **Transfer:** request, send, verify, and resume content-addressed chunks.
5. **Apply:** commit file mutations with crash-safe temp/rename/fsync discipline.
6. **Reconcile:** handle conflicts, tombstones, deletes, renames, retention, and restore.
7. **Recover:** after restart, know what is synced, pending, partial, conflicted, deleted, failed, or unknown.

## How to reinterpret the existing cube

The C++ code already built a lot of machinery, but it is a substrate:

- canonical parsing and length-prefixed binding become protection for peer messages, manifests, and sync-operation identities;
- trusted transport context separation becomes the rule that peer/device identity cannot be caller-authored;
- replay/idempotency becomes duplicate suppression for manifest publications, chunk-transfer reservations, file commits, tombstones, and conflict records;
- SQLite/WAL ledger and restore checks become the local sync state store;
- outbox/claim/lease/relay machinery becomes the local scheduler boundary for sync mutations and transfer work;
- signed terminal transitions become evidence that a sync mutation reached a durable terminal state.

These parts are valuable only when tied to concrete sync behavior. They should not keep growing as generic evidence features detached from files, folders, peers, chunks, and conflicts.

## What was missing from the cube's story

The previous mission framing was missing the product noun. For AnonSync, the product nouns are:

- **device** — an authorized participant in a share;
- **folder/share** — the replicated namespace;
- **file identity** — path plus stable policy for case, Unicode, metadata, and rename behavior;
- **manifest** — a signed or authenticated description of file versions, hashes, tombstones, and lineage;
- **chunk** — a content-addressed transfer unit;
- **peer session** — an authenticated transport relationship with negotiated folder membership;
- **transfer** — resumable movement of verified chunks;
- **commit** — crash-safe materialization of a file version or tombstone;
- **conflict** — preserved divergence, not silent overwrite.

Without these nouns, the cube can be secure-looking while still not being a sync system.

## What should change next

The next code-bearing revision should add a small C++ sync-domain slice:

1. Add typed structs and serialization tests for `DeviceId`, `FolderId`, `FileId`, `ChunkId`, `ManifestEntry`, `Tombstone`, `VersionLineage`, `ConflictRecord`, and `TransferReservation`.
2. Add a deterministic fixture-directory scanner that rejects unsafe paths and emits a local manifest with chunk hashes.
3. Add manifest diff planning from local/remote manifest fixtures into explicit sync actions.
4. Add a fake authenticated peer session harness around manifest exchange.
5. Bind exactly one planned sync action to the existing reservation/ledger path.

The first slice should avoid real OS watchers and real networking. A fake peer harness is enough to force the product model into C++ while keeping tests deterministic.

## What should stop

Until at least one concrete sync operation exists, stop adding generic features whose only subject is authorization, proof material, relay authority, or evidence reporting. Those are support systems. They become product work only when they protect a file-sync path.

## Corrected active invariants

1. **Path and content identity:** the same file/version/chunk has one unambiguous identity across peers and platforms.
2. **Peer and folder authority:** only authorized devices can publish or request state for a share.
3. **Idempotent sync mutations:** retries and duplicate peer messages do not create duplicate file versions, tombstones, transfers, or conflicts.
4. **Crash-safe application:** partial chunks and temp files never masquerade as committed versions.
5. **Honest conflicts:** divergent edits are preserved and surfaced; AnonSync must not silently pick a winner without policy.
6. **Recoverable local truth:** restart and restore preserve enough state to resume or reconcile without inventing success.
7. **Privacy-aware metadata:** sync evidence should be minimized and scoped to the share; future peer protocol work must be explicit about what metadata each peer learns.

## Honest ceiling after rev0650

The current C++ package is still not a complete peer-to-peer sync implementation. It has no production peer discovery, no real network protocol, no encrypted session layer, no file watcher, no content chunker in product code, no manifest diff engine, no transfer scheduler, no conflict resolver, no invite/share UX, and no NAT traversal or relay service. Rev0650 fixes the direction so those are now the work.
