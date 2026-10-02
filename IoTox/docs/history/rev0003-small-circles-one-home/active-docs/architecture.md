# IoTox architecture

## Design center

IoTox is a headless, self-owned device agent built around Tox. It aims to preserve
ratox's small, local, scriptable “just werx” experience while giving physical actions,
recovery, authorization, persistence, routing, and replication explicit semantics.

rev0003 adds an optional namespace replication subsystem, `iotox::mutorr`, from the
Milehigh Small Circles branch. Mutorr does not replace Tox and does not become a
requirement for ordinary IoT commands.

```text
human owner
    |
permanent generated phrase / printed card
    |
RecallRoot-v1                                         [implemented contract]
    |
domain-separated owner/re-entry keys                 [planned]
    |
independent authorization ledger                     [planned]
    |             roles / capabilities / epochs / revocation
    |
    +-------------------------+------------------------------+
    |                                                        |
base device plane                                   optional namespace plane
commands / state / results                          Mutorr small circles
pairing / files / OTA                               heads / inventories / wants
    |                                               immutable objects
    +-------------------------+------------------------------+
                              |
                       IoTox protocol frame                    [implemented seed]
                              |
                    bounded durable message layer              [planned]
                              |
                         peer transport API
                              |
                      one Tox owner thread                     [implemented]
                              |
                    c-toxcore runtime adapter                  [implemented]
                              |
           native route / future Tor route / future I2P route
                              |
                            Tox
```

## Architectural invariants

1. No module outside the toxcore adapter calls a toxcore API.
2. One owner thread exclusively controls each `Tox*` instance.
3. Tox friendship is connectivity, not IoTox authorization.
4. RecallRoot-v1 is never used directly across unrelated cryptographic domains.
5. IoTox operates no key that can reassign customer devices.
6. Reserved network routes fail closed and never silently become native.
7. Basic device operation does not depend on Mutorr.
8. A Mutorr Cube is built only from an authorized namespace membership snapshot.
9. Custody, readability, writing, actuation, and administration are separate powers.
10. Transport success is not business-operation completion.
11. Externally supplied sizes, counts, queues, and work are bounded.
12. Claims in documentation track what has actually been compiled or tested.

## Base device plane

The base device plane is the heart of IoTox. It should remain useful for one owner and
one device without any distributed object store.

Planned responsibilities include:

```text
HELLO and capabilities
pairing and physical claim
controller delegation
command and command result
state snapshot and state event
application acknowledgement
revocation
firmware manifest and bulk transfer
structured local IPC
ratox-style filesystem/FIFO facade
```

Hardware-affecting commands need message IDs, deadlines, idempotency policy, durable
acceptance state, authorization decisions, and explicit results. A successful Tox send
means only that the transport accepted a packet; it does not mean an actuator completed
an operation.

## RecallRoot-v1 and re-entry

RecallRoot-v1 is a fixed Argon2id derivation contract for eight uniformly generated
words from the pinned 7,776-entry EFF long word list.

It permits the same owner-side root to be reproduced from memory or paper without an
IoTox account, server record, old phone database, or surviving backup file. The public
fixed contract also permits offline guessing. Phrase strength is therefore a structural
product requirement.

The derivation contract is implemented and independently known-answer tested. Still
planned are:

- domain-separated owner application signing key;
- deterministic or otherwise reproducible controller Tox key material;
- no-spam and address re-entry behavior;
- device discovery after total controller-state loss;
- challenge-response proof that never sends the phrase or root;
- ownership-epoch binding;
- delegated daily-use controller keys;
- root-compromise transition and race policy.

## Authorization ledger

The authorization ledger is independent of toxcore savedata and friend state. It will
represent:

- owner roots and ownership epochs;
- delegated controller keys;
- roles and individual capabilities;
- expiry and temporary access;
- namespace read, write, store, and administer rights;
- revocations and root transitions;
- device-class-specific physical interlocks.

The device will authorize application messages against this ledger even when the Tox
session is authenticated.

