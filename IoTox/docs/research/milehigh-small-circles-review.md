# Milehigh Small Circles branch review

## Source reviewed

User-supplied archive:

`IoToxmutorr-rev0002-2026.08.13.11.41-cpp20-small-circles-rendezvous-mutorr-cube(1).zip`

SHA-256:

`3e0406bf91ca1afaf2437463a39e0eac3398e75191b6108d3c1df34a973b1d7d`

The archive was treated as a parallel branch descended from the IoTox rev0001
foundation. It was read as source, design record, build report, and test evidence.
The supplied prebuilt test runner reported 22 C++ tests with zero failures. The branch
also included GCC/Clang, sanitizer, benchmark, and fuzz reports.

## Main contribution

The branch introduces `iotox::mutorr`, a toxcore-independent planning layer for
namespace-scoped replication.

Its principal pieces are:

- `Id256`: fixed 256-bit identifiers with canonical lowercase hexadecimal encoding;
- `Cube`: a deterministic bounded-degree ring overlay computed from an authorized
  member snapshot;
- rendezvous custodian selection with a default replication factor of three;
- `HeadRecord`: a fixed 221-byte mutable-head record with a 157-byte canonical signing
  body and a 64-byte opaque signature field;
- head progression classification for initial, advance, duplicate, stale, conflict,
  missing-history, different-stream, and invalid records;
- provisional IoTox frame message types for head, inventory, want, and object offer;
- a native C++ topology demo, microbenchmark, unit tests, and mutable-head fuzz target.

## What was accepted into IoTox rev0003

### Product placement

Mutorr is accepted as an **optional IoTox subsystem**, not as a replacement product
name and not as a prerequisite for basic device command/control.

The product remains IoTox. The namespace replication module retains the
`iotox::mutorr` namespace because the name usefully distinguishes mutable heads and
content-addressed object replication from ordinary device commands and state events.

### Small-circle topology

The deterministic circle planner is a strong research primitive:

- every peer with the same membership snapshot computes the same result;
- discovery order does not matter;
- application degree remains bounded;
- a new member changes only nearby ring neighborhoods;
- small memberships safely collapse to a complete local graph;
- topology planning has no toxcore dependency and is easy to simulate.

The default four-neighbor shape remains provisional rather than universal. Device
class, namespace purpose, failure model, and expected online fraction may justify a
different degree.

### Rendezvous custodians

Highest-random-weight placement is a good fit for deterministic replica preference.
The allocation-free fixed-capacity hot path is useful C++ engineering and was retained.

The current score mixer remains explicitly research-only. It is not a cryptographic
hash and does not defend against identity grinding. Hostile or open membership requires
a cryptographic or keyed placement score and an authorization-controlled identity
creation policy.

### Linked mutable heads

The fixed-size canonical record is useful because it fits comfortably inside one Tox
lossless custom packet, can be fuzzed independently, and makes the signing boundary
explicit.

The record is not frozen as an interoperable protocol. In particular, rev0003 keeps
open whether `previous` should identify the prior content root or the digest of the
complete prior head. A previous-head digest offers stronger linkage of metadata and
writer history, while a previous-root link is simpler for state lineage. This needs a
specific threat and recovery analysis before wire freeze.

### Control/object lane separation

The branch's split is accepted in principle:

```text
small signed announcements and bounded inventories -> Tox lossless packets
large immutable objects                            -> Tox file transfer
```

IoTox should not build a second bulk-fragmentation protocol inside custom packets when
Tox already has a file-transfer facility.

## What was deliberately not accepted as complete

The branch does not yet provide:

- signed or consensus-backed namespace membership epochs;
- authorization integration;
- cryptographic signing or verification;
- cryptographic content digests;
- application-layer object encryption;
- an immutable object store;
- gossip deduplication, retry, queue bounds, or anti-entropy;
- durable head or object persistence;
- Tox file-transfer wiring;
- liveness-aware custodian repair;
- deletion, retention, quota, or storage-pressure semantics;
- multi-writer conflict or CRDT semantics;
- real toxcore or public-network replication evidence.

The branch correctly describes many of these omissions. rev0003 preserves that honesty.

## Important integration decisions

### Authorization precedes Cube construction

A Cube is built from the authorization ledger's namespace membership snapshot. Tox
friendship, online status, relay reachability, or storage capacity does not itself make
a peer a namespace member.

