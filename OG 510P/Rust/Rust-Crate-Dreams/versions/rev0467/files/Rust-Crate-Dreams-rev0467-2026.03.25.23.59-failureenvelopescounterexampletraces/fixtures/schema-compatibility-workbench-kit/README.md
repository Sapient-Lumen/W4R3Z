# schema-compatibility-workbench-kit fixtures

These fixtures keep **P-0124** honest by separating four truths that schema-review tooling often blurs together:

1. **comparison basis**
2. **compatibility profile**
3. **finding strength**
4. **policy decision**

## Schemas

- `comparison-basis.receipt.schema.json`
- `compatibility-profile.receipt.schema.json`
- `finding-strength.report.schema.json`
- `policy-decision.report.schema.json`

## Scenario families

### `latest_only_registry_check_must_not_masquerade_as_transitive_history_guarantee`

Shows that a successful latest-only registry check is not the same thing as a transitive all-history compatibility guarantee.

### `oasdiff_warn_level_change_must_not_masquerade_as_definite_breaking_proof`

Shows that a warning-level OpenAPI finding should stay visibly weaker than a mechanically definite break.

### `validation_success_must_not_masquerade_as_compatibility_verdict`

Shows that JSON Schema validation success on current instances is not the same thing as a compatibility proof about schema evolution.

### `buf_wire_profile_must_not_masquerade_as_generated_source_compatibility`

Shows that a Protobuf result under a wire-focused category should not be over-read as generated-source compatibility under stricter profiles.
