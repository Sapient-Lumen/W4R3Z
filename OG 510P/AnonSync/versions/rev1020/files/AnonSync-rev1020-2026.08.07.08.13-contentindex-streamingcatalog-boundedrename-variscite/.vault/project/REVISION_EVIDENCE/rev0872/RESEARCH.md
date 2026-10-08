# Online primary-source research: rev0872

Sources were accessed on 2026-07-21. They constrain design and support
speculation; they are not evidence that AnonSync implements the cited systems'
guarantees.

## Clock semantics and leases

- Linux `clock_gettime(3)`: https://man7.org/linux/man-pages/man3/clock_gettime.3.html
- Gray and Cheriton, *Leases*: https://web.eecs.umich.edu/~mosharaf/Readings/Leases.pdf
- NTPv4, RFC 5905: https://www.rfc-editor.org/info/rfc5905/

`CLOCK_REALTIME` can jump; Linux monotonic clocks are boot-relative, and
`CLOCK_BOOTTIME` differs by including suspend. A raw monotonic reading is
therefore not a stable cross-reboot epoch. Lease correctness also needs a stated
clock-error/drift model. Rev0872 only prevents accepted local observations from
moving backward; it does not authenticate the source or bound forward error.

## Transaction cutpoint

- SQLite transactions: https://sqlite.org/lang_transaction.html

`BEGIN IMMEDIATE` obtains write authority up front and staged changes become
visible atomically at commit. The clock transition therefore belongs in the
same transaction as the lease mutation it authorizes, with precommit
restoration/reattestation and unrelated work outside the writer interval.

## Attempt identity and expiry

- Amazon SQS visibility timeout: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html
- SQS visibility change API: https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_ChangeMessageVisibility.html
- Google Pub/Sub exactly-once delivery: https://docs.cloud.google.com/pubsub/docs/exactly-once-delivery

These systems separate message identity, delivery-attempt receipt, visibility
lease, and terminal acknowledgment. Their documentation reinforces that stale
or expired attempt identifiers must not settle newer work. Rev0872 covers only
a sender-local durable attempt/expiry boundary, not a managed exactly-once or
receiver effect protocol.

## Logical order versus physical time

- etcd API guarantees: https://etcd.io/docs/v3.6/learning/api_guarantees/
- Hybrid logical clocks: https://cse.buffalo.edu/tech-reports/2014-04.pdf

etcd revisions illustrate logical publication order; HLCs combine causal order
with approximate physical time and anomaly bounds. Neither should be confused
with proof that a physical lease expired. AnonSync therefore keeps evidence
generation and the liveness high-water separate.

## Speculation

The next highest-leverage slice is an owned clock observation record paired
with a receiver terminal/effect owner, not another wire wrapper. The durable
fence is useful because it turns rollback into an explicit rejected input, but
it also concentrates forward-jump risk. A future design should quarantine
implausible jumps, bind observations to boot/source identity and uncertainty,
and require explicit recovery rather than silently lowering the fence.
