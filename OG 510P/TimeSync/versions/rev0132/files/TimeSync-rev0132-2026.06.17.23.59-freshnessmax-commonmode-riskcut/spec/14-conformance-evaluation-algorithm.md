# 14 — Conformance evaluation algorithm

This is the deterministic evaluator outline. It is intentionally simple; profiles may add deeper control-surface checks.

## Inputs

```text
local assessed state
candidate profile map
current policy, when retained or re-used
boundary type: local | export | retained | detached | cross-operator
requested items, when relevant
```

## Output

```text
profile_assessment:
  assessed_profile
  assessment_time
  profile_conformance: satisfied | fallback | unsatisfied
  applicability
  policy_acceptance?
  evaluation_summary?
```

## Algorithm

### 1. Validate the core TimeState

Check that all six core fields exist and that interval order is valid:

```text
earliest <= latest
```

### 2. Resolve the profile map

Find the profile by `authority`, `id`, and `version` or `revision` where possible.

If the map cannot be resolved:

```text
profile_conformance may be recorded historically
but exported actionability is unknown or rejected unless a sealed context supplies the missing identity
```

### 3. Check required/default items

For each item in the profile map's `required_items` and `profile_default_items`, check that the item is present in the correct surface.

Examples:

```text
traceability_posture -> extension_hooks.traceability_posture
sync_dimension       -> extension_hooks.sync_dimension
timescale_realization -> extension_hooks.timescale_realization
clock_continuity_posture -> extension_hooks.clock_continuity_posture
assessment_time      -> profile_assessment.assessment_time
```

Missing required/default items block `satisfied` unless the profile defines an accepted fallback.


### 3a. Check realization and continuity consistency

When present, compact realization/continuity hooks must not contradict the core or each other:

```text
timestate.timescale=UTC      -> timescale_realization.scale must be UTC or unknown
traceability utc_named_realization -> timescale_realization must name a realization
leap_handling=smeared        -> smear_policy cannot be none or not_applicable
```

These checks do not validate the external time service; they only prevent internally contradictory semantic claims.

### 4. Evaluate profile-local applicability

The exported applicability must be a label in the profile map.

If the state asserts a label outside the map, the label is local-only or invalid for that profile boundary.

### 5. Select conformance

```text
all obligations met                         -> satisfied
obligations not met but fallback applies    -> fallback
otherwise                                   -> unsatisfied
```

When fallback applies, select the fallback target label from the profile map and ensure it is not stronger than the source label by profile-local rank.

### 6. Apply current-policy overlay

For retained or reused assessments, do not rewrite historical conformance. Add or update:

```text
policy_acceptance.status
policy_acceptance.checked_at
policy_acceptance.actionability
policy_acceptance.reason or policy_reference
```

A rejected or unknown current-policy result must not be exported as currently actionable.

### 7. Export with sufficient reference strength

Use the profile's `reference_policy` and the boundary tier rule from `spec/10-profile-reference-strength.md`.

For retained, detached, audit, safety, or compliance-sensitive exports, Tier 3 is the expected default:

```text
authority + id + version/revision + digest
```

## What the rev0067 validator checks

`tools/validate_archive.py` checks the subset of this algorithm that is mechanical from the archive fixtures:

```text
JSON/YAML syntax
JSON Schema shape
profile catalog consistency
interval order
profile-local applicability label membership
fallback target validity
required/default item presence
policy acceptance/actionability consistency
manifest hashes
realization/continuity/source-diversity hook consistency
returned discovery hook value shape
expected positive and negative semantic fixtures
```
