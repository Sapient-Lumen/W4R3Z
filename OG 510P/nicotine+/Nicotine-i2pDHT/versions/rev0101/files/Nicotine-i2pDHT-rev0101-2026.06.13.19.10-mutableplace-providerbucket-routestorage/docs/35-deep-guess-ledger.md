# Deep guess ledger

This file is deliberately speculative.  It is for remembering bold design intuitions, not for pretending they are proven.

## Guess A — path isolation beats global candidate soup

Classic iterative Kademlia wants the closest candidates as fast as possible.  In hostile settings, merging every returned node into one global queue may let one adversarial path contaminate the whole lookup.  S/Kademlia's disjoint-path idea should be promoted from “security add-on” to default DHT posture.

Implementation guess: maintain per-path queues, per-path observations, and per-path termination.  A result can be accepted only after enough independent paths produced compatible evidence.

## Guess B — semantic poisoning is worse than silence

An empty response is suspicious but obvious.  A response containing plausible false providers or stale mutable heads is more dangerous because it can trigger early termination.  A power-user DHT should treat “enough provider-looking answers” as insufficient evidence unless they arrive across multiple paths and pass local validation.

Implementation guess: separate `GET_PROVIDERS` termination from `GET_MUTABLE` termination.  Provider lookups should generally finish all paths; mutable lookups need quorum plus newest valid sequence selection.

## Guess C — power users need sweep work, not heroic bursts

Large inventories cannot be reprovided one key at a time with full lookup cost per key.  The DHT should group advertisements by keyspace region and sweep regions over the full interval.  Discover a region's closest nodes once, then batch multiple provider/mutable/contact announcements.

Implementation guess: `SweepPolicy(interval=22h, expiration=48h, region_prefix_bits=N)` as a starting posture, then tune from actual I2P churn.

## Guess D — sloppy records are necessary, but must be visibly second-class

Canonical k-closest placement is how correctness is reasoned about.  Sloppy storage is how hot keys survive churn, tunnel wobble, and popularity.  Sloppy records should be tagged as sloppy, expire sooner, and never override canonical mutable sequence/validator rules.

Implementation guess: lookup-path breadcrumbs and power-user mirrors get extra copies.  Readers prefer canonical quorum but can use sloppy records as hints to continue search.

## Guess E — mutable slots should be a family, not one record type

BEP44-style single-writer mutable items are the minimum.  Future power users will want update feeds, delegated keys, signed directories, and multiwriter registries.  The storage-node rule should remain simple: validate family, target, signature, sequence/root, size, expiry.

Implementation guess families:

- `single_writer`: BEP44/IPNS-like monotonic head.
- `delegated`: long-term identity signs a delegation to a writer key.
- `merkle_feed`: head points to a signed Merkle/log tip.
- `crdt_registry`: head points to a canonicalized multiwriter state root.

## Guess F — bootstrap should be plural and local-first

A good DHT should have many entrances: cached peers, invite files, signed seed lists, friend introducers, room-like groups, and power-user gate nodes.  The system should treat all entrances as hints.  No entrance should be a root of truth.

## Guess G — low-hanging Sybil friction should be layered, not worshiped

Proof of work, destination-bound IDs, signed records, old-contact preference, challenge-response, and local reputation each remove cheap failure modes.  None solves Sybil.  The DHT should assume Sybils exist and use disjoint paths, redundant storage, and anomaly readouts to degrade gracefully.

## Guess H — metadata modes should be explicit budgets

Connectivity-first users may knowingly publish more provider/index metadata.  Quiet users should not.  The DHT should expose posture as a local budget:

- quiet: route, read, maybe watch a few mutable slots;
- connective: carry contacts and bootstrap hints;
- index contributor: carry provider records and sweep queues;
- lab maximal: high-leakage, high-utility experimental mode.

## Guess I — records should be small but composable

The DHT should not become a content store.  It should hold small routing data, small provider announcements, small mutable heads, and pointers to content elsewhere.  Larger data should be content-addressed and provided by peers, not stored in DHT value slots.

## Guess J — the simulator is a product feature

The future implementation should ship with a chaos laboratory: churn, slow paths, false providers, stale mutable heads, bucket poisoning, seed-list capture, and hot-key overload.  Power users and maintainers should be able to reproduce weird network failures locally.


## rev0006 additions — mutable sync

- The DHT should be a mutable control plane, not a file store.
- Mutable heads should point to content-addressed larger things: torrent infohashes, feed entries, roster digests, snapshot roots, and garden service catalogs.
- Multiwriter sync should use per-writer append-only feeds plus owner-signed rosters, not a single shared write slot.
- Garden nodes should watch heads, mirror manifests, cache encrypted blocks, relay feeds, hold tombstones, and report rollback evidence without authoring changes.
- Conflicts should be preserved by default; the DHT should not silently resolve application conflicts.
