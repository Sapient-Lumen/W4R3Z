# Rev0670 — peer transfer-round continuation

## Why this exists

AnonSync is a C++ peer-to-peer file synchronization product. Rev0668 made missing-chunk work schedulable across peers. Rev0669 made one scheduled peer response fail closed unless the batch matched the exact peer schedule and per-peer assignment. The remaining execution gap was continuation: a daemon still had to manually compose scheduled-peer acceptance, receipt-backed reinspection, next request planning, and next peer scheduling after each peer response.

For a Resilio-style sync engine, that composition should be a small, deterministic C++ boundary. Otherwise different callers can disagree about when a peer round is complete, whether the next request is safe to issue, or which peers are allowed to receive continuation work.

## What changed

Rev0670 adds public C++ peer transfer-round primitives:

- `SyncPeerChunkTransferRoundResult`
- `accept_sync_peer_chunk_response_batch_and_plan_next`

`accept_sync_peer_chunk_response_batch_and_plan_next` accepts one `SyncPeerChunkResponseBatchEnvelope` for one scheduled peer assignment, then immediately re-inspects the staged file and chunk receipts, builds the next `sync-chunk-request:v1:` plan, filters next-peer availability down to the verified next request batch, and builds the next `sync-peer-chunk-schedule:v1:` result. The result carries `ready_to_materialize`, `more_chunks_needed`, and `peer_work_scheduled` flags so a future daemon loop can advance without re-deriving state by convention.

## Audit/refactor finding

The rev0669 peer-bound response path was safe, but it ended at byte acceptance. The caller had to separately choose inspection roots, call `inspect_sync_staged_transfer`, call `build_sync_chunk_request_plan`, prune peer availability, and call `build_sync_peer_chunk_schedule`. That made the exact continuation edge easy to duplicate incorrectly.

Rev0670 fixes that by creating one transfer-round boundary above peer-bound acceptance. The refactor also adds two internal helpers:

- next-peer availability validation against portable peer/session ids and remote manifest chunks before any peer bytes are accepted;
- next-peer availability filtering so broad peer availability is narrowed to the verified next request before scheduling.

This avoids the dangerous shape where invalid future scheduling input could be discovered only after a receipt-backed write had already happened.

## Safety properties added

- Write roots and post-write inspection roots must match lexically before peer bytes can be accepted.
- Future peer availability is validated before the receipt-backed acceptance path is invoked.
- Future peer availability must use portable lowercase sync ids and ordered unique chunks from the remote manifest.
- Broad peer availability can include chunks that are not in the next request; those chunks are filtered out before scheduling.
- Peer-bound acceptance still validates request evidence, peer schedule evidence, scheduled assignment membership, response subset ordering, peer response batch id, byte lengths, byte hashes, chunk receipts, and staged bytes.
- Post-batch inspection must agree with acceptance about complete/incomplete staged-file state.
- A complete post-batch inspection must carry whole-file content evidence matching the remote manifest.
- The next request plan and next peer schedule are derived from the post-batch inspection, not from caller-provided mutable state.

## Validation evidence

The sync-domain selftest now covers:

- peer transfer-round root mismatch rejection before byte acceptance;
- scheduled peer batch acceptance through the new transfer-round function;
- post-batch staged-transfer reinspection;
- continuation `sync-chunk-request:v1:` planning;
- filtering broad next-peer availability into a request-scoped `sync-peer-chunk-schedule:v1:`;
- final materialization-ready evidence after the last peer batch;
- invalid next-peer availability rejection before invoking receipt-backed acceptance;
- preservation of rev0669 peer-bound replay and forged-assignment tests.

Recorded validation for this package:

```bash
cmake --build build_o0 --target anonsync_core -j1
ctest --test-dir build_o0 --output-on-failure
./build_o0/anonsync_core --selftest-sync-domain-model
python3 tools/validate_rev0670_peer_transfer_round.py
```

A narrow ASAN/UBSAN sync-domain selftest was also recorded for this revision.

## Remaining ceiling

Rev0670 still does not run a real peer protocol, authenticate peer sessions, persist transfer/schedule state, exchange manifests over transport, perform peer discovery, clean up orphan `.part` or `.chunks` sidecars, garbage-collect receipt sidecars after materialization, or run a daemon. The next code-bearing revision should either build the deterministic fake peer-session harness around manifest diff → local apply → peer transfer rounds → receipt-gated materialization, or persist transfer/schedule state so interrupted peer assignments can resume safely.
