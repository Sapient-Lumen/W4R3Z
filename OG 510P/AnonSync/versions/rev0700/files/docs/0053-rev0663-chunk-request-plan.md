# Rev0663 — deterministic chunk request planning

## Why this exists

AnonSync is a C++ peer-to-peer file synchronization product. Rev0660 made remote chunks receiptable, rev0661 let final materialization require those receipts, and rev0662 let a restarted daemon inspect staged bytes and receipts to recover exact `missing_chunks`.

The next missing seam was peer-request planning. A scheduler should not have to reinterpret receipt files or trust caller-edited inspection state before asking a peer for data. It needs a small C++ boundary that consumes verified staged-transfer inspection evidence and answers:

- which missing manifest chunks should be requested in this batch;
- how many bytes that batch represents;
- whether more chunks remain for later batches;
- whether the inspection evidence was forged, stale, inconsistent, or complete.

Without this boundary, the future peer session would duplicate transfer-policy logic outside the sync domain.

## What changed

Rev0663 adds a public C++ request-planning primitive:

- `SyncChunkRequestPlanOptions`
- `SyncChunkRequestPlanResult`
- `build_sync_chunk_request_plan(...)`

The planner validates the remote file entry and local apply intent with the same staged-remote evidence checks used by chunk writes and staged-transfer inspection. It then verifies that the inspection result is bound to that exact path, staging path, apply idempotency key, remote entry digest, receipt count, and complete-file state. `missing_chunks` must be an ordered subset of the remote manifest chunks; forged offsets, reordered chunks, count mismatches, partial inspections with whole-file evidence, and complete inspections carrying missing chunks all fail closed.

After validation, the planner emits deterministic `sync-chunk-request:v1:` evidence and selects a chunk batch using optional `max_chunks_per_request` and `max_bytes_per_request` budgets. A zero budget means unlimited for that dimension. A nonzero byte budget that cannot carry the first missing chunk is rejected instead of returning an endlessly empty request.

## Audit/refactor finding

The audited gap was scheduler trust. Rev0662 gave the cube a good inspection API, but a caller could still construct or edit an inspection-like structure and ask a peer for chunks based on unvalidated `missing_chunks`. Rev0663 moves that batch selection into the C++ sync domain, where the request plan can be checked against manifest order, receipt counts, and idempotency evidence before peer I/O begins.

This is still deliberately not networking. It is the local deterministic planning seam a fake peer-session harness can call next.

## Safety properties added

- Request batches are selected only from inspection evidence bound to the same remote entry and local apply intent.
- Missing chunks must be an ordered subset of the remote manifest chunks.
- Receipt/missing counts must add up to the remote manifest chunk count.
- Complete staged transfers produce no peer chunk requests.
- Partial inspections may not carry whole-file completion evidence.
- Byte and chunk budgets are deterministic and do not split chunks.
- Too-small byte budgets fail closed instead of spinning on empty request batches.
- Request evidence is deterministic and prefixed as `sync-chunk-request:v1:` for future scheduler logs or persistence.

## Validation evidence

The sync-domain selftest now covers:

- converting a verified partial inspection into a one-chunk request batch;
- deterministic `sync-chunk-request:v1:` evidence;
- `more_chunks_available` and selected-byte accounting;
- rejecting byte budgets too small for the first missing chunk;
- rejecting forged missing chunks not present in the remote manifest order;
- producing no requests for a complete staged transfer.

Recorded validation for this package:

```bash
cmake -S cpp/anonsync_core -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS_RELEASE='-O0 -g0'
cmake --build build --target anonsync_core -j2
ctest --test-dir build --output-on-failure
./build/anonsync_core --selftest-sync-domain-model
python3 tools/validate_rev0663_chunk_request_plan.py
```

A narrow ASAN/UBSAN sync-domain selftest was also recorded for this revision.

## Remaining ceiling

Rev0663 still does not send chunk requests to a peer, persist transfer scheduler state, clean up orphan `.part` or `.chunks` sidecars, garbage-collect receipts after commit, or implement peer discovery/transport. The next code-bearing step should add a fake authenticated peer-session harness that uses `inspect_sync_staged_transfer`, `build_sync_chunk_request_plan`, `write_sync_staged_chunk`, and receipt-gated materialization end to end.
