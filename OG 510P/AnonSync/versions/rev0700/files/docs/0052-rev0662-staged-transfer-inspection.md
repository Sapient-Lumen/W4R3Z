# Rev0662 — staged transfer inspection for chunk resume

## Why this exists

AnonSync is a C++ peer-to-peer file synchronization product. Rev0660 gave the cube receipt-backed staged chunk writes: a remote chunk can be hashed, written into a `.part` file, and paired with a deterministic receipt. Rev0661 let materialization require those receipts before a staged file is renamed into the synchronized folder.

The missing seam was restart/resume inspection. After a daemon restart, a peer-session scheduler must be able to look at a planned staged transfer and answer:

- which chunks have receipts that still match staged bytes;
- which manifest chunks are missing and should be requested from a peer;
- whether the staged file is now complete and safe to hand to receipt-gated materialization;
- whether a receipt or staged byte was tampered and must fail closed.

Without that inspection API, `write_sync_staged_chunk` knew how to append receipts, but the surrounding sync engine would still have to duplicate receipt-scanning logic or trust stale assumptions.

## What changed

Rev0662 adds a public C++ inspection primitive:

- `SyncStagedTransferInspectionOptions`
- `SyncStagedTransferInspectionResult`
- `inspect_sync_staged_transfer(...)`

The inspector validates the same remote-file/apply-plan evidence used by chunk writes, checks that the local root and staging root are separate safe directories, recomputes the expected staging path from the remote entry digest, verifies existing receipt files against staged byte ranges, returns exact `missing_chunks`, and only reports `staged_file_complete` when every receipt and the complete staged file match the manifest.

Rev0662 also refactors shared staged-remote evidence checks into `validate_staged_remote_file_evidence`, then routes `write_sync_staged_chunk` completion reporting through `inspect_sync_staged_transfer`. That makes the post-write path and the restart/resume path use the same receipt/tamper logic.

## Audit/refactor finding

The audited gap was not a hash bug in the receipt writer; it was a layering bug. The cube had two adjacent claims:

1. chunks can be received and receipted;
2. complete staged files can require those receipts before install.

But it lacked the product-facing query between them: a scheduler could not ask the cube for the current missing chunks without reimplementing receipt layout knowledge. Rev0662 closes that seam and reduces duplicate completion logic in the chunk writer.

## Safety properties added

- Existing matching receipts are counted only after the corresponding staged byte range hashes to the manifest chunk hash.
- Missing receipts are returned as exact `SyncChunkRange` values instead of being treated as fatal transfer errors.
- A receipt with a missing staged file fails closed.
- A receipt whose staged bytes were modified fails closed.
- Complete status requires every receipt plus a whole-file/chunk verification pass with no trailing bytes.
- Inspection emits deterministic `sync-transfer-inspect:v1:` evidence for scheduler logs or future persistence.

## Validation evidence

The sync-domain selftest now covers:

- partial transfer inspection after receiving only the middle chunk;
- exact missing chunk offsets for resume;
- complete inspection after all chunks and receipts are present;
- tampered staged bytes under an existing receipt being rejected by inspection;
- the existing receipt-gated materialization and conflict-preservation paths.

Recorded validation for this package:

```bash
cmake -S cpp/anonsync_core -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS_RELEASE='-O0 -g0'
cmake --build build --target anonsync_core -j2
ctest --test-dir build --output-on-failure
./build/anonsync_core --selftest-sync-domain-model
python3 tools/validate_rev0662_staged_transfer_inspection.py
```

A narrow ASAN/UBSAN sync-domain selftest was also recorded for this revision.

## Remaining ceiling

Rev0662 still does not persist transfer state, clean up orphan `.part` or `.chunks` directories, coordinate chunk requests with real peers, or run a peer-session scheduler. The next code-bearing step should persist inspection/receipt state or build a fake peer-session harness that calls `inspect_sync_staged_transfer` before requesting only the missing chunks.
