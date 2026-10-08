# FT-0063 closure — evaluator evidence-input summary

FT-0063 asked for the smallest evidence-input interface for profile evaluators without building a provenance graph.

rev0064 closes it with `evaluator_evidence_summary`.

## Decision

Expose a compact item/class/obligation summary scoped to one profile assessment.

```text
assessment_time
assessed_profile
evaluator id/version
input_items: name + presence + evidence_class
obligation_results
decision_outputs
conclusion_binding
non_provenance_guards
```

## What was rejected

```text
source roster
clock algorithm export
raw timing samples
path history
per-hop provenance graph
transport-authentication-as-traceability
```

## Why this is enough

It lets a reviewer test whether the exported `profile_conformance` and `applicability` are plausible under a resolved profile map. It also lets retained/export boundaries detect missing evidence summaries for profiles that require them, especially P3 and P5.

## New open frontier

FT-0064: cross-operator profile catalog interoperability without central profile distribution or negotiation.
