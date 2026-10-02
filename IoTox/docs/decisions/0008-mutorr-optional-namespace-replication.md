# ADR 0008: Mutorr is an optional namespace replication layer inside IoTox

**Status:** accepted for rev0003

## Context

The Milehigh IoToxmutorr branch demonstrates a deterministic small-circle topology,
rendezvous custodian selection, and linked mutable-head record for selective replication
over Tox.

The work fits IoTox's self-owned direction, but renaming or redefining the entire
product around replication would risk making ordinary device command/control depend on
a much larger distributed-data problem.

## Decision

Keep **IoTox** as the product and project name.

Absorb `iotox::mutorr` as an optional application-layer subsystem for namespaces that
need multi-peer durable replication.

- Basic IoTox commands, state, pairing, recovery, and authorization must work without
  Mutorr.
- A Mutorr Cube is constructed only from an explicitly authorized namespace membership
  snapshot supplied by the IoTox authorization layer.
- The default research topology is a symmetric four-neighbor circle.
- The default research replica preference is three rendezvous-selected custodians.
- Small announcements use IoTox lossless control packets; large immutable objects are
  intended to use Tox file transfer.
- Tox remains the peer transport and may reuse one relationship across many namespaces.
- The current placement mixer, mutable-head fields, message numbers, and default degree
  are provisional and are not frozen as a hostile-network protocol.
- Custody, readability, write authority, actuation authority, and administration remain
  separate capabilities.

## Consequences

- IoTox can remain a small ratox-inspired device agent for simple deployments.
- Larger owner-defined systems gain a path toward selective shared state without one
  full application mesh or one global chatroom.
- Namespace membership epochs, object encryption, signatures, digests, anti-entropy,
  durability, deletion, quotas, and multi-writer semantics remain required work.
- The project retains a clean separation between owner authority, namespace policy,
  replication planning, and Tox connectivity.
- The IoToxmutorr contribution is preserved in the datacube history and credited as the
  source of the Small Circles research branch.
