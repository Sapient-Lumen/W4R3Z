# 23 — Evaluator evidence-input interface

rev0064 added a small review surface for profile evaluators. rev0065 tightened that surface for detached and retained review. rev0066 extended the recognized input-item surface to realization and continuity hooks. rev0068 extends it again to source-diversity posture without changing the evidence-summary shape.

The interface is an **evaluator evidence-input summary**. It records what kind of inputs a local evaluator considered when producing one profile assessment. It does not export the inputs themselves.

```text
profile assessment
  assessment_id
  assessed_profile
  assessment_time
  profile_conformance
  applicability
  optional evaluator_evidence_summary
```

## Purpose

A reviewer needs to ask why a profile assessment said `satisfied`, `fallback`, or `unsatisfied`. The answer should be reviewable without exporting:

```text
full source roster
clock-selection algorithm
raw timing samples
network path history
operator topology
provenance graph
```

The summary therefore records item presence, evidence class, obligation result, evaluator version, and the exact assessment conclusion it was bound to.

## Required scoping

Every evidence summary is scoped by:

```text
summary_id
assessment_time
assessed_profile
evaluator id/version
conclusion_binding.assessment_id
one profile assessment conclusion
```

A summary is not a global certificate and not an independent assertion of conformance. It explains one local/exported profile assessment.

`assessment_index_hint` remains only a convenience hint. The stable binding is `assessment_id`.

## Minimal fields

```text
summary_version
summary_id
assessment_time
assessed_profile
evaluator
scope
input_items
obligation_results
decision_outputs
conclusion_binding
non_provenance_guards
```

`input_items` are named semantic inputs such as `timestate.interval`, `extension_hooks.traceability_posture`, `extension_hooks.timescale_realization`, `extension_hooks.clock_continuity_posture`, `extension_hooks.source_diversity_posture`, or `policy_acceptance`. Each input has a presence value and an evidence class. The summary may say that an input was present, absent, unknown, or not applicable, but it does not carry the raw source material.

## Profile minimum summary items

Each profile may declare `evidence_policy.minimum_summary_items`. A resolved evidence summary must account for those items either as named `input_items` or, for assessment-conclusion facts, in the top-level summary/conclusion fields.

The following names are recognized as assessment-conclusion facts rather than raw inputs:

```text
assessment.assessment_id
assessment.assessment_time
assessment.assessed_profile
assessment.profile_conformance
assessment.applicability
```

All other minimum items are expected as named evidence-summary input items.

## Non-upgrade rule

Evidence classes whose catalog entry says `may_satisfy_profile_obligation: false` may appear only as context, failure explanation, absence, or ignored material. They cannot satisfy a `met` profile obligation.

```text
transport_metadata_only + met profile obligation = invalid
unauthenticated_source_claim + met profile obligation = invalid
retained_prior_assessment + fresh profile obligation = invalid
not_observed + met profile obligation = invalid
```

## Export behavior

The summary is normally requestable. Some profiles require it for retained or detached review. Visibility and requirement are separate:

```text
scope.visibility: local_only | requestable | profile_default | retention_only
profile evidence_policy.retention_required: true | false
```

P3 and P5 set `retention_required: true` because their strongest uses are audit, compliance, control, or safety adjacent.


## rev0068 validity horizon input

`validity_horizon_summary` may satisfy a `validity_horizon` obligation, but it must not treat export time as renewed assessment freshness.
