# Rev0666 — chunk response batch

## Why this exists

AnonSync is a C++ peer-to-peer file synchronization product. Rev0663 made deterministic chunk request batches from verified staged-transfer inspection state, rev0664 made peer bytes pass through request-bound acceptance, and rev0665 added a peer-visible `SyncChunkResponseEnvelope` for one selected chunk.

The next missing seam was batch response handling. A real or fake peer session should not have to treat every returned chunk as an unrelated response once a request batch was already selected. It should be able to say: this set of response envelopes answers this `sync-chunk-request:v1:` batch, in this exact order, with this total byte count, and with one deterministic batch commitment before any byte is staged.

## What changed

Rev0666 adds public C++ batch-response primitives:

- `SyncChunkResponseBatchEnvelope`
- `SyncChunkResponseBatchAcceptanceResult`
- `build_sync_chunk_response_batch_envelope(...)`
- `accept_sync_chunk_response_batch_envelope(...)`

The batch envelope binds:

- the normalized sync path;
- the `sync-chunk-request:v1:` request idempotency key;
- a deterministic `sync-chunk-response-batch:v1:` batch idempotency key;
- the remote entry digest and publisher-neutral version digest;
- the local apply intent idempotency key;
- the response count and total response bytes;
- the ordered list of individual `SyncChunkResponseEnvelope` values.

`build_sync_chunk_response_batch_envelope` only builds a batch for an ordered unique subset of chunks selected by the request batch. It rejects complete transfers, empty request batches, empty response sets, inconsistent selected counts/byte counts, request chunks that are not an ordered subset of the remote manifest, duplicate response chunks, out-of-order response chunks, and response chunks outside the selected request batch.

`accept_sync_chunk_response_batch_envelope` rebuilds the expected chunk request plan from the remote entry, apply intent, staged-transfer inspection, and request options. It then rebuilds the expected batch envelope and compares every batch field and every included individual response envelope. Before writing, it prevalidates each supplied byte string against the response length and SHA-256. Only after the whole batch envelope and all bytes pass preflight does it delegate each response through `accept_sync_chunk_response_envelope`, preserving the rev0665 response-envelope check and the rev0660 receipt-backed staged writer.

## Audit/refactor finding

The audited gap was batch-level replay/cross-response confusion. Rev0665 prevented a single stale or forged response from reaching disk, but the future session layer still had no typed way to accept a multi-chunk peer answer as one deterministic batch. That would have pushed response counting, duplicate detection, byte-total checks, and batch IDs into ad hoc daemon code.

Rev0666 moves those invariants into the C++ sync-domain boundary. A session can now treat `sync-chunk-request:v1:` as the command, `sync-chunk-response:v1:` as each per-chunk commitment, and `sync-chunk-response-batch:v1:` as the peer batch commitment. A forged batch ID, mismatched response count, mismatched total bytes, duplicate chunk, out-of-order response, stale request plan, wrong remote digest, wrong apply intent, or byte hash mismatch fails before staged chunk writes.

## Safety properties added

- Peer batch metadata carries a deterministic `sync-chunk-response-batch:v1:` key.
- A batch cannot be built for duplicate or out-of-order response chunks.
- A batch cannot contain chunks outside the selected `sync-chunk-request:v1:` batch.
- Batch acceptance rebuilds request evidence and batch evidence before writing.
- Batch acceptance prevalidates every response byte length and SHA-256 before staging begins.
- Batch acceptance still routes each chunk through individual response-envelope acceptance and `sync-chunk-receipt:v1:` writes.
- Batch result evidence reports request verification, batch verification, written chunks, reused receipts, completion state, and per-chunk acceptance evidence.

## Validation evidence

The sync-domain selftest now covers:

- rejecting duplicate response chunks in a batch envelope;
- building a two-response batch envelope from an ordered unique subset of a valid request batch;
- rejecting a forged `sync-chunk-response-batch:v1:` ID before staging bytes;
- accepting a valid two-response batch that completes a staged transfer from one reusable existing receipt plus two peer responses;
- retaining individual response-envelope checks inside batch acceptance.

Recorded validation for this package:

```bash
cmake -S cpp/anonsync_core -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS_RELEASE='-O0 -g0 -DNDEBUG'
cmake --build build --target anonsync_core -j2
ctest --test-dir build --output-on-failure
./build/anonsync_core --selftest-sync-domain-model
python3 tools/validate_rev0666_chunk_response_batch.py
```

A narrow ASAN/UBSAN sync-domain selftest was also recorded for this revision.

## Remaining ceiling

Rev0666 still does not run a real or fake peer session, persist transfer scheduler state, retry failed request batches, clean up orphan `.part` or `.chunks` sidecars, garbage-collect receipts after commit, or implement peer discovery/transport. The next code-bearing step should either add a deterministic fake peer-session harness that loops inspection, chunk request planning, batch response envelope construction, batch response acceptance, receipt-gated materialization, and tombstone/conflict application end to end; or add durable transfer cleanup/persistence so staged sidecars are not left unmanaged after success or crash.
