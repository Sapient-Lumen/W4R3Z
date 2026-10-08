# Rev0664 — requested chunk acceptance

## Why this exists

AnonSync is a C++ peer-to-peer file synchronization product. Rev0662 made partial staged transfers inspectable after restart, and rev0663 turned that verified inspection state into deterministic `sync-chunk-request:v1:` batches.

The next missing seam was peer response acceptance. A future peer/session loop must not receive arbitrary valid manifest chunks and hand them directly to the staged writer. The response bytes need to be checked against the exact request evidence that selected them. Otherwise, a buggy or malicious peer-session layer could ask for one chunk but stage a different chunk from the same manifest, bypassing request-batch budgeting and scheduler evidence.

## What changed

Rev0664 adds a public C++ response-acceptance primitive:

- `SyncRequestedChunkAcceptanceResult`
- `accept_sync_requested_chunk(...)`

The new function rebuilds the expected `SyncChunkRequestPlanResult` from:

- the remote manifest file entry;
- the local apply intent;
- the staged-transfer inspection result;
- the request planning options.

It then compares that rebuilt request plan against the caller-provided request evidence. Only after the request idempotency key, selected chunks, selected byte count, completion state, and remaining-work flags match does it accept a response chunk. The response chunk must be one of the chunks selected in the verified request batch. Already-complete staged transfers, empty request batches, caller-mutated request metadata, and unrequested response chunks fail closed.

Accepted chunks still flow through `write_sync_staged_chunk`, so the previous receipt reuse, receipt material, chunk-byte hash checking, `.part` write behavior, and complete-file inspection remain centralized.

## Audit/refactor finding

The audited gap was request/response separation. Rev0663 safely planned what to ask a peer for, but the lower-level staged chunk writer remained deliberately request-agnostic: it accepted any chunk that belonged to the remote manifest entry. That is fine as a primitive, but unsafe as the only peer-response API.

Rev0664 fixes the seam by adding a narrow peer-response boundary above `write_sync_staged_chunk`. The future peer session can now use this order:

1. `inspect_sync_staged_transfer`
2. `build_sync_chunk_request_plan`
3. send request batch to peer
4. `accept_sync_requested_chunk` for each response
5. receipt-gated `materialize_staged_sync_file` when complete

## Safety properties added

- Peer chunk bytes are accepted only after request-plan evidence is rebuilt and compared.
- A caller-mutated `SyncChunkRequestPlanResult` is rejected before disk staging.
- A peer response for a manifest chunk outside the selected request batch is rejected.
- Complete staged transfers reject further peer response bytes.
- Empty request batches reject peer response bytes.
- Accepted responses preserve existing `sync-chunk-receipt:v1:` idempotency evidence and staged-transfer completion checks.

## Validation evidence

The sync-domain selftest now covers:

- rejecting caller-mutated request-plan evidence;
- rejecting peer bytes for chunks outside the selected request batch;
- accepting requested peer bytes only after request evidence has been checked;
- reusing the accepted first chunk's receipt through the lower-level writer;
- rejecting peer bytes after inspection reports the staged file complete.

Recorded validation for this package:

```bash
cmake -S cpp/anonsync_core -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS_RELEASE='-O0 -g0'
cmake --build build --target anonsync_core -j2
ctest --test-dir build --output-on-failure
./build/anonsync_core --selftest-sync-domain-model
python3 tools/validate_rev0664_requested_chunk_acceptance.py
```

A narrow ASAN/UBSAN sync-domain selftest was also recorded for this revision.

## Remaining ceiling

Rev0664 still does not run a peer session, persist transfer scheduler state, retry failed request batches, clean up orphan `.part` or `.chunks` sidecars, garbage-collect receipts after commit, or implement peer discovery/transport. The next code-bearing step should add a deterministic fake peer-session harness that loops inspection, request planning, requested-chunk acceptance, and receipt-gated materialization end to end.
