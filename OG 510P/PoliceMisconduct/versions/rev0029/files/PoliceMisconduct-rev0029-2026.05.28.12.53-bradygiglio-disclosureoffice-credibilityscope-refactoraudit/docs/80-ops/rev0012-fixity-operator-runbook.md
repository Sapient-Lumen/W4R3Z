# Rev0012 fixity operator runbook

1. Start with `data/source_graph/source_capture_manifest.rev0012.json`.
2. Select only P0 targets whose URL state is resolved and whose public display remains blocked.
3. Capture privately with HTTP metadata and no public payload mirroring.
4. Compute SHA-256 over the exact payload bytes.
5. Create a sidecar custody record before reading content.
6. Run a privacy scan before summaries.
7. Do not promote current status unless source-family and docket/order checks pass.
8. Add rollback edges for every summary or claim that would depend on the payload.

A failed fetch is not a dead source. It is a retrieval anomaly and should be retried manually before any absence or drift claim.

