# Research notes refreshed for rev0004

The cube continues to crib concepts but not code.

## I2P/SAM

I2P SAM remains the likely first live transport API for Python/non-Java prototypes.  The official SAM v3 docs describe it as the recommended protocol for non-Java applications and note implementation differences: i2pd does not currently support most SAM 3.2/3.3 features.  That reinforces the need for a transport-neutral DHT core.

## I2P BitTorrent DHT

I2P's BitTorrent-over-I2P notes replace compact IP:port peer info with Destination hashes and define a secure node ID requirement tying node ID prefix bytes to the Destination hash.  The rev0004 guess keeps the stronger variant from rev0003: bind the full node ID derivation to Destination hash, DHT public key, and work nonce.

## BEP44/BEP46

BEP44's mutable items use Ed25519 signatures, optional salt, monotonic sequence numbers, CAS, size limits, and validation before storage.  BEP46 builds mutable torrents on top of those mutable DHT items.  rev0004 keeps this but broadens mutable slots into a family.

## S/Kademlia

S/Kademlia emphasizes disjoint lookup paths, crypto puzzles limiting free node ID generation, and reliable sibling broadcast.  rev0004 promotes disjoint paths and sibling/replication thinking into default design posture.

## Whānau and social trust

Whānau shows that social links can make Sybil attacks harder under the right graph assumptions.  rev0004 does not import Whānau, but it remembers the lesson: invite/friend introducers may become useful bootstrap hints if kept as optional local trust edges rather than global identity truth.

## Coral DSHT

Coral's sloppy hash table focuses on locating nearby copies and avoiding hot spots rather than storing the content itself.  rev0004 adapts this as canonical-plus-sloppy placement: canonical closest nodes for correctness, sloppy breadcrumbs/hot mirrors for liveness.

## libp2p/IPFS Kad-DHT

libp2p/IPFS distinguishes provider records from value records, validates records before storage, uses republish/expiration intervals, and discusses quorum/entry correction for mutable IPNS-style records.  rev0004 borrows the design vocabulary and especially the region-sweep idea for high-volume providers, while rejecting direct dependency in the Python prototype.

## Recent IPFS DHT attack literature

Recent work on active Sybil attacks against IPFS DHT provider records reinforces the danger of early termination and semantically false provider data.  The rev0004 lookup decision helper models this by refusing provider early stop by default.
