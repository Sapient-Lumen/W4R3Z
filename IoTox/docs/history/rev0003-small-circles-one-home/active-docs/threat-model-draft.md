# IoTox threat-model draft

This is a planning document, not a completed security review.

## Security goals

- The device remains owned by the party authorized under its current IoTox ownership
  epoch, not by the vendor or transport infrastructure.
- A remembered RecallRoot phrase can reproduce owner authority under the fixed v1
  contract without an IoTox service.
- Tox peers receive only the application powers explicitly granted to them.
- Commands cannot be silently replayed, duplicated, delayed past policy, or mistaken for
  successful execution merely because transport delivery succeeded.
- Requested Tor/I2P routing does not silently leak through native networking.
- Namespace members receive only the read, write, store, or administrative powers they
  need.
- Replicated object bytes are accepted only after bounded validation and cryptographic
  integrity checks.
- Compromise of IoTox-operated bootstrap/relay infrastructure does not confer ownership,
  authorization, or decryption authority.

## Assets

- RecallRoot phrase and derived root;
- owner application signing keys;
- delegated controller keys;
- device stable identity and endpoint bindings;
- Tox secret keys, no-spam state, and savedata;
- authorization ledger, ownership epochs, roles, capabilities, and revocations;
- physical claim and reset controls;
- actuator authority;
- sensor data and local history;
- durable command/result queues;
- firmware trust roots and anti-rollback counters;
- route configuration and privacy policy;
- namespace membership epochs;
- mutable-head signing keys and linked histories;
- immutable object keys, digests, bytes, manifests, and metadata;
- custodian placement and replica health;
- logs, diagnostics, and audit evidence.

## Adversaries

- unauthenticated Internet peer;
- Tox friend without IoTox authorization;
- revoked former owner or household member;
- compromised authorized controller;
- attacker who learns or guesses the RecallRoot phrase;
- attacker with only a weak human-created phrase guess model;
- malicious or compromised bootstrap/relay infrastructure;
- malicious namespace member;
- compromised custodian;
- local unprivileged process;
- local root or physical attacker;
- manufacturer or supply-chain compromise;
- malicious update source;
- attacker able to create many candidate identities;
- operator mistake and accidental data loss.

## Failure model

- packet replay, delay, duplication, corruption, and reordering above reconnects;
- sleeping mobile controllers and intermittently connected devices;
- NAT and relay changes;
- wrong wall clocks and clock rollback;
- process crash, power failure, and storage corruption;
- full filesystem and exhausted quotas;
- queue saturation and reconnect storms;
- partial namespace membership views;
- device joins, removals, and simultaneous policy changes;
- custodians offline, withholding, or deleting objects;
- interrupted file transfers;
- route proxy/router restart;
- dependency ABI drift or unavailable shared libraries.

## RecallRoot threat

RecallRoot-v1 uses a fixed public salt and fixed parameters so the same phrase derives
the same root without stored metadata. This permits offline guessing and cross-user
amortization.

The supported phrase is eight independently and uniformly generated words from a
7,776-entry list, approximately 103.4 bits of nominal entropy. A quotation, favorite
sentence, keyboard pattern, or owner-composed phrase is not equivalent.

Security requirements:

- creation flows generate rather than solicit prose;
- the phrase and root never enter logs, argv, environment, metrics, crash reports, or
  network messages;
- derived domains are separated;
- daily-use devices hold delegated keys when possible;
- local derivation is rate-controlled against denial of service;
- documentation states that phrase compromise is owner-root compromise.

No architecture can allow universal memory-only re-entry while denying an attacker who
has exactly the same phrase and equivalent device access. Root transition, alerts,
quorum, or physical interlocks can change race conditions, not that fact.

## No vendor recovery authority

IoTox holds no key capable of replacing a customer owner. Manufacturer keys may attest
hardware or firmware but must not authorize ownership reassignment.

A product-class-specific local factory reset may erase the prior ownership domain. It
must not reveal old owner secrets merely because physical reset was invoked.

## Tox assumptions and defense in depth

Tox provides encrypted sessions and public-key transport identity. IoTox should still
bind high-consequence messages to:

```text
target device identity
sender application identity
ownership epoch
authorization grant
message/request ID
freshness or expiry
operation payload
application signature
```

A Tox friend is not automatically an owner, operator, namespace member, firmware
installer, or custodian.

c-toxcore is a security-sensitive dependency and should be pinned, sandboxed where
possible, fuzzed, monitored for updates, and replaceable behind the current narrow
boundary.

## Command risks

### Duplicate or ambiguous execution

A command may execute and lose its result during reconnect. Retrying without a durable
idempotency record can repeat a physical action.

Controls:

- stable command IDs;
- durable acceptance and terminal result records;
- explicit idempotency classification;
- deadlines and `EXPIRED` results;
- cancellation and shutdown semantics that prevent late surprise execution.

### Queue exhaustion

A peer can generate unique commands, results, or subscriptions until memory or disk is
exhausted.

Controls:

- per-peer and global bounds;
- authorization before expensive work;
- priority and backpressure;
- admission quotas;
- bounded diagnostic output;
- safe full-disk behavior.