Future inputs will likely include:

```text
namespace ID
membership epoch
member application identity
role or storage capability
validity interval
signed membership record
```

The current `Cube` receives only IDs and configuration. Epoch and authorization checks
belong in the layer that constructs it.

### Tox relationships should be reused

A device may be neighbors with the same peer in several namespaces. The connection
scheduler should maintain the union of required application neighbors and reuse one
Tox relationship rather than opening a separate transport relationship per Cube.

### Custody does not imply readability

A future custodian may retain encrypted immutable objects without holding a namespace
content key. Authorization to store, read, write, merge, actuate, and administer must
remain distinct.

### Basic IoT remains independent

Mutorr must not make a one-device command path heavier. IoTox should still support a
small agent that only needs owner re-entry, authorization, commands, state, results,
and optional file transfer.

## Technical review notes

### Strengths

- Fixed-size identifiers and records make bounds obvious.
- Sorting once gives deterministic topology and logarithmic lookup.
- Flat adjacency storage is compact and cache-friendly.
- The custodian hot path avoids allocation and full sorting.
- Head comparison is constant-time with respect to object count.
- The implementation compiles under strict GCC and Clang warnings.
- Existing ASan/UBSan, TSan, fuzz, and benchmark lanes fit IoTox's testing culture.
- The module has no hidden network side effects.

### Risks and questions

#### Membership disagreement

Two honest peers with different membership snapshots compute different neighbors and
custodians. A signed epoch alone does not resolve concurrent or partitioned membership
changes. The ledger needs a transition authority and reconciliation rule.

#### Identity grinding

An attacker able to create many authorized IDs may bias ring position or placement.
Authorization limits the attack surface, but high-consequence deployments may also
need keyed placement and enrollment controls.

#### Ring robustness

Four neighbors provide bounded degree but no guarantee that messages propagate under
correlated offline behavior. Simulations should vary online probability, churn,
partitions, and degree. Custodian selection and gossip topology need not use identical
peer sets.

#### Announcement flooding

A ring flood still requires bounded message-ID caches, hop or expiry controls, retry,
and protection against a peer generating endless unique announcements.

#### Head equivocation

A writer can sign two different heads for the same generation. The current evaluator
labels that a conflict, but policy must decide whether to retain both proofs, quarantine
the writer, request history, alert owners, or merge at the application layer.

#### Clock use

`created_unix_ms` is metadata, not a safe ordering source. IoT devices may have bad
clocks. Generation and signed lineage should determine stream order; clocks should be
advisory and bounded.

#### Object confidentiality and metadata

Content addressing leaks equality unless objects are encrypted or salted appropriately.
Even encrypted objects can expose size, timing, access patterns, and namespace activity.
The object model needs explicit privacy goals.

#### Deletion

Immutable replication makes deletion a policy event rather than simple overwriting.
Revocation, retention expiry, tombstones, cryptographic erasure, and offline custodians
need a coherent design.

#### Resource fairness

Rendezvous placement distributes namespace slots, not bytes or write rate. A future
placement input may need capacity classes, weights, quotas, or separate hot/cold
custodians without making results unstable or gameable.

## rev0003 integration changes

The following were integrated into the main IoTox tree:

- C++ `iotox::mutorr` ID, Cube, and HeadRecord implementations;
- the reserved Mutorr message types in the IoTox frame enum;
- 13 Mutorr-related C++ tests from the branch, producing 25 combined tests before
  rev0003-specific additions;
- the mutable-head fuzz target and corpus;
- the native benchmark, renamed `iotox_bench`;
- `iotox cube-demo`;
- build matrix support and package planning;
- original contribution documents and reports under history directories.

One small hardening change was added during integration: Cube construction now rejects
the reserved all-zero member identifier.

## Recommended next experiment

Do not wire Mutorr directly to the public Tox network yet. The next useful replication
slice is a deterministic in-memory simulator with:

- signed or test-signed membership epochs;
- bounded per-peer queues;
- message IDs and deduplication;
- offline/online schedules;
- head gossip and missing-history requests;
- an in-memory immutable object store;
- custodian failure and repair;
- metrics for convergence, duplicate traffic, path length, and replica availability.

That simulator can tell us whether small circles remain attractive under failure,
rather than only under a static thirty-node diagram. In parallel, the base IoTox path
still needs a pinned real c-toxcore two-peer fixture.
