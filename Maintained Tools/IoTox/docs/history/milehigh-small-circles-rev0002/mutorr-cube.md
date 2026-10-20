# Mutorr Cube algorithm

## Purpose

A Cube is one mutable namespace's deterministic replication overlay. Examples include `family/chat`, `garage/sensors`, or a shared directory root. Devices that are not authorized or subscribed to a namespace are not members of that Cube.

The Cube does not replace Tox. Tox supplies encrypted peer connections and later file transfer. The Cube answers three application questions:

1. Which few peers should this device maintain as replication neighbors?
2. Which peers should retain durable copies of this namespace?
3. Is a newly announced mutable head an advance, duplicate, stale record, conflict, or missing-history branch?

## Membership input

A Cube is built from an already-authorized set of 256-bit member IDs. Production member IDs are expected to be uniformly distributed cryptographic identities, such as values derived from stable application identities. rev0002 does not define membership consensus or authorization distribution.

All peers sort the same unique IDs lexicographically. Input discovery order therefore has no effect on the result. Duplicate IDs and invalid configurations fail closed.

## Circle neighbors

The default neighbor count is four. For each sorted member at ring index `i`, the neighbors are:

```text
i - 2, i - 1, i + 1, i + 2      modulo member count
```

This graph is symmetric, connected, and bounded. A joining member perturbs only the adjacent ring neighborhood. When the Cube is smaller than the configured degree plus one, it becomes a complete local graph without self-links or duplicates.

For 30 members:

```text
edges = 30 * 4 / 2 = 60
diameter = ceil(floor(30 / 2) / 2) = 8 hops
```

A head announcement is intended to be flooded once across this graph with message-ID deduplication. The announcement is small. Object bytes are requested only by peers that need them, and a peer that receives an immutable object can immediately seed it onward.

## Custodians

For each namespace, every member receives a stable 64-bit placement score from the namespace ID and member ID. The highest `R` scores are custodians, with the member ID as a deterministic collision tie-breaker. The default replication factor is three.

This is highest-random-weight, or rendezvous, placement. It has the useful join property that adding a member either changes nothing or inserts that new member into the winning set. Existing winners are not replaced by unrelated existing members.

The rev0002 placement mixer is fast and deterministic, but it is not a cryptographic hash and should not be treated as protection against an attacker choosing identities to bias placement. Before hostile open membership, replace or key the scoring primitive behind the same API.

## Allocation behavior and complexity

Cube construction:

```text
sort members:             O(N log N)
construct adjacency:      O(N * degree)
storage:                  O(N * degree)
```

Runtime queries:

```text
member lookup:            O(log N)
neighbor span:            O(1), no allocation
R custodians:             O(N * R), no full sort
mutable-head evaluation:  O(1)
```

`custodian_indices_into` fills a caller-provided span and uses a fixed stack array of at most 32 candidates. This is the intended high-frequency path. The vector-returning functions are convenience wrappers.

## Mutable heads

A head identifies one writer's current immutable root within a namespace:

```text
wire version
namespace ID
writer signing key
monotonic generation
root digest
previous root digest
creation time
content byte count
object count
64-byte signature
```

Generation one requires a zero previous root. Later generations require a non-zero previous root. The comparison function assumes signature verification already succeeded and classifies the candidate without mutating state.

Multiple writers should normally have separate append-only streams whose application view is merged. A true shared multi-writer directory will need explicit conflict semantics or a CRDT layer; silently selecting the numerically largest generation from different writers would be incorrect.

## Not implemented in rev0002

- distribution and consensus for authorized membership;
- liveness/failure detectors and connection scheduling;
- gossip message-ID cache and retry timing;
- signature algorithm, key storage, and verification;
- cryptographic object hashing and immutable object store;
- Merkle directory traversal and anti-entropy inventory;
- Tox file-transfer object exchange;
- durable head/object persistence;
- malicious-identity resistance for placement.
