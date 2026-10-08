# Authoritative sources and citations

This cube is informed by these sources. The final answer that delivered the cube
contains live citations; this file stores the durable URL trail.

## DHT foundations

- Kademlia, Maymounkov and Mazières: XOR metric, k-buckets, parallel asynchronous lookups.
  URL: https://pdos.csail.mit.edu/~petar/papers/maymounkov-kademlia-lncs.pdf
- S/Kademlia: disjoint paths, crypto puzzles, sibling broadcast.
  URL: https://telematics.tm.kit.edu/publications/Files/267/SKademlia_2007.pdf
- Coral DSHT: sloppy hashing, locality/capacity awareness, cache-along-path ideas.
  URL: https://www.cs.princeton.edu/~mfreed/docs/coral-iptps03.pdf

## BitTorrent DHT and mutable records

- BEP5: Mainline DHT over Kademlia.
  URL: https://www.bittorrent.org/beps/bep_0005.html
- BEP42: node-id constraint to reduce some DHT attacks.
  URL: https://www.bittorrent.org/beps/bep_0042.html
- BEP44: immutable and mutable DHT items, Ed25519 signatures, salt, seq, CAS, expiry.
  URL: https://www.bittorrent.org/beps/bep_0044.html
- BEP46: mutable torrents via DHT mutable items.
  URL: https://www.bittorrent.org/beps/bep_0046.html
- BEP51: key sampling/indexing cautionary material.
  URL: https://www.bittorrent.org/beps/bep_0051.html

## libp2p/IPFS DHT

- libp2p Kad-DHT spec: Kademlia plus S/Kademlia, Coral, and BitTorrent influences; validators.
  URL: https://github.com/libp2p/specs/blob/master/kad-dht/README.md
- libp2p DHT docs: client/server mode and provider-record behavior.
  URL: https://libp2p.io/docs/dht/
- IPFS Kad-DHT spec and IPNS mutable records.
  URL: https://specs.ipfs.tech/routing/kad-dht/

## I2P substrate

- I2P SAMv3 docs: stable API, STREAM/DATAGRAM/RAW sessions, SAM 3.3 feature notes.
  URL: https://i2p.net/en/docs/api/samv3/
- I2P datagram docs: authenticated and repliable datagram message framing.
  URL: https://github.com/i2p/i2p.website/blob/main/content/en/docs/api/datagrams.md
- I2P streaming docs: reliable in-order authenticated streams over I2P messages.
  URL: https://i2p.net/en/docs/api/streaming/

## Python code to crib from

- bmuller/kademlia: small asyncio Kademlia reference-ish implementation.
  URL: https://github.com/bmuller/kademlia
- aiobtdht: asyncio BitTorrent DHT/KRPC layering.
  URL: https://github.com/bashkirtsevich-llc/aiobtdht
- btdht: Python BitTorrent DHT crawler/extension base.
  URL: https://github.com/nitmir/btdht
- py-libp2p issues/specs: useful warning that Python DHT APIs are not a finished answer.
  URL: https://github.com/libp2p/py-libp2p/issues/540
