# 19 — Adapter binding catalog

## Purpose

An adapter binding describes how a TimeSync semantic object is carried by an existing mechanism.

It is a boundary description, not a protocol definition.

## Adapter record

Each adapter catalog record contains:

```text
id
version
mode
carrier
payload_types
does_not_define_protocol
timestate_core_mutation
identity_binding
freshness_source
ordering_semantics
result_policy
profile_reference_policy
prohibited_behaviors
```

The key invariant is:

```text
does_not_define_protocol = true
timestate_core_mutation = forbidden
```

## Adapter modes

```text
test_fixture
in_band_claim
out_of_band_pull
out_of_band_push
detached_export
relay_boundary
```

## Carrier categories

```text
json_fixture
existing_protocol
management_api
telemetry_stream
file_export
```

These are deliberately broad categories. A deployment may map them to NTP extension data, PTP management, YANG/NETCONF, gNMI, Kafka, signed JSON export, or another carrier. TimeSync does not standardize those transports here.

## Identity binding

An adapter may expose transport or payload identity, but identity is not traceability by itself.

```text
none
transport_identity
payload_identity
operator_configured
profile_reference_binding
```

The strongest value, `profile_reference_binding`, means the adapter can carry a profile reference that includes a signed profile binding. It does not mean the adapter's own signature is such a binding.

## Freshness source

The allowed values are:

```text
semantic_payload
carrier_native_metadata_only
not_applicable
```

Only `semantic_payload` can provide TimeSync freshness. Carrier-native metadata may help detect delivery delay or stale telemetry, but it does not define the local assessed state's freshness field.

## Ordering semantics

```text
none
carrier_order
sequence_optional
external
```

Ordering metadata may be useful for stream processing, but it cannot improve a TimeState interval or profile conformance.

## Result policy

Adapters that carry discovery results must support the existing negative item statuses:

```text
unavailable
unknown
omitted
```

A returned item still needs an explicit value.

## Profile-reference policy

The adapter catalog repeats one critical rule:

```text
envelope_signature_substitutes_for_profile_binding = false
```

Envelope integrity may protect delivery. Profile-reference digest and signed binding obligations remain inside `assessed_profile`.
