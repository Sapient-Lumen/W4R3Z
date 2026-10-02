# ADR 0020: Tox profile and text are a presentation lane, not authority

**Status:** accepted and implemented in rev0006

## Context

A ratox successor is incomplete without nicknames, status messages, presence, one-to-one
text, action messages, typing state, and receipts. Those facilities are already native to
Tox and are useful to operators. They are not, however, a safe device-command protocol.
A Tox read receipt reports transport reception of a text message; it does not prove that an
IoT operation was authorized, durably accepted, executed once, or completed.

## Decision

IoTox will expose the current c-toxcore profile and text APIs as a first-class human lane:

```text
self name / status message / presence
peer name / status message / presence / typing
normal text / action text / transport read receipt
```

The lane is byte-preserving within toxcore's published bounds. It remains explicitly
separate from IoTox framed lossless packets, the future authorization ledger, and durable
command lifecycle.

## Consequences

The one binary can already act as a useful Tox/ratox-style client. Scripts may use text for
conversation, notices, experiments, and operator ergonomics. Product code must never infer
ownership or actuator authority from a nickname, status, message body, friendship, typing
state, or Tox receipt. Device commands continue to require structured IoTox frames and later
application-level authorization, expiry, idempotency, and execution results.
