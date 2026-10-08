# rev0649 mission-kernel boundary compass — superseded by rev0650

Rev0649 incorrectly reframed AnonSync away from synchronization. That was wrong for this project.

The active mission is now restored in `docs/0040-rev0650-anonsync-p2p-sync-mission-correction.md`: **AnonSync is a C++ peer-to-peer file synchronization system**, aiming at Resilio Sync-style folder replication across authorized devices.

The rev0649 analysis is retained only as evidence of the misalignment that rev0650 corrected. Its useful content is narrow: the existing C++ code has valuable admission, replay, idempotency, SQLite/WAL recovery, outbox, relay, and signed-transition machinery. Its incorrect conclusion was treating that machinery as the product. In rev0650 and later, those pieces are subordinate to sync operations such as manifest publication, chunk transfer reservation, file-version commit, tombstone application, and conflict recording.

## Corrected mission statement

Given a shared folder and a set of authorized devices, AnonSync should discover or address peers, authenticate device/folder membership, compare content manifests, transfer missing chunks, apply file mutations idempotently, preserve conflicts honestly, and resume after interruption.

## Corrected next change direction

The next code-bearing work should be C++ sync substrate, not another generic authorization boundary:

1. Define sync-domain types and wire/storage schemas.
2. Build a deterministic local folder/index/chunk manifest harness.
3. Add a fake authenticated peer session that exchanges manifest deltas and chunk requests.
4. Map one existing ledger/outbox reservation path to one concrete sync mutation.
5. Keep Python limited to validators, audit, and packaging.

## Ceiling retained

The package still does not implement peer discovery, real networking, chunk transfer, conflict resolution, file watching, NAT traversal, or an encrypted sync protocol. Rev0650 corrects direction; it does not claim those product features exist yet.
