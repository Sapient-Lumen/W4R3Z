# rev0007 worklog

## Intent

Keep real forward momentum by finishing a concrete risky proof instead of expanding the registry.

## Substantive work completed

1. Reproduced U-123 through `Downloads._transfer_request()` rather than directly calling `_activate_transfer()`.
2. Verified the same behavior across all external rev0003 source lanes:
   - `github-tag-3.3.10`
   - `github-branch-3.3.x`
   - `github-branch-master`
3. Found the stronger stale-timeout consequence: after a duplicate token overwrite, the first transfer's stale timeout removes the second transfer's active-map entry because `_deactivate_transfer()` deletes by `username + token` without checking object identity.
4. Re-ranked U-123 to the top working priority for the next proof/report pass.
5. Refactored the transfer lifecycle cluster so U-123/U-169/U-170 are treated as one active-transfer session-integrity changeset, while U-158/U-166 and U-269 stay separate.
6. Kept the strict document empty. U-123 is a strong holding-pen candidate, but not complete enough for strict admission.

## Files added

- `docs/U123-DUPLICATE-TOKEN-HANDLER-PROOF.md`
- `docs/TRANSFER-LIFECYCLE-CLUSTER-REV0007.md`
- `docs/AUDITED-BACKLOG-REV0007-ADDENDUM.md`
- `evidence/rev0007-u123-handler-timer-probe.jsonl`
- `evidence/rev0007-u123-source-trace-handler-timer.md`
- `evidence/rev0007-web-public-overlap-u123.md`
- `data/rev0007_ranked_audit_queue.csv/json`
- `data/rev0007_queue_delta.csv/json`
- `data/rev0007_u123_handler_timer_probe.csv/json`
- `data/rev0007_transfer_lifecycle_coherence.csv/json`
- `data/rev0007_public_overlap_u123.csv/json`
- `tools/replay_u123_handler_timer_probe.py`

## Remaining U-123 blockers

- F-connection/socket integration harness: show how FileTransferInit/progress/close behaves after the collision and stale timer.
- Harder public/private overlap sweep: the captured public search found adjacent issues but no direct duplicate-token active-map report.
- Maintainer-grade test shape: translate the probe into a concise unit/regression test that does not depend on excessive monkeypatching.
