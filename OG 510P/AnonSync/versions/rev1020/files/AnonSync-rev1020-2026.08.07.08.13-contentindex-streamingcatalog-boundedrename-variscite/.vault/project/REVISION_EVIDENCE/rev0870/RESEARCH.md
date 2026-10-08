# Research notes: AnonSync rev0870

Access date for all online sources: **2026-07-21**.

These sources are design analogies and boundary checks. They do not establish
AMQP or Amazon SQS compliance, and they do not prove that rev0870 implements an
authenticated remote acknowledgement protocol.

## Attempt-specific delivery identity

AMQP 1.0 transport associates each unsettled delivery with a delivery tag that
is unique within the link while unsettled; settlement ends that association.
Its recovery model also makes duplicate transfer possible when the outcome is
uncertain.

- https://docs.oasis-open.org/amqp/core/v1.0/csprd01/amqp-core-transport-v1.0-csprd01.html

Amazon SQS similarly returns a new receipt handle for each receive and directs a
consumer to delete with the most recent handle. A visibility timeout makes a
message eligible for another receive; it is not itself deletion or settlement.
SQS also documents at-least-once delivery and the possibility of duplicates.

- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_DeleteMessage.html
- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html

The architecture lesson used here is narrow: durable work identity and one
attempt's authority to retire that work are different objects. Rev0870's local
claim ID plays the second role. It is not copied as a claim of wire-protocol
compatibility and is not a cryptographic receiver attestation.

## SQLite transaction authority

SQLite documents that `BEGIN IMMEDIATE` starts a write transaction immediately
and can fail with `SQLITE_BUSY` when another writer owns the database. SQLite
allows multiple readers but only one writer. WAL mode changes reader/writer and
checkpoint behavior but does not remove the single-writer rule or the need to
distinguish transaction commit from later checkpoint/durability policy.

- https://sqlite.org/lang_transaction.html
- https://sqlite.org/wal.html

Rev0870 uses the single-writer transaction as local serialization authority and
re-attests the complete staged cutpoint before commit. This is a correctness
construction above SQLite's transaction semantics, not a claim that the default
VFS or filesystem has been qualified for every power-loss profile.

## Speculative architecture

A plausible next shape has two independent receipt layers:

1. a **local attempt capability**, minted inside the sender database and used to
   fence workers, lease replacement, retry release, and local settlement; and
2. an **authenticated receiver outcome**, bound to peer identity, operation ID,
   receiver durable generation, result, and protocol epoch.

The sender should settle only when a valid receiver outcome is presented while
the matching local capability is still current. The receiver should persist an
idempotency record before publishing that outcome. On ambiguous network failure,
the sender may retry with a new local capability while the receiver returns the
same durable outcome for the same operation. This preserves at-least-once
transport behavior without allowing either a stale local worker or a replayed
remote message to retire unrelated current work.

For performance, the current O(history) owner should remain an oracle while a
bounded point-read scheduler and incremental projector are introduced. Each
optimized mutation can be replayed against the oracle in test, periodic audit,
and repair modes. Deleting the oracle before differential equivalence would
trade visible waste for much harder-to-detect authority drift.
