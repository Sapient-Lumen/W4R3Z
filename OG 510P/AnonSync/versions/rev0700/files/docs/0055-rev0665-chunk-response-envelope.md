# Rev0665 — chunk response envelope

## Why this exists

AnonSync is a C++ peer-to-peer file synchronization product. Rev0663 made deterministic chunk request batches from verified staged-transfer inspection state, and rev0664 added request-bound chunk acceptance so arbitrary manifest chunks are not handed straight to the staged writer.

The next missing seam was the network-facing response object itself. A real or fake peer session will not receive a naked `SyncChunkRange` plus bytes in a vacuum; it will receive a response that claims to answer a specific request batch. If AnonSync does not model that envelope, the daemon has no compact evidence that the response came from the current `sync-chunk-request:v1:` batch rather than a stale request, a different transfer attempt, or a forged local caller object.

## What changed

Rev0665 adds public C++ response-envelope primitives:

- `SyncChunkResponseEnvelope`
- `build_sync_chunk_response_envelope(...)`
- `accept_sync_chunk_response_envelope(...)`

The envelope binds:

- the normalized sync path;
- the `sync-chunk-request:v1:` request idempotency key;
- a deterministic `sync-chunk-response:v1:` response idempotency key;
- the remote entry digest and publisher-neutral version digest;
- the local apply intent idempotency key;
- the response chunk offset, length, and SHA-256.

`build_sync_chunk_response_envelope` only builds an envelope for a chunk selected by the request batch. It rejects complete transfers, empty request batches, inconsistent selected counts/byte counts, chunks not ordered from the remote manifest, and unselected chunks.

`accept_sync_chunk_response_envelope` rebuilds the expected chunk request plan from the remote entry, apply intent, staged-transfer inspection, and request options. It then rebuilds the expected response envelope and compares every field before bytes reach the existing requested-chunk acceptance path. Accepted bytes still pass through `accept_sync_requested_chunk` and `write_sync_staged_chunk`, preserving the existing receipt reuse and post-write staged-transfer inspection behavior.

## Audit/refactor finding

The audited gap was cross-batch response confusion. Rev0664 safely checked request evidence inside the local acceptance function, but it did not require a peer-visible response commitment. That meant the future peer session still had to invent ad hoc metadata for request IDs and response IDs.

Rev0665 makes that boundary explicit. Higher layers can now treat `sync-chunk-request:v1:` as the batch command and `sync-chunk-response:v1:` as the peer response commitment. A stale request ID, forged response ID, mismatched remote digest, mismatched apply intent, or wrong chunk range fails before disk staging.

## Safety properties added

- Peer response metadata carries a deterministic `sync-chunk-response:v1:` key.
- A response envelope cannot be built for a chunk outside the selected request batch.
- Response acceptance rejects stale `sync-chunk-request:v1:` IDs before writing bytes.
- Response acceptance rejects forged `sync-chunk-response:v1:` IDs before writing bytes.
- Accepted responses record both `request_evidence_checked` and `response_envelope_checked` in `SyncRequestedChunkAcceptanceResult`.
- Lower-level `write_sync_staged_chunk` remains a reusable primitive, while peer/session code gets a stricter response-envelope API.

## Validation evidence

The sync-domain selftest now covers:

- rejecting envelope construction for chunks outside the selected request batch;
- building an envelope that binds request ID, response ID, remote entry digest, version digest, apply intent, and chunk range;
- rejecting a stale request ID in the response envelope;
- rejecting a forged response ID in the response envelope;
- accepting a valid response envelope only after request and response evidence are checked.

Recorded validation for this package:

```bash
cmake -S cpp/anonsync_core -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS_RELEASE='-O0 -g0 -DNDEBUG'
cmake --build build --target anonsync_core -j2
ctest --test-dir build --output-on-failure
./build/anonsync_core --selftest-sync-domain-model
python3 tools/validate_rev0665_chunk_response_envelope.py
```

A narrow ASAN/UBSAN sync-domain selftest was also recorded for this revision.

## Remaining ceiling

Rev0665 still does not run a real or fake peer session, persist transfer scheduler state, retry failed request batches, clean up orphan `.part` or `.chunks` sidecars, garbage-collect receipts after commit, or implement peer discovery/transport. The next code-bearing step should add a deterministic fake peer-session harness that loops inspection, chunk request planning, response envelope construction, response acceptance, receipt-gated materialization, and tombstone/conflict application end to end.
