# 18 — Minimal transport envelope

## Purpose

The transport envelope is a carriage wrapper for TimeSync semantic objects. It exists so examples, adapters, management interfaces, telemetry streams, and detached exports can identify what they carry without turning TimeSync into a full protocol.

The envelope is below the semantic layer:

```text
existing carrier / file / management API / telemetry stream
  TimeSync transport envelope
    semantic payload
      wire_claim | local_assessed_state | discovery_request | discovery_result | capability_advertisement | retained_assessment_export
```

The envelope is not part of TimeState.

## Minimal envelope fields

```text
envelope_version
message_type
adapter
semantic_payload
```

Optional fields:

```text
exchange_id
correlation_id
sequence
sent_at
producer
integrity
```

## Message types

```text
wire_claim
local_assessed_state
discovery_request
discovery_result
capability_advertisement
retained_assessment_export
```

Each `message_type` selects the schema and semantic checks for `semantic_payload`.

## Rule: payload meaning is unchanged

Wrapping a payload does not change its meaning.

A `wire_claim` in an envelope is still a source claim, not local assessed state. A `local_assessed_state` in an envelope is still local assessed state, not a source claim. A `retained_assessment_export` is still an export of a retained assessed state, not a new assessment event.

## Rule: envelope metadata is not TimeState

These are not TimeState fields:

```text
sent_at
sequence
exchange_id
correlation_id
producer
adapter.carrier
adapter.binding_strength
integrity.protection
```

They may help carry, correlate, or protect an exchange. They do not establish interval, timescale, freshness, regime, source posture, applicability, or profile conformance.

## Rule: no native transport bundle layer

The envelope can carry one semantic payload. It can correlate messages using `exchange_id` and `correlation_id`, but it does not define request bundles, sessions, negotiations, retransmission rules, ordering guarantees, or source-selection behavior.

A carrier may provide those things. TimeSync does not.

## Rule: adapter identity is descriptive and constrained

The `adapter.id` names a known adapter pattern from `transport/adapter-catalog.json`. The adapter says what kind of carrier and boundary is being used. It does not define profile conformance.

## Allowed adapter promises

An adapter may promise:

```text
which message types it can carry
what carrier category it uses
whether transport authentication or payload signing exists
whether ordering is absent, carrier-provided, or sequence-hinted
how negative discovery results are represented
```

An adapter must not promise:

```text
that the clock is correct
that the profile is satisfied
that fallback is valid
that envelope sent_at is freshness
that transport authentication is traceability
that a payload signature is a signed profile binding
```

## Validation effect

The validator treats transport envelopes as nested semantic containers. It validates both the envelope shape and the semantic payload selected by `message_type`.
