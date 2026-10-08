# FT-0062 closure — minimal transport/adapter binding

## Frontier closed

FT-0062 asked for the smallest transport/adapter binding that can carry TimeSync objects over existing timing, control, management, telemetry, and retention boundaries without making TimeSync a protocol.

## Closure decision

rev0063 closes the frontier with three objects:

```text
transport envelope
adapter catalog record
retained assessment export
```

The envelope carries one semantic payload. The adapter catalog says what class of carrier is being used and which payload types it can carry. Retained export wraps a local assessed state with export context.

## Anti-expansion rule

The closure intentionally rejects protocol behavior:

```text
no negotiation state machine
no retransmission semantics
no clock discipline
no source selection
no profile fallback table in transport
no transport metadata in TimeState
```

## Security decision

Envelope integrity is useful but not a replacement for profile-reference digest or signed profile binding. Profile-reference strength remains scoped inside `assessed_profile`.

## Residual question

The next frontier is not transport. It is evaluator evidence: how little evidence-summary information is enough to make profile assessments reviewable without creating a provenance graph.
