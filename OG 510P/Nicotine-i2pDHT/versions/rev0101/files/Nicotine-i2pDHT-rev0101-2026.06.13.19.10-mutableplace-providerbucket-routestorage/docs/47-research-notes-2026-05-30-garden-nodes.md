# Research notes — garden nodes, 2026-05-30

These notes are not a literature review.  They are the source-shaped constraints that influenced rev0005.

## I2P floodfill routers

I2P's network database has floodfill routers that accept stores and respond to queries.  The docs describe floodfills as a simple distributed storage mechanism with no central authority or consensus.  Floodfill participation is tied to capacity/health, and the current automatic rules target only a minority of routers.  I2P also records peer-profile metrics such as response time, successful lookups, successful stores, and last response.  This is a strong teacher for garden nodes: use contribution roles and local profiling, but keep them untrusted.

## I2P threat notes

The same I2P docs warn about malicious floodfills, partial keyspace attacks, bootstrap attacks, and query capture.  That pushes garden-node design away from single-garden trust and toward disjoint paths, local autocuration, and cross-checking.

## libp2p/IPFS DHT client/server mode

IPFS/libp2p distinguishes DHT servers from DHT clients: servers respond to queries and store records, while clients query but do not serve/store.  The spec says a large number of reliable DHT servers distributes load, while under-resourced nodes should remain clients.  This supports a garden/leaf split, with the important addition that our garden nodes are explicitly voluntary and locally selected.

## Provider sweep

The go-libp2p-kad-dht reprovide-sweep issue argues that one lookup per provider record is terrible for large providers, and proposes grouping provider records by XOR keyspace region so records allocated to the same DHT servers are reprovided together.  This exactly matches garden-node `region_gardener` and `bulk_reprovider` services.

## Coral DSHT

Coral's DSHT lesson is that replicated resources should be located, not blindly stored as content in the DHT.  Sloppy hashing allows a node to find a nearby valid copy without hot-spotting the index.  Garden nodes should therefore store short-lived breadcrumbs and provider hints before they store content.

## S/Kademlia

S/Kademlia proposes disjoint lookup paths, crypto-puzzle friction, and reliable sibling broadcast.  Garden nodes should not replace this.  They should amplify it: more path diversity, sentinel checking, and safer sibling/replica repair.

## BEP44 mutable records

BEP44's mutable item model uses a public key, salt, sequence number, signature, and token-based write semantics.  Garden mutable stewardship should respect this shape: gardens can watch and reannounce signed heads, but cannot forge them.

## Whānau / social trust caution

Whānau uses social links to resist Sybil attacks, but it depends on assumptions about attack edges and honest-region connectivity.  Garden autocuration borrows only the local-memory spirit.  It does not claim Sybil-proof routing and does not publish a global social trust graph.
