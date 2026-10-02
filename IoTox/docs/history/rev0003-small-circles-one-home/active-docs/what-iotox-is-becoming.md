# What IoTox is and is becoming

## The compact answer

IoTox is becoming a self-owned networking and coordination layer for physical things.

A device gets a durable identity, speaks to its owner and trusted peers through Tox,
keeps functioning without an IoTox account or mandatory cloud, and exposes a small,
inspectable local interface inspired by ratox. The owner can reconstruct the owner
side of the relationship from a permanent phrase. Authorization remains an IoTox
policy above Tox friendship. When several authorized devices need to share durable
state, an optional Mutorr layer can arrange them into namespace-sized small circles
instead of one global mesh.

The desired product feeling is still simple:

```text
remember phrase
reach devices
pair people and controllers
read state
send command
receive result
share selected data
keep working without the vendor
```

The implementation underneath that feeling must be explicit about identity,
authorization, replay, durability, routing, privacy, recovery, and failure.

## What IoTox already is

The current project is a C++20 research agent and test facility. It has several
working architectural boundaries:

- one C++ owner thread exclusively controls each toxcore instance;
- c-toxcore is isolated behind a narrow runtime ABI adapter;
- Tox savedata is replaced through private temporary files and atomic rename;
- Tox/native, Tox/Tor, and Tox/I2P are represented as one peer transport with
  different routes, while direct Tor and direct I2P remain separate future transports;
- reserved routes fail closed instead of silently leaking through native networking;
- lossless custom packets carry a strict versioned IoTox frame;
- the permanent RecallRoot-v1 contract derives one reproducible owner root from
  eight generated EFF-list words through a frozen Argon2id contract;
- IoTox contains no vendor key capable of reassigning customer devices;
- Tox friendship is deliberately separate from IoTox authorization;
- GCC, Clang, sanitizers, fuzzing, exact C ABI mocks, and native tests are part of
  the project rather than release-time decorations.

These pieces do not yet make a complete networked product. They do make the project
more than a mood board: the boundaries can be compiled, tested, broken, measured,
and replaced.

## What the Milehigh branch contributed

The user-supplied IoToxmutorr branch asked a useful next question:

> When a household or small organization has many devices and multiple shared
> datasets, must every peer maintain a direct application relationship with every
> other peer?

Its answer is a namespace-scoped **Cube**:

- only devices authorized for one namespace participate in that namespace;
- all members sort the same stable 256-bit identities into a ring;
- each member normally keeps two predecessors and two successors as replication
  neighbors;
- small head and inventory announcements gossip around that bounded circle;
- deterministic rendezvous placement selects a few custodians to retain durable
  copies;
- the mutable item is a small linked head, while content beneath it is intended to
  be immutable and content-addressed.

For thirty members, a four-neighbor circle uses sixty undirected application edges
rather than the 435 edges of a complete mesh. The planner is deterministic, independent
of discovery order, inexpensive to execute, and isolated from toxcore. It therefore
fits the existing IoTox architecture surprisingly well.

rev0003 absorbs the C++ implementation, tests, benchmark, fuzz target, documents,
and build evidence from that branch. It does **not** rename the product to IoToxmutorr.
Mutorr is an optional subsystem inside IoTox.

## The emerging stack

The combined direction now looks like this:

```text
                 owner memory / printed phrase
                            |
                    RecallRoot-v1
                            |
         domain-separated owner and recovery authority
                            |
              independent authorization ledger
              roles / grants / epochs / revocation
                            |
             +--------------+---------------+
             |                              |
      device commands                 shared namespaces
      state and results               optional Mutorr layer
             |                         small circles
             |                         signed heads
             |                         custodians
             +--------------+---------------+
                            |
                     IoTox protocol
                            |
                           Tox
              native / future Tor / future I2P
                            |
              owner and community infrastructure
```

The layers have different jobs.

### RecallRoot-v1

RecallRoot-v1 gives the owner a portable, vendor-independent point of re-entry.
The phrase is not a support password and is not sent to a server. It reproduces an
owner-side root from memory or paper under a fixed public Argon2id contract.

