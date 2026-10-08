# Research notes — mutable sync systems

These notes preserve the sources and design influences behind rev0006.

## BEP44 / BEP46

BEP44 defines mutable DHT items with Ed25519 public keys, optional salt, sequence numbers, signatures, and small bencoded values.  BEP46 uses that machinery to make torrents updateable by publishing the latest infohash under a mutable key.  The cube keeps this as the minimum viable mutable-head pattern.

Design steal:

```text
small signed mutable head -> content-addressed larger thing
```

## Syncthing

Syncthing's Block Exchange Protocol describes devices with folders, local models, metadata, block hashes, and a global model formed from the union of device models.  Peers request missing or outdated blocks.  That says our DHT should not be a block-transfer engine; it should make model/head/provider discovery robust.

Design steal:

```text
files as metadata + block hashes; transfer missing blocks outside the DHT
```

## Hypercore

Hypercore is a secure distributed append-only log with sparse replication and signed Merkle trees.  The DHT does not need to implement Hypercore, but the per-writer-feed idea is very strong for multiwriter sync.

Design steal:

```text
append-only feed body elsewhere; mutable DHT head stores only the latest tip
```

## Secure Scuttlebutt

SSB's feed model shows the value of unforgeable append-only logs and offline-friendly replication.  Its subjective/social replication choices are not copied here, but the feed-per-writer model remains attractive.

Design steal:

```text
writer identity owns an append-only sequence; peers replicate what they care about
```

## Willow

Willow's data model emphasizes namespaces, subspaces, paths, timestamps, and policy choices.  Its Confidential Sync proposal emphasizes incremental sync, partial sync, access control, and private interest overlap.

Design steal:

```text
make the DHT generic enough for many namespace/path/policy instantiations
```

## Tahoe-LAFS

Tahoe-LAFS is a strong teacher for capabilities, encrypted storage, erasure coding, and untrusted storage servers.  Its mutable file docs describe encrypted and signed mutable slots where read-write caps can set contents, read-only caps can read/validate, and storage servers need not be trusted.

Design steal:

```text
garden storage can be useful without being trusted or able to read content
```

## Resilio / BitTorrent Sync

Resilio's public docs are not a full open protocol spec, but the visible product lesson is powerful: peer-to-peer, cloud-free, direct transfer when possible, no mandatory central cloud copy, and sticky continuous sync.  A FLOSS version should expose its control plane as signed, inspectable records.

Design steal:

```text
sticky continuous peer sync, but open and auditable
```

## IPNS

IPNS records are cryptographically verifiable mutable pointers to immutable/content-addressed objects.  That is almost the exact abstraction a DHT sync head needs.

Design steal:

```text
mutable names point to immutable/content-addressed state
```

## Strongest current guess

Build the DHT so that it can natively validate:

```text
BEP44-like mutable slots
BEP46-like torrent heads
IPNS-like signed pointers
Hypercore/SSB-like feed tips
Syncthing-like snapshot/provider records
Tahoe-like capability-separated storage offers
Willow-like namespace/subspace-aware records
```

Do **not** build one giant sync protocol into the DHT.  Build the validator and garden service substrate that lets respectful sync protocols grow.
