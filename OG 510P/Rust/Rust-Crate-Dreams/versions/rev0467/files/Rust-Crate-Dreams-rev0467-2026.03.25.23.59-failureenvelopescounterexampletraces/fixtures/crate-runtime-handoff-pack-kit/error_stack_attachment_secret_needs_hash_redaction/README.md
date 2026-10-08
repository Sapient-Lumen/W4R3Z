# Scenario — `error-stack` attachment is exact but must be hashed for support

This scenario exists to force **P-0513** to keep separate:

- exact capture of a runtime field,
- whether the field is safe to share,
- whether the shared bundle preserves useful comparison value,
- and whether the receiver-facing summary is still honest after redaction.

## Why it matters

A crate may attach rich supporting context to an error, but some of that context can contain tokens, IDs, file paths, hostnames, or user-derived values that should not be copied verbatim into a support bundle.
A runtime handoff pack needs to preserve the fact that the data was exact while still downgrading the share class from raw export to hashed or omitted export.

## Expected artifact pressure

- `capture-exactness.policy.json` should allow a field to remain `exact_capture_with_redaction` rather than pretending redaction erased the evidentiary value.
- `share-safety.receipt.json` should record that the field came from an observed attachment and was transformed with `hash` or `omit`.
- `handoff-fidelity.report.json` should make it possible for a bundle to remain high fidelity even when raw support sharing is intentionally restricted.
