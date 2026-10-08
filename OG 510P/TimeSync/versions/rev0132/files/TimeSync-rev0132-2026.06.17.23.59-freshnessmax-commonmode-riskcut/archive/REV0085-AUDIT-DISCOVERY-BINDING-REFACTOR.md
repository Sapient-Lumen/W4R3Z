# rev0086 audit — discovery binding and negotiation refactor

## Finding

The rev0085 discovery path validated known returned objects, but version handling and digest binding were implicit.  A consumer could receive a syntactically valid object that was semantically newer than advertised support, or a digest that was current-use only by convention.

## Refactor

The validator now separates three concerns:

```text
check_result_version_negotiation(...)
check_digest_binding_metadata(...)
check_digest_binding_policy(...)
```

This keeps object-specific validation focused on the returned value and moves cross-cutting binding/version safety into reusable helpers.

## Added audit coverage

- exact supported semantic version passes
- RFC 8785 canonical JSON binding passes for current TimeSync-owned surfaces
- byte-envelope binding passes only when payload type is authenticated and bytes are verified before parsing
- legacy Python sort-keys binding fails for current use
- unknown newer semantic result fails when accepted as current
- version negotiation metadata cannot update profile assessment or actionability

## Boundary preserved

The refactor does not make discovery a credential system, registry, transparency log, or provenance graph.  It only makes returned objects safer to interpret.
