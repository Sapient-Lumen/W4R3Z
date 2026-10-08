# 26 — Evidence non-provenance guardrails

The evidence summary is small because it deliberately refuses to answer several attractive but expansive questions.

## Forbidden expansion

The TimeSync evidence summary does not export:

```text
source roster
path history
clock algorithm
raw observations
complete provenance graph
transport-authenticated traceability assertion
external provenance interpretation
ordinary retained-summary salt/preimage disclosure
```

The schema carries explicit `non_provenance_guards` booleans. They are required to be false so an exported summary cannot silently become a broader audit artifact.

## Allowed redaction

A summary may be redacted to item class, presence, and obligation result. Optional item digests can bind a redacted summary item, but bare unsalted digests must not be used for hidden low-cardinality values.

rev0069 adds `external_evidence_reference` for opaque handles and salted commitments. This binds a redacted evidence item to external retained material without making TimeSync parse or validate that material's provenance.

rev0070 adds a detached authorized verifier challenge result. It may record a match result and opaque receipt for external salt/preimage review, but the salt/preimage material remains outside ordinary TimeSync exchange and the result does not reopen the assessment.

## Boundary to external systems

When a consuming domain needs chain-of-custody evidence, per-source attestations, calibrated instrument logs, legal retention artifacts, selective-disclosure proof systems, or cyber-forensic timelines, that material belongs outside TimeSync. TimeSync may bind to an opaque external reference or salted commitment, but it does not become that system.
