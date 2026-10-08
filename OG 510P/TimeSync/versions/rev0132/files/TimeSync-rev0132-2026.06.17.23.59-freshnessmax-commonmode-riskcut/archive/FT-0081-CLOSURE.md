# FT-0081 closure — Aggregate publication correction and lineage

FT-0081 asked whether aggregate replay-transparency publications should define correction, withdrawal, supersession, and longitudinal reconciliation semantics.

rev0082 answers yes, but only as bounded aggregate publication-lineage metadata.

## Closed by

- `schema/replay-transparency-audit.schema.json`
- `spec/45-aggregate-publication-correction-and-lineage.md`
- `examples/evaluator/aggregate-verifier-audit-summary-p3-corrected.json`
- `examples/evaluator/aggregate-verifier-audit-summary-p3-reconciled.json`
- `tools/validate_archive.py`

## Boundary decision

Aggregate correction lineage can say how a later aggregate relates to a prior aggregate publication. It cannot rewrite the prior publication, expose suppressed deltas, identify verifiers, reveal individual challenge-result identifiers, update profile assessments, update current actionability, or become TimeSync provenance.

## Result

FT-0081 is closed in rev0082.