This intentionally permits offline guessing. The supported phrase format therefore
requires generated entropy rather than comforting prose. The root must later be
split into domain-separated keys; daily controllers should use delegated keys rather
than carrying the root everywhere.

### Authorization ledger

The authorization ledger decides who may do what. It will eventually hold owner
roots, controller keys, roles, capabilities, namespace memberships, expirations,
ownership epochs, and revocations.

A Tox friend can be connected and still be unauthorized. A Mutorr custodian can
store encrypted objects and still be unable to read or control them. A controller
can be revoked without pretending the entire device has a new physical identity.

### Command and state plane

The base IoTox product remains a device agent. It needs dependable commands, state
snapshots, state events, results, acknowledgements, durable queues, deadlines,
idempotency, and explicit errors.

This path must remain useful without Mutorr. A single thermostat and one owner should
not need a distributed object graph merely to change a set point.

### Mutorr namespace plane

Mutorr is for data that benefits from selective multi-peer replication:

```text
home/config
workshop/sensors
camera/archive
family/shared
controller/backups
```

Each namespace gets its own authorized membership snapshot and topology. This avoids
turning the entire household into one chatroom or one full mesh. The application may
use small Tox packets for heads and inventories, then Tox file transfer for larger
immutable objects.

Mutorr is not yet a finished replication protocol. The current C++ code is a topology,
placement, and head-format research core.

### Tox transport and routes

Tox remains the default connection fabric because it already provides the difficult
peer-network properties that made ratox compelling: long-term identities, encrypted
sessions, bootstrap discovery, NAT traversal, relays, lossless custom packets, and
file transfer.

IoTox intends to contribute useful bootstrap and TCP-relay capacity, reproducible
server tooling, measurements, documentation, and upstream fixes. Infrastructure
participation grants no ownership authority.

Tor and I2P remain planned routes for Tox, not substitutes in the current build.
The direct-overlay possibilities stay architecturally separate.

### Ratox-style local surface

The outside should retain ratox's beauty. A future Unix façade may expose ordinary
files, FIFOs, or command-line operations such as:

```text
/run/iotox/self/address
/run/iotox/status
/run/iotox/peers/<id>/online
/run/iotox/peers/<id>/events
/run/iotox/peers/<id>/command
```

Those surfaces will translate into structured requests. They will not themselves be
the authorization database or durable queue. The goal is a simple surface that does
not lie about whether a command was merely written, durably accepted, authorized,
executed, or completed.

## The larger dream

IoTox could let a physical thing belong to its owner in a stronger sense than most
consumer IoT products permit.

A device could boot with its own identity, be claimed without a vendor account, retain
local function when the Internet is gone, and remain reachable after the owner loses
every controller but remembers the phrase. The owner could operate a hub on a NAS,
router, Raspberry Pi, or VPS without making that hub the sovereign owner. Devices
could coordinate locally and replicate selected encrypted state without sending it
to an IoTox cloud.

The most interesting future is not merely a phone turning on a light. It is a small,
owner-defined society of devices:

- a sensor reports to the few peers authorized for its namespace;
- a home controller retains durable queues while phones sleep;
- a NAS becomes a custodian for encrypted camera archives;
- controllers can be replaced or revoked without replacing every device;
- local automation survives loss of the public Internet;
- the owner can inspect, script, export, and replace the software surface;
- native Tox, Tor-routed Tox, and I2P-routed Tox provide explicit connectivity choices.

The phrase “from memory, you can reach your devices” and the small-circles idea belong
together. The first gives the human a durable way home. The second gives the devices
a bounded way to carry selected parts of that home for one another.

## What IoTox is not becoming

IoTox is not intended to become:

- a mandatory vendor account system;
- a vendor-held recovery or reassignment service;
- one giant Tox group used as a database bus;
- a blockchain, public consensus network, or token system;
- a global storage swarm in which every friend receives every object;
- a silent traffic multiplexer that uses native networking after Tor or I2P was requested;
- a framework that makes simple devices depend on the optional replication engine;
- a claim that transport encryption alone settles application authorization;
- a promise that unimplemented cryptography or public-network behavior already works.

