# Audit — rev0092 JCS digest hardening

## Finding

The riskiest unfinished item after rev0091 was not another registry surface. It was an executable trust-boundary mismatch: the archive named RFC 8785/JCS for current-use digest surfaces, but the validator still computed profile-rule digests with Python `json.dumps(..., sort_keys=True, separators=(",", ":"), ensure_ascii=False)`.

That mismatch is dangerous because Python sort-keys is deterministic but not a portable JCS commitment. It does not prove RFC 8785 UTF-16 member ordering, I-JSON duplicate-member handling, or ECMAScript-compatible number behavior.

## Change made

rev0092 adds `tools/jcs.py` and moves profile-rule digest computation onto it. The helper implements the current TimeSync digest subset:

```text
strict duplicate-member rejection during JSON parse
lone-surrogate string rejection
recursive object-member sorting by UTF-16 code units
no whitespace
safe-integer JSON numbers only for current TimeSync-owned digest surfaces
SHA-256 over canonical UTF-8 bytes
```

The subset is intentionally narrower than full RFC 8785 number serialization. That is acceptable because the digest-binding policy now states that current TimeSync-owned digest surfaces are safe-integer/I-JSON objects. Future digest surfaces that need fractional numbers must either encode those values as strings, bind external bytes, or add a full ECMAScript/Ryu-grade number serializer with fixtures.

## Negative evidence added

```text
examples/negative/digest-binding-policy-codepoint-order-invalid.json
examples/negative/profile-catalog-unsafe-digest-number-invalid.json
examples/negative/jcs-duplicate-member-invalid.json
```

These catch the three concrete failure modes that would have been easy to miss:

```text
wrong member-order semantics
unsafe JSON number in digest-bound normative rules
duplicate member name silently normalized by an ordinary JSON parser
```

## Refactor result

The validator remains large, but one high-risk responsibility moved out of the monolith. `tools/validate_archive.py` now imports canonicalization and strict JSON parsing from `tools/jcs.py` instead of owning digest serialization directly.

## Still open

Temporal-coherence reuse beyond scope composition remains open. Validator modularization remains open. Full RFC 8785 floating-point number serialization remains intentionally out of scope until a current TimeSync-owned digest surface admits JSON floats.
