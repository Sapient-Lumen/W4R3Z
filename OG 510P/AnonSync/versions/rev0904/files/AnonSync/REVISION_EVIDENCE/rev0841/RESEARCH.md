# AnonSync rev0841 research notes

Accessed 2026-07-18. These sources informed the implementation and speculation. They do
not imply that AnonSync implements the cited standards or systems.

## Locale-independent machine integers

The C++ `to_chars` facility specifies direct character conversion without stream locale.
Rev0841 uses integer `std::to_chars` in the v3 signing and JSON owner instead of relying on
`std::ostringstream` and ambient `num_put`/`numpunct` behavior.

- Current C++ working draft, character conversion:
  https://eel.is/c++draft/charconv.to.chars
- Current C++ working draft, iostream locale behavior:
  https://eel.is/c++draft/iostreams.base

## Deterministic signed JSON

RFC 8785 exists because semantically equivalent JSON can have multiple byte
representations, while hashes and signatures need invariant bytes. It also calls out
locale-independent serialization. Rev0841 does **not** implement JCS: it defines a local
length-framed signing format and a fixed JSON representation with integer-only numeric
fields.

- RFC 8785, JSON Canonicalization Scheme:
  https://www.rfc-editor.org/rfc/rfc8785.html
- RFC 8259, JSON grammar:
  https://www.rfc-editor.org/rfc/rfc8259.html

## Convergence is a semantic property

CRDT literature defines convergence in terms of replicas that receive the same updates
reaching the same state by deterministic rules. This is the missing proof target for
AnonSync: valid local evidence and hash chains are useful prerequisites but do not define
concurrent update/delete semantics or guarantee replica agreement.

- Preguiça, Baquero, Shapiro, “Conflict-free Replicated Data Types (CRDTs)”:
  https://arxiv.org/abs/1805.06358
- Kleppmann and Beresford, “A Conflict-Free Replicated JSON Datatype”:
  https://arxiv.org/abs/1608.03960

## SQLite is one part of a larger recovery protocol

SQLite documents atomic commit assumptions, WAL/checkpoint behavior, and the requirement
to treat a database and its hot journal/WAL as a state family. AnonSync already handles
many of these details, but its external receipts, atomic files, and downstream effects
must be analyzed in the same crash-state machine rather than independently.

- SQLite atomic commit:
  https://www.sqlite.org/atomiccommit.html
- SQLite write-ahead log:
  https://www.sqlite.org/wal.html
- SQLite online backup API:
  https://www.sqlite.org/backup.html
- SQLite corruption and durability assumptions:
  https://www.sqlite.org/howtocorrupt.html

## Authentication is not anonymity or recovery after compromise

The MLS architecture explicitly separates a cryptographic group protocol from delivery,
identity/authentication infrastructure, metadata decisions, multi-device synchronization,
and application policy. It describes forward secrecy and post-compromise security as
properties that depend on epoch updates and key deletion. This is a useful warning for
AnonSync: signing lifecycle evidence is not a privacy architecture, and multi-device state
synchronization can itself weaken recovery after compromise.

- RFC 9420, Messaging Layer Security protocol:
  https://www.rfc-editor.org/rfc/rfc9420.html
- RFC 9750, Messaging Layer Security architecture:
  https://www.rfc-editor.org/rfc/rfc9750.html

## Hostile parsing needs layered isolation

Linux kernel documentation states that seccomp filtering is not by itself a sandbox; it
reduces exposed kernel surface. Landlock adds self-imposed filesystem/network access
restrictions. A future AnonSync hostile-input worker should combine these with process,
namespace, descriptor, resource, and protocol constraints.

- Linux seccomp filter documentation:
  https://docs.kernel.org/userspace-api/seccomp_filter.html
- Linux Landlock documentation:
  https://docs.kernel.org/userspace-api/landlock.html

## Speculation

A useful long-term shape is a two-plane system. The data plane stores encrypted,
content-addressed chunks and never decides semantic conflicts. The control plane carries
small authenticated operations with explicit causal references, object/key epochs,
revocation facts, and convergence semantics. Each local durable transition consumes one
frozen authority capsule and emits a digest-bound recovery receipt. A deterministic model
then becomes both the protocol specification and the oracle for generated histories.
