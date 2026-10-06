# Amoeba lesson: immutable object files + “name → capability set” directories

Amoeba is an older distributed OS that did two things that map surprisingly well onto DeriveBSD’s worldview:

1) its **Bullet server** stored *immutable files* (create once, read many)

2) its **directory server** mapped human names to **capability sets** (multiple replicas, location-transparent)

The practical lesson is not “build a distributed OS like Amoeba.”
It’s that *immutability + capability references + indirection* make replication and revocation much easier to reason about.

## The Bullet server idea: immutable files as a performance and reliability tool

Immutable files enable:
- simple caching (whole-file caching is safe)
- replication without coherence nightmares
- atomic updates by writing a new object and swapping the directory entry

DeriveBSD already embraces immutability for store objects and artifacts.
The Bullet-server framing is useful because it emphasizes the operational win:
**writes become “publish a new object”** rather than “mutate shared state.”

## Directory server idea: indirection makes revocation and HA cheap

Amoeba’s directory server maps a name to a **set** of capabilities (replicas).
Clients can try any replica; failures are handled by retrying another.

DeriveBSD already needs the same indirection for:
- channels → current release digest
- cache endpoints → redundant mirrors / witness builders
- portals → revocable handles

Amoeba’s “capability set” is a nice mental model for:
- *multi-origin distribution* without losing digest identity
- *revocation-by-pointer* (rotate what the name points at)

## DeriveBSD translation

### 1) Treat “names” as pointers, not authority

A stable name (channel, alias, component URL) should resolve to a digest-bound object.
Authority comes from:
- the caller’s leases/grants
- trust policy for the resolved digest

This prevents a whole class of “I guessed the path” / “I found the URL” ambient authority bugs.

### 2) Model redundancy explicitly

Where we can, represent “this object is available from multiple places” as an explicit set:
- multiple caches
- multiple witnesses
- multiple transport lanes

Then record *which one was used* as evidence.

See: `docs/46-cache-trust-model.md`, `docs/190-cache-witness-quorums-trustix.md`, `docs/301-p2p-distribution-and-swarm-caches.md`.

### 3) Avoid making replication a hidden implementation detail

Replication is not just a reliability detail; it affects trust and explainability.
DeriveBSD should keep replication a **policy-visible** choice:
- which sources are acceptable
- when to require multiple corroborations

## References

- “Amoeba: a distributed operating system for the 1990s” (Mullender et al.): https://www.cs.cornell.edu/home/rvr/papers/Amoeba1990s.pdf
- “The Amoeba Distributed Operating System – A Status Report” (Tanenbaum): https://www.cs.vu.nl/~ast/Publications/Papers/compcom-1991.pdf

Last updated: 2026-02-27
