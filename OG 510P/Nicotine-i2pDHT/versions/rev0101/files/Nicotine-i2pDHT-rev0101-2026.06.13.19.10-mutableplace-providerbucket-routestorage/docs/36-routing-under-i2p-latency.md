# Routing under I2P latency and anonymity

## Design pressure

I2P is not UDP on the public internet.  It is a tunnelled anonymous substrate with variable latency, separate router behavior, and multiple application APIs.  A DHT on top of it should assume that every extra round trip matters.

## Guesses

### 1. Use 256-bit XOR as the native routing keyspace

A 256-bit SHA-256-based keyspace matches the existing rev0003 direction and the broad libp2p/IPFS Kad-DHT style.  BEP44/BEP46 compatibility can remain as a 160-bit facet for mutable-torrent interop reasoning, but the native I2P DHT should not be trapped in the BitTorrent Mainline keyspace.

### 2. Default to disjoint iterative lookup

Each lookup starts from a seed set and splits candidates into path queues.  Each path has its own visited set and observation trail.  Returned contacts should not immediately dissolve path boundaries.

Pseudo-shape:

```text
seed contacts -> distance sort -> diversity split -> path queues
for round in max_rounds:
    ask alpha_per_path from each path
    validate responses
    append closer nodes only to that path, unless cross-path promotion is deliberate
accept only when quorum + path diversity + validator selection agree
```

### 3. Diversity is hard without IP addresses

IPFS/Bitcoin-style network-group diversity does not directly map to I2P.  We can diversify by Destination hash, node public key, observed behavior, age, and invitation source, but those are weaker than network-prefix diversity.

### 4. Prefer old-good contacts but sample new edges

Kademlia's old-contact preference remains useful.  A DHT that only trusts old contacts can ossify or be captured; a DHT that eagerly accepts every new contact can be flooded.  The guess is to keep old contacts in primary buckets and put new contacts into replacement/sampling lanes until they survive challenges and useful responses.

### 5. Avoid global early termination

Provider and mutable lookups should avoid early termination based solely on count.  A false provider attack can return plausible-looking providers early.  Mutable slots should select the newest valid signed record after quorum, then repair stale storage nodes by writing back the winning record.

## Python surface

`lookup.py` encodes these guesses as `LookupPolicy`, `LookupPath`, `LookupTrace`, and `decide_lookup_acceptance()`.
