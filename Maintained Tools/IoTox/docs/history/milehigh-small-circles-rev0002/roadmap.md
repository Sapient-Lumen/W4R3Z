# IoToxmutorr roadmap

## rev0001 — completed Tox foundation

- C++20 build and test facility;
- runtime c-toxcore adapter and one Tox owner thread;
- atomic identity persistence;
- initial custom-packet frame;
- deterministic ABI integration mock;
- explicit transport/route model.

## rev0002 — completed Small Circles Cube

- deterministic namespace-scoped member ring;
- default four-neighbor bounded topology;
- rendezvous-hashed durable custodians;
- allocation-free placement hot path;
- fixed-size linked mutable-head format;
- head progression classification;
- native Cube demo, benchmark, tests, and fuzzing seed.

## rev0003 candidate — in-memory replication simulation

- C++ membership epoch and subscription model;
- bounded message-ID deduplication window;
- `MUTORR_HEAD`, inventory, want, and offer payload codecs;
- deterministic multi-node event simulator using the Cube adjacency;
- gossip propagation, duplicate suppression, retry, and churn tests;
- immutable in-memory object store keyed by caller-provided 256-bit digests;
- convergence and transfer-volume metrics for 30, 100, and 1,000 simulated devices.

## rev0004 candidate — cryptographic and durable object core

- select a constrained signing implementation and expose a narrow C++ adapter;
- select cryptographic digest implementation for object identities;
- Merkle directory and chunk manifest;
- durable head/object store with atomic index updates;
- anti-rollback and fork-history policy;
- bounded inventories and sparse anti-entropy.

## rev0005 candidate — Tox wiring

- typed bootstrap and TCP relay configuration;
- two pinned real toxcore nodes;
- connect Cube neighbors as ordinary Tox friends rather than a group chat;
- exchange head/inventory/want messages;
- transfer immutable objects through Tox file transfer;
- restart from savedata and durable Mutorr state;
- measure resource use and transfer amplification.

## Later

- local Unix-domain API and service lifecycle;
- physical claim ceremony, ownership, roles, and capabilities;
- multi-writer append-only chat feeds and merged views;
- CRDT evaluation for collaboratively edited structured directories;
- ratox-style filesystem/FIFO facade over the structured API;
- OTA manifests and anti-rollback;
- Tox/Tor and Tox/I2P route experiments;
- target-hardware reliability and power testing.