## The difficult work now visible

The combined design exposes several hard problems rather than solving them by naming
them.

### Real Tox proof

The current toxcore path is adapter-verified against an exact C++ shared-library mock.
A real pinned c-toxcore build, controlled bootstrap/relay fixture, two genuine peers,
restart, reconnect, file transfer, NAT testing, and target-device measurements remain
the decisive networking gate.

### Re-entry protocol

RecallRoot-v1 derives a root, but the exact subkey tree, deterministic controller Tox
identity, no-spam handling, device discovery, challenge-response handshake, ownership
epoch binding, and phrase-compromise transition protocol are not frozen.

### Authorization ledger

Roles and capabilities are accepted architecture, not implemented state. The ledger
needs canonical serialization, signatures, delegation, revocation, expiry, rollback
resistance, conflict rules, and atomic persistence.

### Namespace membership

A Cube assumes every participant has the same authorized membership snapshot. The
system still needs signed membership epochs, reconciliation under stale views,
join/leave rules, and behavior when two authorized controllers propose conflicting
membership changes.

### Cryptographic placement and heads

The current rendezvous mixer is deterministic and fast but not adversarially secure.
It must be replaced or keyed before hostile identities can influence placement.
The mutable head carries canonical bytes and a 64-byte signature slot but no selected
signature implementation. The current `previous` field links the previous root,
not necessarily the digest of the complete previous head; that choice needs review
before the wire format freezes.

### Confidential replication

A custodian should not automatically become a reader. Objects likely need namespace
content keys, authenticated encryption, key envelopes for authorized members, and a
rotation story when a member is removed. Deletion, retention, quotas, and secure
metadata exposure also need explicit policy.

### Multi-writer state

One writer can advance one linked stream. Several writers require merged append-only
views, CRDTs, or application-specific conflict semantics. Comparing generation numbers
from different writers would be incorrect.

### Availability and churn

Deterministic custodians are a placement preference, not proof that replicas exist.
The system needs liveness, anti-entropy, repair, queue bounds, sleep-aware retry,
storage-pressure behavior, and resistance to withholding or amplification attacks.

### Privacy across routes

Reusing one Tox identity across native, Tor, and I2P routes links those routes.
Separate route identities improve unlinkability but complicate recall, authorization,
and peer mapping. This remains an explicit product choice.

## Why the side-project posture is acceptable

IoTox may not become a commercial product. That is not a reason to fake certainty or
avoid building it.

The project can still leave useful things behind:

- a current C++ toxcore integration and test harness;
- atomic savedata and strict owner-thread patterns;
- reproducible Tox bootstrap/relay deployment work;
- a documented permanent recall-root experiment;
- an authorization-ledger design;
- a deterministic small-circle and rendezvous planner;
- protocol fuzz targets and failure tests;
- upstream toxcore fixes, measurements, and documentation;
- a ratox-inspired agent that is useful even without the full dream.

Each revision should therefore be a buildable datacube rather than a promise of future
completion. The cube should preserve decisions, code, tests, evidence, uncertainty,
and branch provenance. If work stops, the last cube should still be understandable and
salvageable by somebody else.

## The near-term shape

The project should resist the urge to implement every layer simultaneously. The
coherent order remains:

1. build and run a pinned real c-toxcore;
2. prove two native IoTox peers and persistence across restart;
3. freeze domain-separated RecallRoot subkeys and a re-entry handshake;
4. implement the independent authorization ledger;
5. add bounded durable command/result queues;
6. simulate signed membership epochs and Mutorr gossip in memory;
7. select signature, digest, and authenticated-encryption boundaries;
8. wire small announcements and bulk object transfer through real Tox;
9. add the structured local socket and ratox-style façade;
10. investigate Tor- and I2P-routed Tox with leak tests and explicit policy.

The direction is no longer merely “Tox for IoT.” It is becoming:

> a small, honest, owner-reconstructible device network in which Tox supplies the
> roads, IoTox supplies authority, ratox supplies the sense of simplicity, and
> optional small circles let trusted devices carry selected state for one another.
