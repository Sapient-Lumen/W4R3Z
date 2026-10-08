# rev0098 to rev0099 migration map

## Summary

rev0099 is compatible with rev0098 consumers that ignore the new negative fixtures and helper modules. It tightens validation for profile compatibility statements by making artifact-time ordering executable.

## New helper

```text
tools/profile_compatibility_temporal.py
```

## Validator change

`tools/validate_archive.py` now delegates profile compatibility issue/signature/expiry/drift timing to `tools/profile_compatibility_temporal.py`.

The previous inline `issued_at < expires_at` check is now part of that helper.

## New rejection cases

A rev0098 profile compatibility statement can become invalid in rev0099 if:

```text
issued_at > binding.signed_at
binding.signed_at > expires_at
compatibility_drift.evaluated_at > binding.signed_at
compatibility_drift.evaluated_at > expires_at
```

## Fixture changes

New semantic vectors:

```text
TV-N266
TV-N267
```

New derivation entries:

```text
DF-0099-001
DF-0099-002
DF-0099-003
```

## Boundary

No TimeState core field changes. No profile obligation changes. No new authority registry. No transport semantics change.
