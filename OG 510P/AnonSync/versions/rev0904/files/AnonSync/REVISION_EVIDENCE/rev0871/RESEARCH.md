# Online primary-source research: rev0871

Sources were revisited on 2026-07-21. They are analogies and design constraints,
not evidence that AnonSync implements the external systems' guarantees.

## Amazon SQS

- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_ChangeMessageVisibility.html
- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_DeleteMessage.html
- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-queue-message-identifiers.html
- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/troubleshooting-api-errors.html

SQS separates a current receipt handle from visibility timeout and permits
bounded timeout changes. The relevant lesson is that a stale handle must not
control a later receive attempt, and lease extension needs its own explicit
operation and ceiling. AnonSync deliberately chooses a stricter local rule:
expiry itself revokes all terminal authority even before replacement.

## Google Cloud Pub/Sub

- https://docs.cloud.google.com/pubsub/docs/exactly-once-delivery
- https://docs.cloud.google.com/pubsub/docs/lease-management

Pub/Sub documents acknowledgment-ID freshness and lease extension as distinct
correctness surfaces. This supports treating claim identity, deadline, renewal,
and terminal receiver outcome as separate authority owners. Rev0871 implements
only the sender-local claim/deadline/renewal slice; it does not claim Pub/Sub's
managed exactly-once behavior.

## OASIS AMQP 1.0

- https://docs.oasis-open.org/amqp/core/v1.0/csprd01/amqp-core-transport-v1.0-csprd01.html

AMQP tracks each unsettled delivery attempt with a delivery tag and separates
delivery state from settlement. This reinforces the need for durable attempt
identity and a future authenticated terminal receiver state. Rev0871 has no
AMQP transport or receiver disposition protocol.

## SQLite

- https://sqlite.org/lang_transaction.html
- https://sqlite.org/wal.html

SQLite's explicit transaction and one-writer behavior make writer-lock duration
an authority and availability concern. Moving randomness before `BEGIN
IMMEDIATE` reduces avoidable lock residence while the subsequent transaction
still reloads and binds the exact cutpoint before publication.

## Speculation

The next coherent vertical slice is not more sender-local queue machinery. It
is an authenticated terminal receiver record bound to exact operation bytes,
receiver actor epoch, sender attempt receipt, transport channel, and key epoch,
with receiver-side idempotent effect ownership. After that, a trusted clock or
persisted high-water policy and an owned heartbeat/wake scheduler can turn the
current API into an operational protocol. Until those owners exist, adding more
wire wrappers would create surface area without closing the end-to-end proof.
