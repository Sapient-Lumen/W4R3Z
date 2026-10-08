# 32 — Redacted external evidence references and salted commitments

rev0069 closes FT-0068 by adding a narrow binding surface for evidence values that are too sensitive or too low-cardinality to export directly.

## Placement

The surface appears only on evaluator evidence-summary input items:

```text
evaluator_evidence_summary.input_items[*].external_evidence_reference
```

It is not part of the six-field TimeState core. It is not a profile assessment conclusion. It is not a source roster, path history, raw observation log, clock algorithm export, or provenance graph.

## Allowed use

An external reference may:

```text
bind a redacted input item to an opaque retained record
carry a salted commitment for a hidden value or hidden group
point an authorized reviewer toward an out-of-band challenge process
explain that a value was reviewed locally but redacted in the exported summary
```

An external reference must not:

```text
satisfy a profile obligation by itself
upgrade unauthenticated evidence
turn export time into freshness
turn a retained record into current actionability
cause TimeSync to interpret external chain-of-custody or provenance
```

## Salted commitment rule

A bare digest of a redacted low-cardinality value is not enough. Values such as `traceable`, `unknown`, `smeared`, `single_source`, or `mitigated_by_diversity` can be enumerated. Therefore a redacted item using a `redacted_input_group` digest must also carry a salted commitment or omit the digest entirely.

The commitment metadata records:

```text
scheme
algorithm
commitment value
what the commitment binds
salt disclosure posture
salt length
low_cardinality_protection: true
```

The salt itself is normally retained separately or disclosed only to an authorized verifier. TimeSync does not define the verifier workflow.

## External provenance boundary

`external_provenance_not_interpreted: true` is required. A consuming domain may use an audit system, transparency log, calibration record, or selective-disclosure proof system outside TimeSync, but the TimeSync evaluator summary only binds to that material. It does not parse or validate that external system's provenance semantics.

## Evidence class rule

`external_evidence_reference` is an evidence class so pointer-only items can be represented. It has `may_satisfy_profile_obligation: false`. A pointer-only external reference cannot satisfy a met profile obligation. A separate local measurement, authenticated source claim, profile rule, local policy rule, source-diversity summary, or validity-horizon summary must be the actual obligation evidence.

## rev0070 challenge boundary

rev0070 keeps salt and preimage disclosure outside ordinary TimeSync summaries. The new authorized-verifier challenge result can bind a challenge to a redacted commitment and carry an opaque receipt/digest showing that external review occurred, but it must not carry the salt or preimage material in ordinary TimeSync exchange and must not reopen the profile assessment.
