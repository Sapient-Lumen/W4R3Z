# IoTox roadmap

## Guiding rule

Build the shortest end-to-end spine before adding the widest feature canopy.

IoTox now has two coherent research tracks:

```text
spine:   owner re-entry -> authorization -> command/result -> real Tox
canopy:  authorized namespace -> small-circle gossip -> encrypted objects -> repair
```

The canopy must not block or complicate the spine. Both tracks share identity,
authorization, protocol, persistence, testing, and Tox transport boundaries.

## rev0001 — completed: Just Werx Foundation

- C++20 build and test facility;
- GCC, Clang, ASan/UBSan, TSan, and frame fuzzing;
- runtime c-toxcore adapter;
- one Tox owner thread;
- atomic private savedata persistence;
- initial strict lossless custom-packet frame;
- exact C++ toxcore ABI mock;
- explicit transport/route model;
- ratox-style façade preserved as a future surface.

## rev0002 — completed: Home From Memory

- permanent RecallRoot-v1 decision;
- eight-word EFF-list phrase contract;
- fixed Argon2id parameters and real known-answer test;
- no vendor recovery or reassignment authority;
- independent authorization-ledger decision;
- Tox retained as primary network and infrastructure commons;
- more precise `adapter-verified` network status;
- expanded recovery, ownership, threat, and offline-guessing analysis.

## rev0003 — completed: Small Circles, One Home

- reviewed the Milehigh IoToxmutorr branch;
- preserved its original design documents and reports;
- absorbed C++ fixed identifiers, Cube topology, rendezvous custodians, and linked heads;
- kept IoTox as the product and Mutorr as an optional subsystem;
- added provisional Mutorr control message types;
- integrated the Cube demo, native benchmark, tests, fuzz target, and corpus;
- added explicit analysis of namespace membership, confidentiality, deletion, churn,
  previous-root versus previous-head linkage, and side-project salvageability;
- merged the ownership and small-circle visions into one architecture.

## rev0004 candidate — real native Tox gate

This is the highest-priority implementation slice.

- obtain or build a pinned c-toxcore revision reproducibly;
- compile the adapter against official headers in at least one lane;
- package a known compatible toxcore runtime for the fixture;
- add typed bootstrap-node and TCP-relay configuration;
- run two genuine IoTox peers in a controlled fixture;
- exchange `HELLO` frames in both directions;
- restart both peers from savedata and verify stable identities;
- test disconnect, relay-only mode, reconnect, and duplicate packet behavior;
- exercise one real Tox file transfer;
- record memory, descriptors, threads, idle CPU, and traffic;
- distinguish build-, integration-, network-, and target-verified status.

A local/private Tox fixture is sufficient for this gate; public-network dependence should
not make the test nondeterministic.

## rev0005 candidate — owner key hierarchy and re-entry simulation

- freeze domain-separated labels beneath RecallRoot-v1;
- select or isolate the application signing primitive;
- define deterministic/reproducible controller Tox key material and no-spam behavior;
- define device identity and signed route-endpoint bindings;
- implement a challenge-response re-entry transcript that never sends the phrase/root;
- add ownership epoch and replay protection;
- simulate total controller-state loss and reconstruction from the known-answer phrase;
- document phrase compromise, transition races, and physical interlocks;
- add test vectors independent of the main implementation.

## rev0006 candidate — authorization ledger and durable command core

- canonical authorization-ledger records;
- owner, administrator, operator, viewer, automation, and storage capability primitives;
- delegated controller keys and expiry;
- revocation and ownership transition;
- atomic ledger persistence and rollback detection;
- bounded durable inbox/outbox;
- message ID generation and deduplication;
- `RECEIVED`, `STARTED`, `SUCCEEDED`, `FAILED`, and `EXPIRED` results;
- precise timeout, cancellation, shutdown, and idempotency semantics;
- full-disk, power-loss, duplicate-command, and clock-skew tests.

## rev0007 candidate — Mutorr in-memory convergence simulator

This track begins only after it can consume explicit authorization/membership records.

- signed or deterministic test membership epochs;
- per-namespace subscriptions and capabilities;
- bounded message-ID deduplication windows;
- codecs for head, inventory, want, and object offer;
- deterministic multi-node event simulation over Cube adjacency;
- online/offline schedules, churn, partitions, retry, and queue pressure;
- in-memory immutable object store keyed by caller-provided 256-bit IDs;
- custodian failure, withholding, and repair;
- convergence, duplicate traffic, path length, and availability metrics;
- experiments at 30, 100, and 1,000 simulated devices;
- compare degrees 2, 4, 6, and adaptive policies rather than assuming four forever.

## rev0008 candidate — cryptographic object and membership core

- choose cryptographic or keyed rendezvous scoring;
- choose object digest representation;
- choose authenticated encryption and namespace content-key model;
- key envelopes and member removal/rotation;
- decide previous-root versus previous-head digest linkage;
- signature verification and equivocation evidence;
- Merkle directory/chunk manifests;
- durable encrypted object store and atomic indexes;
- storage quota, retention, tombstone, and cryptographic-erasure policy;
- sparse anti-entropy and bounded inventory summaries.

## rev0009 candidate — live Tox replication

- map authorized Cube-neighbor requirements onto reusable Tox relationships;
- exchange head, inventory, want, and offer messages through real Tox;
- transfer immutable objects through Tox file transfer;
- resume or recover interrupted transfers;
- restart from savedata, ledger, queues, heads, and objects;
- measure amplification, convergence, memory, disk, and power;
- test malicious payloads, stale epochs, forks, revoked members, and unavailable
  custodians.

## rev0010 candidate — local product surface

- supervised daemon lifecycle;
- Unix `SOCK_SEQPACKET` or framed-stream API;
- peer credentials and local capability policy;
- subscriptions and structured errors;
- command-line client;
- ratox-style files/FIFOs over the structured core;
- export/import and diagnostics;
- initial hardware adapters for one safe test device class.

## Later network routes

### Tox/Tor

- TCP-only toxcore policy;
- explicit proxy/stream plumbing;
- no UDP, local discovery, native DNS, or silent fallback;
- route-leak tests;
- relay/bootstrap reachability and latency measurements;
- identity-linkability modes.

### Tox/I2P

- explicit local I2P stream-tunnel arrangement;
- owner/community Tox relay endpoints reachable through I2P;
- bootstrap, restart, idle resource, and route-leak tests;
- stable-destination and identity-binding policy.

### Direct overlays

Direct Tor and direct I2P transports remain separate future experiments. They do not
share Tox's identity, friendship, packet, or file-transfer semantics merely because
they use the same route names.

## Continuous work

Every revision should continue:

- strict GCC and Clang builds;
- sanitizer and fuzz execution;
- checksummed artifacts and reports;
- accurate status language;
- threat-model updates;
- source and decision provenance;
- preservation of prior datacube history;
- upstream Tox contributions where appropriate;
- target-hardware measurements as soon as hardware exists.

## Stop conditions and salvage

IoTox may remain a side project or stop before the full roadmap. Each stage should
therefore produce something independently useful. A failed route experiment should not
invalidate the C++ toxcore harness. An unfinished replication engine should not prevent
a useful ratox successor. A product that never ships can still contribute tests,
servers, fixes, measurements, and clear design records to the Tox ecosystem.
