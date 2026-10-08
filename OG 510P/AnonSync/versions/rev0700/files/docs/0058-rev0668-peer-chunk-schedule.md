# Rev0668 — peer chunk schedule

## Why this exists

AnonSync is a C++ peer-to-peer file synchronization product. Rev0667 can accept one batch of peer chunk responses, re-inspect staged receipt state, and produce the next deterministic chunk request. The audited gap above that layer was multi-peer scheduling: the daemon could know which chunks are missing, but it still had no deterministic C++ boundary for deciding which peer should be asked for which chunks when more than one peer can provide the same content.

That is a real sync-product seam. Without a schedule primitive, caller/session glue tends to make ad hoc choices, duplicate network work, accept overbroad peer availability, or lose the exact unassigned chunk set needed to wait for another peer.

## What changed

Rev0668 adds public C++ peer scheduling primitives:

- `SyncPeerChunkAvailability`
- `SyncPeerChunkAssignment`
- `SyncPeerChunkScheduleResult`
- `build_sync_peer_chunk_schedule(...)`

`SyncPeerChunkAvailability` records one peer/session and the ordered subset of the current `sync-chunk-request:v1:` batch that peer claims it can serve, plus optional per-peer chunk and byte caps. `build_sync_peer_chunk_schedule` sorts peer availability deterministically by peer id/session id, rejects duplicate peer ids, rejects invalid peer/session identifiers, rejects empty peer advertisements, rejects peer chunks outside the selected request batch, and greedily assigns request chunks in request order to the first available peer with remaining capacity.

The result carries the overall `sync-peer-chunk-schedule:v1:` id, the original request id, totals for requested and assigned chunks/bytes, per-peer `sync-peer-chunk-request:v1:` ids, exact per-peer chunk assignments, and exact unassigned chunks when availability or per-peer budget cannot cover the full request.

## Audit/refactor finding

The audited risk after rev0667 was scheduler drift outside the evidence boundary. `accept_sync_chunk_response_batch_and_plan_next` correctly returns a next request plan, but a real P2P sync daemon then has to choose peers. If that choice is not deterministic and evidence-bound, retries can request different chunks from different peers for the same missing state, peer advertisements can include chunks that were not requested, and partial availability can be confused with a complete transfer plan.

Rev0668 moves that choice into the C++ sync-domain layer. The caller now gets a stable peer work plan with explicit unassigned chunks instead of inventing scheduling semantics in network/session code.

## Safety properties added

- Peer scheduling requires a valid remote file entry and local apply intent that stages a remote file.
- The request plan must have a `sync-chunk-request:v1:` id, selected chunk counts/bytes must match the chunk vector, and requested chunks must be an ordered subset of the remote manifest entry.
- Peer ids and peer session ids must be portable sync ids.
- Duplicate peer ids are rejected before network work is produced.
- Each peer availability set must be an ordered unique subset of the selected request batch.
- Per-peer chunk and byte caps are honored deterministically.
- The result carries exact unassigned chunks when the current peer set cannot cover the whole request.

## Validation evidence

The sync-domain selftest now covers:

- deterministic scheduling across input peers supplied in reverse order;
- per-peer `sync-peer-chunk-request:v1:` evidence;
- partial scheduling with exact unassigned chunks;
- duplicate peer-id rejection;
- rejection of peer availability outside the selected request batch;
- preservation of rev0667 transfer-round continuation tests.

Recorded validation for this package:

```bash
cmake --build build --target anonsync_core -j2
ctest --test-dir build --output-on-failure
./build/anonsync_core --selftest-sync-domain-model
python3 tools/validate_rev0668_peer_chunk_schedule.py
```

A narrow ASAN/UBSAN sync-domain selftest was also recorded for this revision.

## Remaining ceiling

Rev0668 still does not run a real peer protocol, authenticate peer sessions, persist transfer scheduler state, clean up orphan `.part` or `.chunks` sidecars, garbage-collect receipt sidecars after materialization, exchange manifests over a transport, implement peer discovery, or retry across real network failures. The next code-bearing revision should either build the deterministic fake peer-session harness around manifest diff → local apply → inspection → request → peer schedule → batch response → continuation → receipt-gated materialization, or persist the transfer/schedule state so interrupted sessions can resume without recomputing everything from scratch.
