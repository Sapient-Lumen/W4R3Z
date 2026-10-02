# Threat-model draft

This is a planning document, not a completed security review.

## Product security promises under consideration

- Devices remain useful without an IoTox account or mandatory vendor cloud.
- The owner can reproduce a stable recall root from a permanent eight-word phrase.
- IoTox has no key capable of reassigning customer devices.
- Tox is a transport and reachability substrate, not the authorization ledger.
- Reserved Tor/I2P routes fail closed.
- Physical actions require an application-level authorization decision.

## Assets

- permanent recall phrase;
- 32-byte recall root;
- owner application signing key;
- route-specific Tox secret keys and no-spam values;
- device identity keys;
- Tox savedata and friend state;
- authorization ledger and ownership epochs;
- delegated controller identities;
- claim material and owner-signed device certificates;
- actuator authority;
- sensor data and local history;
- firmware-signing trust roots;
- durable command/result queues;
- audit records;
- route configuration and privacy policy.

## Adversaries and failures

- attacker who photographs or learns the printed recall phrase;
- attacker performing unlimited offline phrase guesses;
- unauthenticated Internet peer;
- Tox friend without IoTox authorization;
- revoked former owner or household member;
- compromised delegated controller;
- malicious or compromised bootstrap/relay infrastructure;
- local unprivileged process;
- local root or physical attacker;
- supply-chain compromise;
- hostile or malformed dependency library;
- replay, delay, duplication, and reordering across reconnects;
- power loss, storage corruption, and rollback to old ledger state;
- route fallback that leaks traffic outside Tor or I2P;
- resource exhaustion against queues, decoders, KDF calls, transfers, or logs.

## Recall-root threat statement

The permanent phrase is a bearer root.

```text
knowledge of phrase = ability to reproduce recall root
```

This is not a defect to be obscured by a reset flow. It is the mechanism that permits re-entry from memory.

The security boundary therefore depends on both:

1. structural generation entropy; and
2. physical/cognitive protection of the phrase.

Argon2id makes each guess consume resources. It does not make a chosen lyric or familiar sentence unpredictable. There is no online rate limit, per-user secret salt, vendor-held pepper, or lockout service.

Eight uniform selections from 7,776 words provide approximately 103.4 bits of nominal generation entropy. That figure is false for owner-selected words, biased randomness, photographed cards, cloud notes, terminal logs, or compromised generation software.

## Phrase compromise response

The architecture needs a signed owner-root transition from ownership epoch N to N+1. Once a device accepts the transition, the old root must no longer authorize operations or further transitions.

Open attack: an adversary with the old phrase may race the legitimate owner. Possible controls include:

- multi-controller approval for root transition;
- local physical confirmation;
- transition delay and conspicuous alerts;
- device-class-specific interlocks;
- rollback-resistant monotonic storage;
- owner-selected quorum policies.

No control can preserve universal phrase re-entry while denying an undetected attacker who has the same phrase and equivalent access. The product must state that honestly.

## Lost phrase

IoTox support cannot reproduce or reset the old owner root.

A device may offer local destructive factory reset depending on product class. Such reset erases the prior ownership domain and user data; it does not recover prior secrets. Some high-consequence devices may deliberately require a stronger physical service procedure or disallow field reset.

## Initial security rules

1. A Tox friend is a transport peer, not automatically an authorized operator.
2. No physical action executes without an IoTox authorization-ledger decision.
3. The recall phrase is never sent to an IoTox service or device peer.
4. The recall root is domain-separated before use by distinct cryptographic functions.
5. Daily-use controllers should use delegated keys rather than retaining the high-value root indefinitely.
6. Every externally supplied length and count is bounded before allocation.
7. Hardware-affecting commands are idempotent or explicitly marked otherwise.
8. Expired commands do not execute.
9. Firmware is independently signed and anti-rollback protected.
10. Tox savedata and authorization state are replaced atomically with least-privilege modes.
11. Ownership epochs and revocations must resist storage rollback.
12. Reserved routes fail closed and never silently become native routes.
13. Toxcore and Argon2 remain replaceable behind narrow boundaries.
14. IoTox operates no universal recovery or device-reassignment key.
15. Logs, argv, environment, crash dumps, and metrics never contain real recall phrases or roots.

## Tox-layer assumptions and defense in depth

Tox provides encrypted peer sessions and public-key transport identity. IoTox should still sign high-consequence application commands with delegated application keys, include the target device identity and ownership epoch, and enforce expiry and replay protection.

That permits the device to ask both:

```text
Did this arrive through an expected Tox peer session?
Was this exact operation signed by an authorized IoTox principal for this device and epoch?
```

A transport defect should not automatically become actuator authority.

## Route privacy decision

Reusing one Tox identity across native, Tor, and I2P routes can link them. Separate route identities reduce direct linkage but complicate re-entry and authorization.

The likely direction is one stable application owner identity with separately derived route endpoint identities and signed bindings. The exact privacy mode must be selectable and explicit; implementation convenience must not silently decide it.

## KDF denial of service

RecallRoot-v1 intentionally consumes 64 MiB and four lanes. Secret derivation must never be exposed as an unauthenticated network operation. Local software should rate-limit failed phrase attempts, prevent parallel derivation storms, and communicate resource requirements on constrained systems.

## Outstanding reviews

- independent cryptographic review of the key hierarchy and transition protocol;
- real c-toxcore security/update review and sandbox design;
- phrase-generation implementation and randomness tests;
- secure input/memory design on Linux, mobile, and desktop controllers;
- physical reset and interlock policies by device class;
- Tor/I2P leak tests;
- licensing and supply-chain review.
