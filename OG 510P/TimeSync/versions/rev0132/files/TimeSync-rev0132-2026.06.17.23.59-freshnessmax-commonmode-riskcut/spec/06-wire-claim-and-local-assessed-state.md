# 06 — Wire claim and local assessed state

## Reason for the split

The six TimeState fields mix upstream claim, local inference, and downstream consequence. A cleaner architecture separates:

```text
WireClaim              what a source or relay says on the wire
LocalAssessedState     what the receiver locally judges and exports
```

## Minimum wire claim

```text
WireClaim:
  interval_claim
  timescale_claim
  identity_or_auth_proof
```

Optional wire-adjacent claims:

```text
traceability_posture_claim
sync_dimension_claim
```

The minimum wire claim does not include profile conformance, local regime, downstream applicability, profile lifecycle, or current-policy acceptance.

## Local assessed state

```text
LocalAssessedState:
  timestate:
    interval
    timescale
    freshness
    regime
    source_posture
    applicability

  optional extension_hooks
  optional boundary_context
  optional profile_assessments
```

Local assessed state may incorporate multiple wire claims, local policy, source posture, uncertainty calculations, holdover behavior, profile obligations, and boundary context.

## Non-confusion rule

A source may claim time. A receiver assesses time.

Exported profile conformance is therefore a local/export metadata result unless a particular profile explicitly defines a signed external assessment mechanism.
