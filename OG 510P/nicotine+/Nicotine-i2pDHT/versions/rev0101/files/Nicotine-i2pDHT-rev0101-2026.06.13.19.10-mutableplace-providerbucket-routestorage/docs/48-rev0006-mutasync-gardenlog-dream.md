# rev0006 — mutasync gardenlog dream

This revision accepts the user's nudge: mutable records should stay at the center because they are the doorway to technologies we can respect — mutable torrents, FLOSS sync, signed feeds, encrypted block stores, garden-backed availability, and eventually tools that feel as sticky as proprietary peer sync without surrendering protocol freedom.

The cube remains a DHT design cube.  It does **not** become a file-sync project.  The design move is subtler:

> The DHT should be a mutable control plane for sync systems, not the sync system itself.

A Resilio-like system wants several things at once:

1. A stable share identity.
2. A way to find peers that care about that share.
3. A way to announce that the share changed.
4. A way to verify that the announcement is authorized.
5. A way to find encrypted blocks, manifests, and witnesses.
6. A way for high-resource nodes to help without becoming owners.

Mutable DHT records can do 2-5 cleanly if we keep the payloads small and signed.  The DHT should carry heads, rosters, provider claims, and cache hints.  File contents, large manifests, block exchange, reconciliation, and conflict UX live above or beside the DHT.

## Deep guess

A future FLOSS sync family over this substrate should use **per-writer append-only feeds plus mutable heads**.

The tempting shortcut is a single mutable slot per folder.  That is too brittle for multiwriter sync.  A single shared writer key turns every device into an authority-equivalent device; a single slot also makes concurrent updates painful.  Better:

```text
collection root key
  -> mutable roster head
      -> authorized writer keys
          -> per-writer append-only feed head
              -> content-addressed encrypted blocks / manifests
```

The DHT stores the live head pointers.  The feeds and blocks are content-addressed.  Garden nodes can watch and reannounce the heads, cache encrypted blocks, mirror compact manifests, witness rosters, and help sleeping devices reconnect.

## Why this belongs in the DHT foundation

Mutable torrents are the smallest proof: public key + optional salt resolve to the latest infohash.  But the same primitive generalizes:

- mutable torrent head: `pubkey + salt -> infohash`
- mutable feed head: `writer pubkey + collection salt -> latest signed feed entry`
- mutable roster head: `owner pubkey + collection salt -> authorized writers digest`
- mutable snapshot head: `owner pubkey + collection salt -> latest manifest root`
- garden catalog head: `garden pubkey + service salt -> current service offer digest`

The DHT needs to know how to validate these things before any application asks for them.

## The Resilio lesson, without cloning Resilio

Resilio/BitTorrent Sync's user-facing magic is not just P2P transfer.  It is sticky continuous sync, direct peer transfer where possible, no mandatory cloud copy, and fast catch-up.  Our version should be FLOSS and built around verifiable open records.  That means we need the DHT to be good at:

- finding peers for a share;
- finding the newest authorized head;
- keeping records alive while publishers sleep;
- helping power users donate bandwidth/storage;
- never letting helpers author changes.

## The Syncthing lesson

Syncthing is a teacher for block sync and local/global model thinking.  Devices advertise folder models, files are represented by block hashes, and peers request missing/outdated blocks.  That suggests our DHT should not store file data; it should help peers discover models, heads, and providers.

## The Hypercore / SSB lesson

Append-only feeds make replication simpler because a peer can ask: "what entries do you have after index N?"  Signed feed entries create a stable audit trail.  The DHT only has to find the tip.

## The Willow lesson

Sync needs namespaces, subspaces/writers, paths, and policy.  A generic DHT should not pick one conflict policy forever; it should provide enough validated heads and records for applications to instantiate their own policy.

## What rev0006 adds

New code:

```text
src/i2p_dht_lab/mutasync.py
```

New tests:

```text
tests/test_mutasync.py
```

New record ideas:

```text
CollectionDescriptor
WriterGrant
FeedEntry
BlockRef
FileVersion
SnapshotManifest
SyncMutableHead
SyncGardenPlan
```

New guardrail:

> Multiwriter sync uses per-writer feeds, not a shared mutable write slot.

## Nonclaims

- No block exchange protocol.
- No encryption format.
- No live I2P transport.
- No production sync algorithm.
- No conflict UX.
- No guarantee that this is the final sync architecture.

The point is to put the right **mutable record algebra** into the DHT baby before downstream apps hard-code weaker assumptions.