A future namespace membership snapshot is an authorization-ledger product. Mutorr does
not discover or elect its own legitimate members.

## Optional Mutorr namespace plane

Mutorr addresses selected multi-peer shared state. Examples include:

```text
home/config
workshop/sensors
camera/archive
family/shared
controller/backups
```

Each namespace has its own authorized member snapshot. Every member given the same set
sorts the same 256-bit IDs, computes the same bounded circle, and selects the same
preferred custodians.

### Cube topology

The research default is four symmetric neighbors:

```text
i - 2, i - 1, i + 1, i + 2    modulo member count
```

For thirty members this produces sixty undirected application edges rather than 435
full-mesh edges, with a computed diameter of eight hops. Small Cubes become complete
local graphs.

The Cube code is deterministic, discovery-order independent, toxcore-independent, and
implemented in C++20. The default degree is provisional; simulations must evaluate
failure, sleep, churn, and correlated partitions.

### Rendezvous custodians

For each namespace, the current planner scores every member and selects the highest
few. The default replication factor is three. Selection has an allocation-free hot
path bounded at 32 results.

The current 64-bit mixer is a performance fixture, not adversarial cryptography. It
must be replaced or keyed before identities can be chosen by hostile participants.
Custodian selection expresses desired placement, not proof of existing replicas.

### Mutable heads and immutable objects

Mutorr intends for the mutable item to remain small:

```text
namespace
writer
monotonic generation
current immutable root
previous link
creation metadata
size and object count
signature
```

The current head wire record is fixed at 221 bytes and has a canonical 157-byte signing
body. Encoding, decoding, validation, progression classification, tests, and fuzzing are
implemented. Signature verification and cryptographic digests are not.

The `previous` field currently links the previous root. Before protocol freeze, IoTox
must decide whether stronger history binding requires the digest of the complete prior
head instead.

Single-writer streams can form linked chains. Multiple writers need per-writer streams
plus an explicit merged view, application conflict rules, or a CRDT. Generation numbers
from different writers are not globally comparable.

### Announcement and bulk lanes

```text
small control lane:
  MUTORR_HEAD
  MUTORR_INVENTORY
  MUTORR_WANT
  MUTORR_OBJECT_OFFER
  -> IoTox lossless custom packets

bulk lane:
  immutable object and chunk bytes
  -> planned Tox file-transfer manager
```

The custom message numbers are provisional. Large objects should not be fragmented
through an unnecessary second transport protocol.

### Connection reuse

Cubes describe application-neighbor requirements. A future scheduler should take the
union of required peers across namespaces, reuse existing Tox relationships, apply
bounded reconnect/backoff policy, and never infer namespace membership from friendship.

## Confidential object replication

Transport encryption protects a Tox connection, but a custodian may not be authorized
to read stored content. The object layer likely needs:

- namespace content keys;
- authenticated encryption;
- cryptographic content identities over a carefully chosen plaintext or ciphertext
  representation;
- key envelopes for readers;
- rotation when membership changes;
- metadata-minimizing manifests;
- quota, retention, tombstone, and cryptographic-erasure policy.

These choices are intentionally not frozen in rev0003.

## Tox owner-thread boundary

`ToxTransport` owns:

- the dynamically loaded toxcore table;
- Tox options and the `Tox*` instance;
- the worker thread and `tox_iterate` loop;
- toxcore callbacks;
- savedata snapshots;
- public command and event queues.

Callbacks copy data into typed C++ events before consumers see it. Other modules use
stable application identities rather than toxcore friend numbers.

The current public command queue remains a research implementation. Before commands can
control hardware, it needs bounded capacity, cancellation, deadlines carried into the
worker, precise timeout semantics, and shutdown rules that prevent a caller-visible
timeout from becoming a later surprise actuation.

## Runtime dependency adapters

IoTox-owned source and tests are C++20. c-toxcore and Argon2 are external C
implementations behind narrow runtime adapters.

The adapters provide:

