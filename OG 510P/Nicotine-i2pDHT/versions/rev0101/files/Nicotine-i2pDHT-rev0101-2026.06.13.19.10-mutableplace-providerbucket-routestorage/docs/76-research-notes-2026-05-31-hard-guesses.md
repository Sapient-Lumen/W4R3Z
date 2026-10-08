# Research notes — hard guesses first

This revision keeps using outside systems as teachers but not as templates to copy.

## BEP44 mutable items

BEP44 remains the cleanest compact mutability reference: Ed25519 public key, optional salt, sequence number, signature, bencoded value size budget, CAS, and mandatory rejection of older/equal conflicting sequences by storing nodes.

Relevant pressure for this cube: BEP44 validates a mutable record but does not by itself solve split views or stale replicas for an I2P-hosted app DHT. That is why rev0009 adds `MutableHeadMemory` and witness receipts above basic signature validation.

## libp2p/IPFS Kad DHT

The libp2p Kad-DHT spec emphasizes validators before storage/retrieval and stable record selection among competing values. It also documents quorum and correction behavior for IPNS records in the IPFS DHT.

Relevant pressure for this cube: validator/select hooks are mandatory, but rev0009 does not copy IPNS behavior as a finished answer. Instead it treats quorum, stale correction, and latest selection as things to stress in the chaos harness.

## S/Kademlia

S/Kademlia remains important for disjoint paths, signatures, and low-friction anti-Sybil puzzles. Its lesson for rev0009 is not “we are secure now.” The lesson is that lookup diversity and node-id admission should be designed early.

Relevant pressure for this cube: future fork receipts should include path-family evidence, not just source node ids.

## I2P netDb / floodfill

I2P's floodfill documentation is an unusually useful warning: giving some nodes more storage/query responsibility is normal, but malicious, slow, partial-keyspace, and bootstrap attacks remain live concerns.

Relevant pressure for this cube: garden nodes can be supernodes that give bandwidth and storage, but their receipts and catalogs must remain evidence, not truth.

## IPNS as a cautionary teacher

IPNS is valuable as a warning: mutable naming over a DHT is hard when records expire, replicas are stale, and clients need a latest-enough answer without global consensus. rev0009 therefore avoids naming polish and tests the ugly mechanics first.

## Research debt

- Quantify how many disjoint paths should be required for mutable heads versus provider records.
- Decide whether fork receipts should be stored near the mutable target, near a witness target, or only exchanged opportunistically.
- Model capture by seed channel, not only by node id.
- Test revocation-head rollback/fork behavior using the same forkwatch machinery.
- Decide if same-sequence fork evidence should permanently poison a writer key or only a salt-specific head.
