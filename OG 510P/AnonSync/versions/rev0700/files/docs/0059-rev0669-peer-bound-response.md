# Rev0669 — peer-bound response acceptance

## Why this exists

AnonSync is a C++ peer-to-peer file synchronization product. Rev0668 introduced deterministic peer chunk scheduling: one verified `sync-chunk-request:v1:` batch can be split into per-peer `sync-peer-chunk-request:v1:` assignments with exact unassigned chunks. The audited gap was the next execution edge. A generic `sync-chunk-response-batch:v1:` proves a batch answers the current missing-chunk request, but it does not by itself prove that the responding peer/session was the peer assigned to those chunks by the schedule.

That matters for a Resilio-style sync engine. A daemon should be able to reject stale, cross-peer, or forged scheduled work before bytes reach the staged file. Otherwise scheduler evidence can drift away from transfer acceptance, making retries and multi-peer sessions harder to reason about.

## What changed

Rev0669 adds public C++ peer-bound response primitives:

- `SyncPeerChunkResponseBatchEnvelope`
- `SyncPeerChunkResponseBatchAcceptanceResult`
- `build_sync_peer_chunk_response_batch_envelope`
- `accept_sync_peer_chunk_response_batch_envelope`

`SyncPeerChunkResponseBatchEnvelope` carries the global request id, the `sync-peer-chunk-schedule:v1:` id, peer id, peer session id, the scheduled `sync-peer-chunk-request:v1:` id, the underlying `sync-chunk-response-batch:v1:` id, remote entry/version digests, apply intent id, response count, total bytes, and ordered response envelopes. Its `sync-peer-chunk-response-batch:v1:` id commits to the schedule id, peer assignment, base batch evidence, response count, byte total, and response envelope digest.

`accept_sync_peer_chunk_response_batch_envelope` rebuilds the request plan from staged inspection/options evidence, validates the peer schedule shape, requires the supplied assignment to appear in the schedule, checks that response chunks are an ordered unique subset of that peer assignment, rebuilds the expected peer-bound envelope, and only then delegates to the existing receipt-backed batch acceptance path.

## Audit/refactor finding

The rev0668 scheduler made peer work deterministic, but scheduled execution still had to be enforced by caller glue. The old batch acceptance path could reject stale request ids and forged batch ids, yet it had no concept of the peer schedule or per-peer assignment. The refactor added shared validation helpers for request-plan shape and peer-schedule shape so both scheduling and peer-bound response handling use one evidence vocabulary.

This keeps the new boundary narrow: no network protocol was added, no peer authentication is claimed, and no staging semantics were duplicated. The peer-bound path proves assignment ownership, then reuses the existing receipt-backed write pipeline.

## Safety properties added

- Peer-bound response batches require a valid remote file entry and local apply intent that stages a remote file.
- The request plan is re-derived from receipt-checked staged inspection evidence during acceptance.
- The schedule must carry a `sync-peer-chunk-schedule:v1:` id, match the request totals, and cover every selected request chunk as assigned or unassigned.
- Scheduled assignments must be sorted by unique peer id, carry valid portable peer/session ids, have consistent assigned chunk/byte counts, and carry the exact `sync-peer-chunk-request:v1:` key for their chunks.
- A response batch must be tied to an assignment present in the schedule.
- Response chunks must be an ordered unique subset of that scheduled peer assignment.
- Cross-peer replay is rejected before chunk bytes are written.
- Forged peer assignments are rejected by the envelope builder.

## Validation evidence

The sync-domain selftest now covers:

- peer-bound batch envelope creation;
- schedule id and per-peer request id binding;
- successful scheduled assignment acceptance before byte writes;
- cross-peer replay rejection;
- forged assignment rejection;
- preservation of rev0668 scheduling and rev0667 continuation tests.

Recorded validation for this package:

```bash
cmake --build build_o0 --target anonsync_core -j2
ctest --test-dir build_o0 --output-on-failure
./build_o0/anonsync_core --selftest-sync-domain-model
python3 tools/validate_rev0669_peer_bound_response.py
```

A narrow ASAN/UBSAN sync-domain selftest was also recorded for this revision.

## Remaining ceiling

Rev0669 still does not run a real peer protocol, authenticate peer sessions, persist transfer/schedule state, exchange manifests over transport, perform peer discovery, clean up orphan `.part` or `.chunks` sidecars, garbage-collect receipt sidecars after materialization, or run a daemon. The next code-bearing revision should build the deterministic fake peer-session harness around manifest diff → local apply → inspection → request → peer schedule → peer-bound response acceptance → continuation → receipt-gated materialization, or persist transfer/schedule state so interrupted sessions can resume safely.
