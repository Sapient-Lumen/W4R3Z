# Scenario — tonic concurrency limit per connection is not a process-total limit

This scenario exists so the archive does not flatten a truthful local limit into a global throughput promise.

The important support truths are:

- the limit is per connection,
- total in-flight requests multiply with concurrent connections,
- and summaries should not present the value as one process-wide cap.
