# 24 — Evidence classes and visibility

Evidence classes are deliberately coarse. They are not a source taxonomy.

| Class | Meaning | Can satisfy profile obligations by itself? |
|---|---|---:|
| `local_measurement_summary` | Local assessed observation summary, not raw samples. | yes |
| `authenticated_source_claim` | A source claim with authenticated identity/channel. | yes, profile permitting |
| `unauthenticated_source_claim` | A claim lacking required authentication. | no |
| `source_diversity_summary` | Dependency/common-mode summary without roster or path history. | yes for source-diversity posture |
| `operator_configuration` | Local configured profile, scope, or policy fact. | yes for configuration obligations |
| `profile_catalog_rule` | Normative rule from the assessed profile. | yes for rule lookup |
| `validity_horizon_summary` | Validity/current-actionability summary for one profile assessment. | yes for validity-horizon obligations |
| `local_policy_rule` | Current-policy acceptance/actionability rule. | yes for policy overlay |
| `external_evidence_reference` | Opaque external handle or salted commitment for redacted item binding. | no |
| `authorized_verifier_disclosure` | Detached challenge/disclosure receipt for an authorized external review. | no |
| `retained_prior_assessment` | Historical assessment reused as a record. | no as fresh timing evidence |
| `transport_metadata_only` | Envelope/carrier fact. | no |
| `not_observed` | Explicit absence or unknown state. | no |

The machine-readable source of truth is `evaluator/evidence-class-catalog.json`. The validator derives forbidden satisfaction classes from `may_satisfy_profile_obligation: false`; profile policies must include those classes in `classes_that_cannot_satisfy_profile_obligations`.

## Visibility lanes

```text
local_only       used internally, not exported by default
requestable      may be returned through flat request/result accounting
profile_default  visible by default for a profile because omission would mislead
retention_only   exported for retained review/audit boundaries
```

The lane is part of the evidence summary scope. Requirement is separate from visibility:

```text
default_visibility: one of the four lanes above
retention_required: boolean
retention_required_when: trigger labels
profile_default_when: trigger labels
```

`retention_required` is not a visibility lane. It is a profile evidence-policy requirement.

## Redaction modes

`summary_with_salted_commitments` means the summary may bind redacted input items to salted commitments and opaque external handles. Bare digests over hidden low-cardinality values are rejected because they can be enumerated.

## Why this is not provenance

The class names say what kind of evidence fed the evaluator. They do not identify every source, path, sample, hop, selection rule, verifier authorization workflow, salt/preimage workflow, or external chain-of-custody record. When a consuming boundary needs that material, it has exceeded the TimeSync evidence-summary layer and must use a domain-specific provenance or audit system outside TimeSync.
