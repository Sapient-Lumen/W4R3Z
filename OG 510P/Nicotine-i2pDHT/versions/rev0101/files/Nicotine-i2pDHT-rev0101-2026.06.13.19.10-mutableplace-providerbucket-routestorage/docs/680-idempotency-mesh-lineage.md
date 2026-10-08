# Idempotency mesh lineage

The idempotency mesh joins original ACK evidence, retry settlement, retry publication staging, and egress journal compaction. It catches key drift, payload drift, boundary drift, replay, same-sequence forks, and dropped contradiction evidence.

The design guess is that idempotency keys should be carried as local lineage evidence, not trusted as a guarantee of exactly-once delivery.
