# Rev0952 research notes

Consulted 2026-07-30.

## Syncthing Block Exchange Protocol v1

- https://docs.syncthing.net/specs/bep-v1.html

Syncthing distinguishes a full index from later index updates and binds durable
continuation to index identity and monotonic sequence. The useful precedent is
that a small continuation token is meaningful only when paired with a specific
authoritative dataset. Rev0952 follows the narrow part of that rule: its
inspection count/cursor is accepted only on the same authenticated catalog and
visible-replica basis. It is not yet an incremental index or remote change log.

## Syncthing scanning and watching

- https://docs.syncthing.net/users/syncing.html

Syncthing combines filesystem watching with periodic full scans because watcher
notifications can be missed. This supports AnonSync's existing authority split:
watchers wake work, while descriptor-rooted complete epochs remain repair and
absence authority. The rev0952 remote sweep similarly bounds asynchronous
coverage without claiming a point-in-time filesystem snapshot.

## SQLite isolation and transactions

- https://sqlite.org/isolation.html
- https://sqlite.org/lang_transaction.html

SQLite readers observe a stable transaction snapshot, and `BEGIN IMMEDIATE`
acquires the write transaction up front or reports contention. Rev0952 keeps the
remote progress singleton in the catalog database and uses optimistic exact-old-
state update plus re-read inside the retained transaction owner. This serializes
cursor/sweep publication within that database. It does not create atomicity with
the replica database, payload namespace, or filesystem; the digest basis and
apply-before-progress order are the conservative bridge.

## Linux `openat2(2)` resolution controls

- https://man7.org/linux/man-pages/man2/openat2.2.html

`RESOLVE_BENEATH`, `RESOLVE_IN_ROOT`, and magic-link restrictions illustrate the
kernel-level shape needed to keep pathname resolution beneath an owned root.
AnonSync's remote inspection frontier deliberately counts descriptor-rooted
path checks rather than treating string validation as filesystem authority.

## Inference

A durable cursor alone cannot prove completion when the indexed dataset changes.
A count alone cannot prove which cyclic prefix was covered. The combination of
basis, origin, acknowledged count, and current cursor makes accidental or
corrupt continuation detectable without letting scheduling metadata authorize
content. The next step should move from repeated full projection restoration to
a durable exact index/change sequence, while retaining complete rooted scans as
rebuild and rotating-scrub oracles.
