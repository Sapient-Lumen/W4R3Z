# REV0103 audit — transport integrity refactor

## Finding

The transport-envelope temporal helper made `sent_at` safe as an artifact boundary, but transport integrity claims still lived mostly in schema shape and prose. The validator checked adapter ID, carrier/mode, message type, and payload semantics, but it did not ensure that:

```text
adapter.binding_strength = signed_payload
```

was backed by a signed or detached-signature integrity block covering the semantic payload, or that:

```text
adapter.binding_strength = authenticated_transport
```

actually authenticated the semantic payload rather than only metadata.

## Executable correction

`tools/transport_integrity.py` now owns:

```text
semantic_only cannot claim authentication/signature coverage
authenticated_transport requires integrity.protection = transport_authenticated
authenticated_transport must cover semantic_payload
signed_payload requires signed_payload or detached_signature protection
signed_payload must cover semantic_payload or semantic_payload_digest
signed_payload requires integrity.algorithm and integrity.value
profile_reference-only coverage is rejected as a profile-binding substitute
```

## New negative coverage

- `transport-signed-payload-without-signature-invalid.json`
- `transport-authenticated-without-semantic-cover-invalid.json`
- `transport-profile-reference-only-cover-invalid.json`

All three are rendered JSON fixtures and derivation-checked from existing positive transport envelope examples.

## Non-goals

rev0103 does not introduce a transport protocol, signature verifier, key registry, or profile-credential layer. It only checks that envelope integrity labels are not internally misleading.
