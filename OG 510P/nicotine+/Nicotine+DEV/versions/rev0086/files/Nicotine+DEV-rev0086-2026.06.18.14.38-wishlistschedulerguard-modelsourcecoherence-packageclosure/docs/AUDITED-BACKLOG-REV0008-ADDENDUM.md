# Audited backlog rev0008 addendum

## U-123 priority change

U-123 is now the first strict/high-quality report-candidate in the DEV cube. The title was sharpened from a generic active-state overwrite to the concrete consequence proven in rev0008:

```text
Duplicate peer-supplied download transfer tokens can orphan a later F-connection transfer session after a stale first timeout
```

The finding remains bounded to transfer-session availability/state integrity. It should not be described as RCE or file disclosure.

## Queue changes

See `data/rev0008_ranked_audit_queue.csv` for all rows. The practical top queue after rev0008 is:

```text
1. U-123 — package/report/test now
2. U-169 — supporting context for same transfer-session boundary
3. U-269 — next transfer-lifecycle proof candidate
4. U-270 — next parser/lifetime proof candidate
5. PB-01/U-168/U-176 — separate peer-state-machine harness later
```

## Duplicate/coherence notes

No new numeric IDs were created. rev0008 intentionally avoids multiplying rows. The transfer lifecycle family is folded into a smaller set of report groups so suggested fixes do not conflict.
