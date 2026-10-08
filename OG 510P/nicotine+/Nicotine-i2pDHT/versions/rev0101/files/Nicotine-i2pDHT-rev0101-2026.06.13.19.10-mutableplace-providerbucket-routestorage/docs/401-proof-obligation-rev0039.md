# Proof obligation rev0039

The local proof lane must show:

- `servicehealth` rejects active withdrawal, replay, metadata overrun, family monoculture, refusal loops, and scope drift.
- `servicedrain` accepts only closed, withdrawn, receipt-backed, hard-negative-preserving drains.
- `continuityjournal` preserves hard negatives and rejects rollback, fork, previous-link mismatch, duplicate replay, gap/crash-tail, and scope drift.
- `serviceopsfold` exposes the current revision through code, tests, docs, public pointers, foldmap, foldregistry, surfaceledger, and rev0038 predecessor checks.
