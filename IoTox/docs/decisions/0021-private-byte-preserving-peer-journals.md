# ADR 0021: Peer journals are private, bounded, and byte-preserving

**Status:** accepted and implemented in rev0006

## Context

Ratox made incoming text observable through ordinary files. IoTox needs the same composable
quality without assuming that every Tox byte string is valid UTF-8, allowing unbounded logs,
or copying sensitive packet bodies into a global diagnostic stream.

## Decision

Each projected peer directory may contain two separate private journals:

```text
messages           Tox human text, action text, and read receipts
protocol           successfully decoded IoTox lossless frames
```

Records are one physical line. Control characters, non-printable bytes, backslashes, and
field delimiters are escaped; original byte length is recorded. Journals rotate at bounded
thresholds to `messages.previous` and `protocol.previous`. Runtime directories are owner-only
and files are mode `0600`. The global event journal records metadata but not message or packet
payloads.

## Consequences

Shell tools can inspect and follow useful traffic without corrupting line framing. The files
remain observational projections, not durable delivery queues or an authorization ledger.
Payload logging is itself sensitive: operators must protect the runtime root, choose
retention policy, and eventually be able to disable or redact journals for privacy-critical
deployments.
