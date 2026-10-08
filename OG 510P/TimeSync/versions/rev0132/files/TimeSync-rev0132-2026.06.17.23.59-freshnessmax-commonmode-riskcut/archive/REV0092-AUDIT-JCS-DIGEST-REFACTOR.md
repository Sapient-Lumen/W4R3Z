# rev0092 audit/refactor — JCS digest boundary

## Problem

The archive had a doctrine/implementation split:

```text
schema and specs: current digests are RFC 8785/JCS-bound
validator: current profile-rule digests use Python sort-keys JSON
```

That split was not immediately visible because all existing profile objects are simple enough that Python and the intended JCS subset happened to agree.

## Refactor

`tools/jcs.py` now owns canonicalization and strict JSON parsing. `tools/validate_archive.py` consumes it through:

```text
load_json_ijson(...)
sha256_hexdigest(...)
jcs_self_test(...)
```

This keeps the validator from accumulating another set of low-level serialization rules.

## Semantic tightening

The digest-binding policy now requires:

```text
object_member_order = lexicographic_utf16_code_unit_order
ijson_constraints_enforced = true
duplicate_member_names_rejected = true
unsafe_numbers_rejected_for_timesync_digest_surfaces = true
legacy_python_sort_keys_permitted_for_current_binding = false
```

## Why this is substance, not bureaucracy

The revision adds one small helper module, three attack fixtures, and executable checks. It does not add a new registry, profile, credential layer, or discovery negotiation surface.

## Next refactor target

The next best validator split is temporal: move aggregate lifecycle/replay/policy timestamp-window checks into reusable helpers beside `tools/temporal_coherence.py` instead of continuing to expand `tools/validate_archive.py`.
