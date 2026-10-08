# Rev0667 — chunk transfer round continuation

## Why this exists

AnonSync is a C++ peer-to-peer file synchronization product. Rev0663 made deterministic chunk request batches from verified staged-transfer inspection state, rev0664 bound accepted peer bytes to those requests, rev0665 added per-chunk response envelopes, and rev0666 added batch response envelopes for ordered multi-chunk peer replies.

The audited gap after rev0666 was continuation state. A caller could safely accept a multi-chunk batch, but then had to separately re-run transfer inspection and separately build the next request plan. That is exactly the kind of daemon/session glue that tends to drift from the evidence model: one staging tree might be written while another is inspected, post-write receipt state might not be checked before the next request is scheduled, or a caller might materialize based on stale pre-batch inspection.

## What changed

Rev0667 adds public C++ transfer-round primitives:

- `SyncChunkTransferRoundResult`
- `accept_sync_chunk_response_batch_and_plan_next(...)`

`SyncChunkTransferRoundResult` carries:

- the full `SyncChunkResponseBatchAcceptanceResult` from the accepted batch;
- the post-batch `SyncStagedTransferInspectionResult`;
- the next `SyncChunkRequestPlanResult` rebuilt from that post-batch inspection;
- `post_batch_inspection_checked` and `next_request_plan_built` flags;
- `ready_to_materialize` when the staged file now has verified receipts and full content evidence;
- `more_chunks_needed` when the continuation request still has chunks to fetch.

`accept_sync_chunk_response_batch_and_plan_next` first rejects mismatched write and inspection roots, so peer bytes cannot be written under one staging tree while continuation evidence is derived from another. It then delegates acceptance to `accept_sync_chunk_response_batch_envelope`, re-runs `inspect_sync_staged_transfer`, verifies that acceptance completion agrees with post-batch inspection, and calls `build_sync_chunk_request_plan` against the verified post-write state.

## Audit/refactor finding

The audited gap was session-layer continuation drift. Rev0666 correctly protected each batch before disk writes, but it left the continuation decision to outside code. For a sync daemon, the next action after a batch must be evidence-bound: either request the next exact missing chunks, or mark the staged file ready for receipt-gated materialization. Rev0667 moves that transition into the C++ sync-domain boundary.

This is a refactor as much as a feature: the caller no longer needs to remember that batch acceptance must be followed by receipt inspection and request-plan rebuilding. The transfer round returns the post-write state and the next deterministic action together.

## Safety properties added

- Batch continuation rejects mismatched write/inspection roots before accepting peer bytes.
- Batch acceptance remains delegated to the rev0666 request/batch envelope verifier.
- Post-batch inspection is mandatory before any continuation or materialization-ready signal is returned.
- The next request plan is rebuilt from verified post-batch receipt state, not from stale pre-batch inspection.
- Partial rounds return exact next `sync-chunk-request:v1:` evidence.
- Final rounds return `ready_to_materialize` only when the post-batch inspection proves the staged file complete.

## Validation evidence

The sync-domain selftest now covers:

- a four-chunk transfer round whose first bounded request accepts two chunks and returns a continuation request for the remaining two chunks;
- rejection of mismatched write and inspection roots before accepting bytes;
- a second bounded request that completes the staged file and returns `ready_to_materialize` with no next chunk request;
- preservation of the earlier rev0666 duplicate/forged batch rejection and byte preflight checks.

Recorded validation for this package:

```bash
cmake --build build --target anonsync_core -j2
ctest --test-dir build --output-on-failure
./build/anonsync_core --selftest-sync-domain-model
python3 tools/validate_rev0667_chunk_transfer_round.py
```

A narrow ASAN/UBSAN sync-domain selftest was also recorded for this revision.

## Remaining ceiling

Rev0667 still does not run a real peer protocol, persist transfer scheduler state, clean up orphan `.part` or `.chunks` sidecars, garbage-collect receipt sidecars after materialization, authenticate peer sessions, exchange manifests over a transport, or implement peer discovery. The next code-bearing step should either add a deterministic fake peer-session harness that loops manifest diff, local apply planning, staged inspection, request planning, batch acceptance/continuation, and receipt-gated materialization end to end; or add persisted staged-transfer state and cleanup so the transfer-round evidence survives daemon restart.
