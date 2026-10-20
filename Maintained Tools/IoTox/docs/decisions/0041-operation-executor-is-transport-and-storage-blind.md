# ADR 0041 — Operation executors are transport- and storage-blind

- Status: accepted
- Revision: rev0011
- Date: 2026-08-14
- Depends on ADR 0038 and ADR 0036

## Context

The first `device.describe` implementation was embedded in the large process coordinator. That
made a harmless read operation depend conceptually on transport, durable storage, session state,
and projection details even though its result only needs validated command input plus stable device
context.

Future operations will need different effect policies. Mixing their business logic with toxcore
callbacks or journal mutation would make replay, testing, cancellation, and physical-effect review
harder rather than safer.

## Decision

IoTox operation execution lives behind a C++ command-engine boundary:

```text
validated CommandRequest
+ immutable CommandExecutionContext
                  |
                  v
transport/storage-blind executor
                  |
                  v
typed CommandResultPayload or Status
```

The caller remains responsible for protocol parsing, authority admission, durable lifecycle
transitions, exact request/result encoding, retry, delivery, and projections. The executor must not
call toxcore, mutate the authority ledger, write the command store, or decide transport retry.

The rev0011 context supplies only facts needed by `device.describe`: product revision/version,
negotiated protocol, stable device principal, supported feature mask, and offered operation mask.
An incomplete identity context fails closed.

## Consequences

The same operation implementation can be exercised without a Tox instance, filesystem, daemon,
mock shared library, or clock. The process coordinator is smaller in responsibility even though it
still owns the lifecycle state machine.

This boundary does not imply every future physical operation can be a pure function. Mutable and
physical operations will need explicit effect adapters, effect identity, crash recovery,
idempotency, cancellation, compensation, and hardware-specific policy. Those adapters must remain
separate from transport and durable protocol mechanics, and no operation may be registered before
its restart policy is declared.
