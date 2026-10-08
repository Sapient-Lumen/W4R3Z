# Online primary-source research: rev0873

Sources were accessed on 2026-07-21. They constrain the design and support the
speculation below; they are not evidence that AnonSync implements the cited
systems' guarantees.

## SQLite transaction and migration boundaries

- SQLite transactions: https://sqlite.org/lang_transaction.html
- SQLite ALTER TABLE: https://www.sqlite.org/lang_altertable.html

SQLite documents `BEGIN IMMEDIATE` as acquiring write-transaction authority up
front, and its generalized schema-change procedure rebuilds exact tables rather
than pretending every change is a safe in-place column append. Rev0873 therefore
migrates historical schemas inside one immediate transaction, attests the exact
historical contract, rebuilds the v4 protocol surface, restores the intended
state independently, and only then commits.

## Visibility, attempts, retries, and terminal handling

- Amazon SQS visibility timeout:
  https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html
- Amazon SQS timely processing:
  https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/best-practices-processing-messages-timely-manner.html
- Amazon SQS delay queues:
  https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-delay-queues.html
- Google Pub/Sub exactly-once delivery:
  https://docs.cloud.google.com/pubsub/docs/exactly-once-delivery
- Google Pub/Sub lease management:
  https://docs.cloud.google.com/pubsub/docs/lease-management
- Google Pub/Sub subscription retry policy:
  https://docs.cloud.google.com/pubsub/docs/subscription-retry-policy
- Google Pub/Sub dead-letter topics:
  https://docs.cloud.google.com/pubsub/docs/dead-letter-topics
- Google Pub/Sub basics:
  https://docs.cloud.google.com/pubsub/docs/pubsub-basics

These systems expose separate concepts for immutable message/work identity,
one delivery attempt's receipt, temporary visibility/acknowledgment lease,
retry delay, redelivery, and terminal/dead-letter treatment. That separation
supports AnonSync's decision not to overload one digest or deadline with all of
those meanings. Rev0873 closes only durable retry-mint provenance; it does not
provide managed exactly-once delivery or a terminal receiver effect protocol.

## Clock semantics

- Linux `clock_gettime(3)`:
  https://man7.org/linux/man-pages/man3/clock_gettime.3.html

Linux documents monotonic clocks as relative to an unspecified point, with
`CLOCK_MONOTONIC` tied to time since boot on Linux and `CLOCK_BOOTTIME` differing
by suspend accounting. Persisting either raw value across reboot as if it were a
stable epoch would be unsound without boot identity and recovery semantics.
Rev0873 therefore retains accepted caller observations honestly but does not
claim a trusted clock.

## Speculation

The highest-leverage next slice is not another digest wrapper. It is an owned
clock-observation and retry-decision record paired with an indexed scheduler.
The record should bind source/boot identity, uncertainty, anomaly state, failure
class, attempt age/count, deterministic backoff/jitter input, and terminal
policy. That would make a wake deadline explain both *when* it was minted and
*why* retry authority still exists.

In parallel, a receiver terminal/effect owner is more important than broadening
sender settlement. Without an idempotent crash-consistent receiver cutpoint,
ambiguous network response can still duplicate an external effect even when the
sender's local receipt protocol is exact.
