# Rev0672 — fake peer-session convergence harness

## Scope of this linked revision

Rev0672 is code-bearing. It promotes a new active C++ executable:

- `bin/rev0672/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3`

The revision implements the rev0671 recommendation: stop adding isolated wrappers for a moment and build a deterministic fake peer-session harness that proves the existing sync-domain boundaries can converge a destination folder to a source peer manifest.

## Mission fit

The heart of AnonSync is folder convergence under evidence-bound local truth. Rev0672 moves that mission forward by proving a source/destination file-fetch path through the real local primitives:

`source scan → destination scan → manifest diff → local apply plan → staged inspection → chunk request → peer schedule → peer-bound response batch → peer transfer round continuation → receipt-gated materialization → destination rescan → content convergence`

This is not a network feature. It is the product-shaped test harness that a network feature should later satisfy.

## Public C++ surface

Rev0672 adds:

- `SyncFakePeerFileFetchSessionOptions`
- `SyncFakePeerFileFetchSessionFileResult`
- `SyncFakePeerFileFetchSessionResult`
- `run_sync_fake_peer_file_fetch_session`

The result records the source manifest, destination manifest before sync, diff plan, local apply plan, destination manifest after sync, files materialized, transfer rounds, chunks written, receipts reused, bytes materialized, source and destination convergence-content digests, and per-file materialization evidence.

## Audit/refactor performed

The audit finding was that rev0670 had strong micro-boundaries but no product-shaped owner for the loop between them. Callers still had to decide how to repeatedly inspect, request, schedule, synthesize or receive peer responses, advance transfer rounds, and then materialize.

Rev0672 refactors that caller glue into one deterministic C++ boundary for the file-fetch path. The new boundary does not bypass the lower-level checks; it calls them in order and fails closed if an unsupported mutation appears.

A second audit finding was root topology risk. A fake harness that writes staged bytes while scanning local paths must never let source, destination, or staging roots overlap. Rev0672 adds explicit overlap rejection for source/destination and staging roots before scan or byte mutation.

A third audit finding was convergence evidence shape. After materialization, a destination rescan naturally carries destination-local publisher lineage and manifest counters. Rev0672 therefore adds publisher-neutral convergence-content digest helpers for the harness result instead of pretending source and destination manifest-entry digests should match byte-for-byte after local rescan.

## Selftest coverage added

`--selftest-sync-domain-model` now includes a two-file fake peer session. The fixture uses a small chunk size and a one-chunk peer-round cap, forcing multiple peer transfer rounds. The selftest requires:

- a successful run of `run_sync_fake_peer_file_fetch_session`;
- two materialized files;
- `content_converged == true`;
- transfer-round count equal to the source chunk count;
- chunk-write count equal to the source chunk count;
- no receipt reuse on the fresh run;
- exact source bytes at both destination paths;
- matching source/destination convergence-content digests; and
- failure when the staging root overlaps the destination root.

Recorded result: `anonsync_core sync domain model selftest passed=196 failed=0`.

## Validation

The release CTest suite reports `100% tests passed, 0 tests failed out of 27`.

The focused sanitizer selftest reports `anonsync_core sync domain model selftest passed=196 failed=0`.

The package validator is:

```bash
python3 tools/validate_rev0672_fake_peer_session.py
```

## Remaining ceiling

Rev0672 proves file-fetch convergence locally. It still does not claim production sync. Missing pieces include durable transfer/session state, persisted manifest/index rows, cleanup of `.part` and `.chunks` sidecars, tombstone and conflict branches inside the fake session, peer/folder trust material, invite/share-key authority, protocol serialization, authenticated transport, resource governance, and metadata/privacy policy.

The next best move is to persist the fake-session state: manifests, apply intents, chunk requests, peer assignments, accepted response batches, receipt rows, materialization terminal states, and cleanup checkpoints.
