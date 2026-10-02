# IoTox roadmap

## rev0001 — completed foundation

- C++20 build and test facility.
- GCC and Clang presets.
- ASan/UBSan and GCC ThreadSanitizer paths.
- Runtime c-toxcore adapter.
- One Tox owner thread.
- Atomic savedata persistence.
- Initial custom-packet frame.
- Network-stack type model.
- Deterministic toxcore ABI integration mock.
- Ratox successor and multi-route planning documents.

## rev0002 — completed decisions and recall-root testbed

- Accepted permanent printed/memorized re-entry as a product feature.
- Frozen `iotox-recall-root-v1` Argon2id parameters and normalization.
- Pinned and retained the 7,776-entry EFF word list.
- Added eight-word structural validation.
- Added a C++ runtime Argon2 ABI adapter and exact C++ mock.
- Added a real Argon2 known-answer CTest.
- Accepted that offline guessing is inherent and phrase entropy is structural.
- Rejected any vendor-held device-reassignment key.
- Kept Tox as the primary peer network and adopted a contribution/stewardship intent.
- Confirmed that authorization lives in an independent ledger, not the Tox friend list.
- Added recovery, ownership, threat, vision, open-question, and research documents.

## rev0003 candidate — real toxcore and re-entry experiment

Primary goal: replace “Tox ABI integration proven against the exact mock” with “two real Tox peers and the first memory-reentry hypothesis proven against pinned c-toxcore.”

Candidate work:

- reproducibly fetch or vendor a verified c-toxcore source archive;
- build minimum non-A/V dependencies;
- compile ABI-verification code against official tox headers;
- add typed bootstrap and TCP-relay configuration;
- create a controlled local bootstrap/relay fixture;
- run two real Tox identities;
- exchange IoTox `HELLO` frames;
- restart both identities from savedata;
- add secret-key import and deterministic no-spam support to the adapter;
- select a reviewed domain-separated KDF for recall-root subkeys;
- derive a test-only deterministic controller Tox identity;
- erase its friend savedata and test device-originated reintroduction;
- record memory, threads, descriptors, bootstrap latency, reconnect, and idle behavior.

## rev0004 candidate — local API and service shell

- Unix `SOCK_SEQPACKET` control endpoint;
- length-prefixed fallback where necessary;
- request/response IDs and structured errors;
- service lifecycle and signal handling;
- bounded, cancellable command/event queues;
- deadline semantics that prevent timed-out physical commands from executing later;
- status and metrics endpoints;
- small CLI client separate from the daemon.

## rev0005 candidate — authorization ledger

- stable application device identity;
- owner signing identity and route-binding format;
- delegated controller keys;
- roles and capability grants;
- ownership epochs;
- revocation and expiry;
- signed device certificates used for roster reconstruction;
- rollback-resistant ledger persistence;
- root-transition protocol for a compromised phrase.

## rev0006 candidate — durable protocol

- select and constrain CBOR implementation;
- hello/capabilities negotiation;
- durable inbox and outbox;
- expiry, retry, deduplication, and idempotent result cache;
- application receipt states;
- state snapshot plus incremental event model;
- queue pressure and full-disk tests.

## later

- physical initial-claim ceremony;
- file-transfer manager;
- signed OTA manifests and anti-rollback;
- ratox-style filesystem façade;
- public and owner-operated Tox bootstrap/relay deployment tooling;
- Tox/Tor experiment and route proof;
- Tox/I2P experiment and route proof;
- target-hardware power and reliability testing;
- optional owner-operated mailbox/automation hub;
- evaluation of direct I2P/Tor transports as separate projects.