- buildability when development headers are absent;
- exact ABI test doubles written in C++;
- explicit missing-symbol and version failure;
- a single upgrade boundary;
- business logic that does not include dependency headers.

Runtime loading is a research and modularity boundary, not a production packaging or
licensing conclusion. A “just werx” distribution should pin, build, review, and ship
compatible dependency versions deliberately.

## Transport versus route

IoTox models two axes:

```text
peer transport: Tox | future I2P-direct | future Tor-direct
route:          native | future I2P | future Tor
```

Current combinations:

| Stack | rev0003 status | Meaning |
|---|---|---|
| Tox/native | adapter-verified | Lifecycle and packet boundary tested against the exact C ABI mock; no real network proof yet |
| Tox/Tor | reserved | Future TCP-only Tox route through explicit Tor plumbing and leak tests |
| Tox/I2P | reserved | Future Tox relay/bootstrap route through explicit I2P plumbing and leak tests |
| Tor-direct | out of scope | Separate future application transport without Tox semantics |
| I2P-direct | out of scope | Separate future application transport without Tox semantics |

Tox/Tor and Tox/I2P must never silently enable native UDP, local discovery, DNS, or
fallback outside requested policy.

## Tox infrastructure stewardship

IoTox intends to support owner-operated and responsibly contributed Tox bootstrap and
TCP-relay infrastructure. Useful work may include reproducible server deployment,
monitoring, capacity, test reports, and upstream fixes.

Operating a server grants no device ownership, recovery, authorization, namespace
membership, or content-decryption authority.

## Persistence

Implemented Tox savedata replacement uses:

1. a randomized private temporary file;
2. complete writes;
3. file `fsync`;
4. atomic rename;
5. parent-directory `fsync`;
6. mode `0600` for newly created state.

Still required:

- encrypted key storage appropriate to target platforms;
- atomic authorization-ledger storage;
- rollback-resistant ownership epochs;
- durable inbox and outbox;
- durable head and immutable-object store;
- known-good recovery slots;
- full-disk and power-loss behavior;
- storage quotas and garbage collection.

## Local interface

The primary local API should be structured, likely a Unix `SOCK_SEQPACKET` endpoint or
length-framed stream. It needs request IDs, responses, errors, deadlines, credentials,
and subscriptions.

A ratox-style façade can expose files and FIFOs over the same internal operations. It
is a compatibility and operator surface, not the database or source of authorization.

## Dependency direction

```text
CLI / Unix socket / ratox-style facade
                  |
       device services and applications
                  |
 authorization ledger + namespace membership
                  |
 base command plane + optional Mutorr plane
                  |
 protocol codecs + durable stores + queues
                  |
             peer transport API
                  |
          c-toxcore runtime adapter
```

Dependency arrows do not point upward. Mutorr has no toxcore dependency. Toxcore has no
knowledge of ownership. The local façade has no authority of its own.

## Current implementation status

Implemented or adapter-verified in rev0003:

- C++20 build, tests, benchmark, and fuzz targets;
- strict GCC and Clang warning lanes;
- ASan/UBSan and TSan presets;
- Tox runtime ABI loader and exact C++ mock;
- one-owner-thread Tox lifecycle and packet loop;
- private atomic Tox savedata persistence;
- transport/route model with fail-closed reserved routes;
- versioned fixed IoTox packet frame;
- RecallRoot-v1 phrase parser, word list, Argon2 adapter, and known-answer test;
- Mutorr fixed identifiers, Cube topology, rendezvous planner, linked head format,
  benchmark, tests, and fuzz target.

Planned or unverified:

- pinned real c-toxcore build and two-peer network fixture;
- public bootstrap and relay configuration;
- RecallRoot subkey hierarchy and live re-entry;
- device identity and physical claim;
- authorization ledger;
- durable application queues;
- cryptographic application signatures and object encryption;
- namespace membership epochs and gossip simulator;
- Tox file transfers;
- Unix socket and ratox façade;
- Tor/I2P Tox routes;
- target-hardware power and reliability testing.
