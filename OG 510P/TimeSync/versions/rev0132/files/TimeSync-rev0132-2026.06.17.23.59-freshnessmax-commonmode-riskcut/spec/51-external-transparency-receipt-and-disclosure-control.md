# 51 — External transparency receipt and disclosure-control references

rev0086 adds two optional aggregate-only references: an external transparency receipt reference and an explicit statistical disclosure-control reference.

## External transparency receipt reference

Placement:

```text
external_transparency_receipt_reference
```

The field can bind an aggregate statement to an outside receipt, checkpoint, or log entry without making TimeSync operate or validate the outside system.

The reference carries:

```text
receipt_type
statement_digest
checkpoint_digest
receipt_digest
receipt_validation_status
boundary
```

When `receipt_validation_status` is `validated`, the record must carry a checkpoint digest and a receipt digest that binds `external_transparency_receipt`.

The field may identify receipt class, digest commitments, and validation status. It must not export log operator identity, monitor identity, raw log entries, proof material, gossip transcripts, external repository topology, or provenance graphs.

## Disclosure-control reference

Placement:

```text
aggregate_summary.aggregate_privacy_controls.statistical_disclosure_control_reference
```

The field makes privacy claims more explicit without turning TimeSync into a privacy-accounting system.

It carries:

```text
policy_digest
mechanism_class
minimum_group_size_class
noise_policy_class
privacy_budget_exported
raw_population_size_exported
```

The policy digest binds the external aggregate privacy policy. Mechanism class may report thresholding, bucketization, noise, redaction-only, mixed, or unknown/redacted posture.

## Boundary

TimeSync still does not define a transparency log, monitor, witness network, differential-privacy accountant, privacy-budget ledger, publication repository, or proof-verification protocol.

These references are digest-bound summary hooks. They constrain aggregate replay-review posture only and cannot update TimeState, profile conformance, actionability, individual replay visibility, or TimeSync provenance.
