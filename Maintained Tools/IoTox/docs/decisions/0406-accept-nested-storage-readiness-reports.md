# 0406 — Accept nested storage-readiness evidence reports

## Status

Accepted.

## Context

`tools/qualify-storage-readiness.py` emits a real storage-readiness report with
nested evidence objects. Those nested objects legitimately contain fields named
`status`. The native stable-evidence checker used a small field probe that
stopped at the first matching JSON field name. In practice, that meant a valid
official report could be rejected before the checker reached the top-level
`"status": "ready"` field.

This surfaced during the local precious-candidate signoff pass recorded in
`docs/evidence/2026-09-26-local-precious-candidate-signoff.md`: the storage
report was ready, but `iotox evidence collect sync` rejected it as not ready.

## Decision

Teach the native JSON field probes used by stable evidence validation to keep
scanning until they find the requested field with the requested value. This
keeps official nested reports acceptable without requiring a flattened special
receipt.

Add a human CLI regression fixture where a storage-readiness receipt has nested
`status` evidence before the top-level `status=ready` field in sorted JSON
order.

## Consequences

- `iotox evidence collect sync` accepts the current official
  `tools/qualify-storage-readiness.py --backup-custody-proof ...` output.
- The stable sync path can now use the richer storage-readiness report rather
  than a hand-flattened minimal JSON fixture.
- This remains a lightweight receipt-shape check, not a general JSON schema
  engine. The stable evidence boundary still depends on native receipt classes,
  content-free hashes, and operator custody of the proof bundle.

