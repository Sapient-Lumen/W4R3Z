# rev0003 contents

## Identity

- project: **IoTox**;
- revision: `rev0003`;
- version: `0.3.0`;
- codename: **Small Circles, One Home**;
- implementation boundary: C++20 for every IoTox-owned product, test, mock, fuzz,
  simulation, and benchmark translation unit.

## C++ foundation retained

- CMake/Ninja project with strict warning policy;
- GCC debug/release and Clang debug builds;
- Clang ASan/UBSan and GCC TSan lanes;
- runtime c-toxcore 0.2 ABI adapter;
- exact C++ toxcore shared-library mock;
- one owner thread per Tox instance;
- callback-to-event translation;
- friend acceptance and lossless packet exchange;
- private atomic savedata persistence;
- strict versioned IoTox lossless frame;
- explicit Tox/native, Tox/Tor, and Tox/I2P route model;
- fail-closed reserved routes;
- frozen RecallRoot-v1 Argon2id contract and pinned EFF word list;
- exact Argon2 ABI mock plus real known-answer test.

## rev0003 Small Circles integration

- reviewed Milehigh `IoToxmutorr` source archive and provenance digest;
- preserved original branch documents and text reports;
- `iotox::mutorr::Id256` fixed identifiers;
- deterministic authorized-member `Cube` topology;
- default four-neighbor symmetric small circle;
- fixed-capacity rendezvous custodian selection;
- default replication factor of three;
- fixed 221-byte mutable-head record;
- 157-byte canonical signing body and opaque 64-byte signature slot;
- linked-head progression classification;
- provisional Mutorr head/inventory/want/object-offer frame types;
- `iotox cube-demo` and `iotox_bench`;
- mutable-head fuzzer and corpus;
- zero-identity rejection hardening.

Mutorr remains an optional namespace replication subsystem. Basic IoTox pairing,
command, state, and result paths are not required to use it.

## Owner and authority direction

- a permanent generated phrase reconstructs the RecallRoot-v1 owner root;
- offline guessing is accepted by design and phrase entropy is structural;
- IoTox has no vendor key capable of reassigning customer devices;
- Tox friendship is transport state, not authorization;
- an independent ledger will hold roles, capabilities, epochs, membership, delegation,
  and revocation;
- Tox remains the primary network;
- owner/community bootstrap and TCP-relay contribution remains part of the plan;
- native, future Tor-routed Tox, and future I2P-routed Tox are explicit route choices;
- direct Tor/I2P transports remain separate and outside this build.

## Tests and evidence

- 25 registered compiled C++ tests;
- six CTest command checks;
- passing GCC debug, Clang debug, Clang ASan/UBSan, GCC TSan, and GCC release lanes;
- two Clang libFuzzer smoke targets, 5,000 runs each;
- native Cube/head microbenchmark;
- mock identity save/reload and mode-0600 evidence;
- exact negative-route and malformed-CLI evidence;
- file type, runtime dependency, exported-symbol, word-list, and checksum reports;
- current Linux x86-64 convenience binaries;
- retained rev0001 artifact set;
- rev0002 verification metadata;
- Milehigh branch reports and source SHA-256.

The matrix found and rev0003 fixed a real owner-thread startup publication race. A
successful `start()` now guarantees that `running()` is observable and immediate public
operations are valid; the integration test records the invariant.

## Documents

- `docs/what-iotox-is-becoming.md`;
- integrated architecture, vision, roadmap, protocol, networks, threat model, testing,
  and open questions;
- RecallRoot and ownership/recovery research;
- ratox successor assessment;
- ADR index and ADR 0008 for optional Mutorr replication;
- Milehigh contribution review;
- rev0003 build and performance reports;
- preserved rev0002 and Milehigh design records under `docs/history/`.

## Deliberately absent

The cube does not contain a real c-toxcore implementation, Tor, I2P, ratox source, or a
complete IoT product. It does not claim:

- two genuine connected Tox peers;
- public bootstrap, DHT, NAT, or relay proof;
- real Tox file transfer;
- live RecallRoot re-entry;
- an implemented authorization ledger;
- durable command/result queues and idempotency;
- cryptographically complete Mutorr membership, placement, signing, hashing,
  encryption, storage, gossip, anti-entropy, repair, deletion, or multi-writer policy;
- Tox-over-Tor or Tox-over-I2P operation;
- target-hardware power or reliability measurements;
- independent security or licensing approval.
