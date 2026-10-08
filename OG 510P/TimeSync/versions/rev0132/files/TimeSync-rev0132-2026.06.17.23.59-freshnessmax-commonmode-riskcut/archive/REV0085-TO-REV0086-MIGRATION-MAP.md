# rev0085 to rev0086 migration map

## What changed

rev0086 adds a portable digest binding and semantic-version negotiation layer around discovery-returned and digest-bound objects.

## Required migration

Implementations that produce current-use digests for TimeSync-owned semantic objects should publish or retain a binding equivalent to:

```text
binding_mode = canonical_json_rfc8785
canonicalization = json_canonicalization_scheme_rfc8785
digest_algorithm = sha256
```

Implementations that return external signed statements or receipts should use `external_byte_envelope` or `external_receipt_bytes` and must verify bytes before parsing payload content.

Discovery responders should add `semantic_version`, `schema_uri`, `version_negotiation`, and `digest_binding` to returned digest-bound items when available.  Older responders remain interpretable as legacy, but current-use consumers should fail closed when the binding is absent and the profile requires portable digest semantics.

## Non-migration

TimeState fields are unchanged.  Profile obligations are unchanged except for profile digest regeneration caused by adding a non-satisfying evidence class.  Aggregate lifecycle semantics from rev0085 are unchanged; rev0086 defines how the decision table and related returned objects are byte-bound and version-negotiated.
