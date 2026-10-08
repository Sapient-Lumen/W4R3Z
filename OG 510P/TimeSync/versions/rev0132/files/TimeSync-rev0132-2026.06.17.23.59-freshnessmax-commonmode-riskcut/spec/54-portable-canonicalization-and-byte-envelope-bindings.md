# TimeSync rev0086 — Portable canonicalization and byte-envelope bindings

rev0086 closes FT-0085 by making digest-bound surfaces portable across implementations.  Earlier revisions used a Python `json.dumps(..., sort_keys=True, separators=(",", ":"), ensure_ascii=False)` convention in the validator.  That convention remains acceptable only as a historical implementation detail; it is not the portable current binding profile.

## Normative digest rule

TimeSync-owned semantic objects that are digested for current interpretation use:

```text
canonicalization: json_canonicalization_scheme_rfc8785
digest_algorithm: sha256
profile_id: timesync-jcs-sha256-v1
```

The digest binds the canonical bytes of the object after omitting the digest field that would otherwise self-reference the object. The archive keeps this rule intentionally narrow: it identifies the bytes being committed to, not the legal authority, operator identity, credential status, or truth of the underlying time claim.

rev0092 makes the current TimeSync-owned digest subset executable: duplicate JSON member names are rejected before schema validation, object member names sort by UTF-16 code units, lone surrogates fail, and digest-bound TimeSync objects use only I-JSON safe integers. Fractional or higher-precision values must be encoded as strings, or the object must be bound as external bytes.

## Surfaces that use canonical JSON

The following surfaces are current-use canonical JSON surfaces:

```text
normative_profile_rules
aggregate_lifecycle_decision_table
profile_compatibility_statement
transparency_trust_policy_reference
discovery_returned_object
```

A current-use digest on these surfaces MUST NOT use the legacy Python sort-keys serialization profile. For TimeSync-owned semantic objects, `tools/jcs.py` is the executable canonicalization boundary.

## Surfaces that bind pre-existing external bytes

External signed statements, receipts, and retained operator records may bind external bytes instead of TimeSync-reserialized JSON.  For those surfaces, TimeSync records the digest, payload type, envelope kind, and verification boundary.  It does not require consumers to parse the payload before verifying the signed bytes.

The byte-envelope binding profile requires:

```text
payload_type_authenticated = true
verified_before_payload_parse = true
canonicalization_dependency = not_required_for_signature_validation
raw_payload_bytes_exported = false by default
```

This mirrors the architectural lesson from DSSE-style and COSE/SCITT-style envelopes: the signature or receipt binds bytes and payload type; TimeSync must not silently reinterpret the payload by reserializing JSON and hashing something else.

## Boundary

The digest binding policy:

```text
does not update profile assessment
does not update TimeState actionability
does not create a credential system
does not operate a transparency log
does not export raw external bytes by default
does identify the bytes that a digest binds
```

## Refactor note

rev0086 added `check_digest_binding_metadata(...)` and `check_digest_binding_policy(...)` in the validator so canonicalization and envelope checks no longer lived as scattered, one-off result checks. rev0092 moves low-level canonical bytes and strict JSON parsing into `tools/jcs.py`, reducing validator sprawl at the riskiest digest boundary.
