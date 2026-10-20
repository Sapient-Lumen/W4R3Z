# Threat-model seed

This is a planning document, not a completed threat model.

## Assets

- device Tox secret key and savedata;
- owner and delegated-controller identities;
- claim secret and ownership records;
- actuator authority;
- sensor data and local history;
- firmware signing trust roots;
- durable command and result queues;
- namespace membership epochs and authorization records;
- mutable-head signing keys, signatures, and linked history;
- immutable object digests, objects, and custodian placement;
- audit records;
- route configuration and privacy policy.

## Adversaries and failures

- unauthenticated Internet peer;
- Tox friend without IoTox authorization;
- revoked former owner or household member;
- compromised authorized controller;
- malicious or compromised bootstrap/relay infrastructure;
- local unprivileged process;
- local root or physical attacker;
- supply-chain compromise;
- replay, delay, duplication, and reordering above reconnect boundaries;
- power loss and storage corruption;
- route fallback that leaks traffic outside Tor or I2P;
- resource-exhaustion attacks against queues, decoders, transfers, or logs.
- malicious identity grinding to bias ring position or custodian placement;
- stale or split membership views that produce divergent Cube plans;
- signed rollback, fork, equivocation, or deletion of mutable heads;
- inventory amplification and requests for nonexistent objects;
- compromised custodians withholding, corrupting, or selectively serving objects.

## Initial security rules

1. A Tox friend is a transport peer, not automatically an authorized operator.
2. No physical action executes without an IoTox authorization decision.
3. Every externally supplied length and count is bounded before allocation.
4. Hardware-affecting commands are idempotent or explicitly marked otherwise.
5. Expired commands do not execute.
6. Firmware is independently signed and anti-rollback protected.
7. Tox savedata is replaced atomically and protected with least-privilege file modes.
8. Reserved routes fail closed and never silently become native routes.
9. Toxcore remains sandboxed and replaceable behind a narrow boundary.
10. Recovery and ownership transfer work without a mandatory vendor service.
11. A Cube is built only from namespace-authorized identities; connectivity does not imply membership.
12. Mutable-head generation is never trusted without signature, namespace, writer, and chain validation.
13. Immutable object bytes are accepted only after a cryptographic digest match.
14. Custodian placement is availability policy, not proof that data exists; anti-entropy verifies replicas.
15. Membership snapshots require explicit epochs and bounded reconciliation before hostile deployment.

## rev0002 cryptographic boundary

rev0002 defines canonical head bytes but does not implement signing or cryptographic content hashing. Its fast rendezvous mixer is deterministic placement machinery, not an adversarially secure primitive. Synthetic IDs are test fixtures only. No deployment should treat the current Cube core as sufficient authentication or integrity protection by itself.

## Open privacy decision

Reusing one Tox identity across native, Tor, and I2P routes may make the routes linkable. Separate identities reduce direct linkage but create synchronization and authorization complexity. The product must choose deliberately rather than allowing implementation convenience to decide.
