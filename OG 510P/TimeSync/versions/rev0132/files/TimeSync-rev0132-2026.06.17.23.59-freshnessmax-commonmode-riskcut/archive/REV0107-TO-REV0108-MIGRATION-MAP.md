# rev0107 to rev0108 migration map

rev0107 extracted discovery current-use version/digest binding checks. rev0108 extracts transport capability advertisement semantics and closes a capability overclaim path.

## Compatibility

No TimeState fields changed. No schema was expanded. Existing valid capability advertisements that describe catalog-known adapters, catalog-known profiles, and TimeSync request items remain valid.

## New invalid cases

The following now fail semantic validation:

```text
capability supported_profiles entry not found in profiles/profile-catalog.json
capability requestable_items entry outside TimeSync assessment/request vocabulary
capability requestable_items entry not supported by any advertised profile obligation/default/requestable surface
capability supported_profiles advertised for an adapter whose profile_reference_policy.may_carry_profile_reference is false
```

## Files added

```text
tools/transport_capability_semantics.py
examples/negative/transport-capability-unknown-profile-invalid.json
examples/negative/transport-capability-unknown-request-item-invalid.json
examples/negative/transport-capability-profile-ref-forbidden-adapter-invalid.json
AUDIT-2026.06.13-rev0108.md
archive/REV0108-AUDIT-TRANSPORT-CAPABILITY-REFACTOR.md
```

## Test additions

```text
TV-N292
TV-N293
TV-N294
DF-0108-001
DF-0108-002
DF-0108-003
```

The semantic vector suite grows from 310 to 313 vectors.