## Authorization-ledger risks

- rollback to a pre-revocation ledger;
- concurrent owner transitions;
- forged or overbroad grants;
- ambiguous capability inheritance;
- expired grants accepted due to bad clocks;
- compromised daily controller attempting root-level operations;
- stale endpoint bindings after Tox key rotation.

Controls require canonical signed records, ownership epochs, monotonic/rollback-resistant
state where available, explicit transition authority, bounded expiry semantics, and
physical interlocks for high-consequence changes.

## Mutorr namespace risks

### Stale or split membership

Different snapshots produce different neighbors and custodians. An attacker may keep a
victim on an old epoch or exploit concurrent transitions.

Controls:

- signed membership epochs or snapshot digests;
- bounded overlap/reconciliation;
- explicit transition authority;
- rejection or quarantine of unknown epochs;
- anti-entropy for policy records as well as data.

### Identity grinding

The current fast rendezvous mixer is not cryptographic. A participant able to choose
many identities may bias ring position or custody.

Controls:

- authorized enrollment;
- cryptographic or keyed placement score;
- stable application identities;
- cost or rate limits on identity creation where relevant.

### Gossip amplification

A malicious member can emit endless unique heads or wants.

Controls:

- message-ID and head-ID deduplication;
- per-peer rate and work limits;
- bounded hop/expiry policy;
- authorization before forwarding;
- request coalescing;
- inventory and want count bounds.

### Equivocation and rollback

A writer may sign different heads for the same generation, withhold history, or replay
old but valid heads.

Controls:

- retain signed conflict evidence;
- bind namespace, writer, membership epoch, and lineage;
- monotonic local observations;
- request linked history;
- policy for quarantine, owner alert, and application merge;
- review whether the previous link should hash the complete prior head.

### Compromised custodians

A custodian may withhold, corrupt, selectively serve, or delete data.

Controls:

- cryptographic object verification;
- replication factor and repair;
- anti-entropy;
- multiple independent sources;
- custody is a preference, not a proof;
- owner-visible availability metrics.

### Unauthorized readability

Tox link encryption does not prevent an authorized storage peer from reading plaintext
objects it receives.

Controls:

- application-layer authenticated encryption;
- separate store/read capabilities;
- namespace keys and reader envelopes;
- rotation after removal;
- minimize clear metadata.

### Equality and metadata leakage

Content addressing and deterministic placement may reveal object equality, namespace
activity, size, timing, member sets, or access patterns.

Controls depend on the eventual object and encryption model. Privacy claims must be
specific rather than assuming “encrypted” means metadata-free.

### Deletion and revoked members

Immutable objects can remain on offline custodians. A revoked reader may retain old
keys and copies.

Controls and limitations:

- revocation can protect future content through key rotation;
- it cannot make a former authorized reader forget plaintext already obtained;
- tombstones and retention policy can request deletion but cannot prove every offline
  copy disappeared;
- cryptographic erasure can make retained ciphertext useless when keys are destroyed,
  subject to previous key exposure.

## Route privacy and leak risk

Reusing one Tox identity across native, Tor, and I2P routes makes those routes linkable.
Separate route identities improve unlinkability but complicate re-entry and authorization.

Reserved routes must fail closed. Future route tests must inspect sockets, DNS, UDP,
local discovery, relay endpoints, proxy restart, and fallback behavior.

Three simultaneous routes may improve reachability while increasing resource use and
cross-route correlation. Route policy must be explicit per device and peer.

## Local interface risks

A Unix socket or ratox-style filesystem surface can be attacked by local processes.
Future controls include:

- restrictive filesystem modes;
- peer credentials;
- local capability policy;
- bounded requests and subscriptions;
- no secret input through argv;
- safe FIFO behavior and no blocking network thread on local consumers;
- audit without secret leakage.

## Update risks

Firmware transfer authorization is separate from firmware authenticity.

Requirements:

- signed manifests;
- target model/hardware constraints;
- artifact digest and size;
- storage reservation;
- anti-rollback counter;
- staged verification;
- A/B or equivalent recovery;
- health confirmation;
- no assumption that an authorized Tox peer may install arbitrary code.

## Current rev0003 security boundary

Implemented security-related mechanisms:

- exact RecallRoot-v1 parsing and derivation context;
- known-answer Argon2 test;
- explicit secret-buffer wiping where the adapter controls memory;
- strict fixed IoTox frame bounds;
- private atomic Tox savedata replacement;
- one-owner-thread toxcore boundary;
- fail-closed reserved routes;
- fixed-size Mutorr IDs and heads;
- rejection of zero member IDs, duplicates, malformed heads, and oversized frames;
- C++ mocks, sanitizers, and fuzz targets.

Not implemented:

- owner/application signatures;
- live re-entry;
- authorization ledger;
- durable command semantics;
- cryptographic Mutorr scoring, object digests, or encryption;
- membership epochs;
- live Tox replication;
- Tor/I2P routing;
- independent security audit.

No deployment should treat the current research binary as sufficient protection for
locks, medical systems, safety controls, or high-consequence industrial equipment.
