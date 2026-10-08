# TR-STATUS-01 — download status-message provenance proof (rev0012)

Canonical rows:

```text
U-158 lead: UploadFailed/UploadDenied peer status messages can drive download abort/retry state using only claimed username and virtual path.
U-166 subcase: PlaceInQueueResponse can update queued-download queue position using only claimed username and virtual path.
```

## Result

rev0012 built a maintainer-style current-behavior pytest witness and ran it against all current/future archived lanes:

```text
github-tag-3.3.10: 4 passed
github-branch-3.3.x: 4 passed
github-branch-master: 4 passed
```

## Current behavior proven

### U-158 / UploadFailed active-close and retry

A local active download keyed by `username + token` and indexed by `username + virtual_path` can be acted on by `UploadFailed(file)` when the peer-connection layer supplies the matching claimed username. The message itself carries no transfer token or generation.

Observed current behavior:

```text
UploadFailed(filename) with claimed username
-> finds transfer through downloads.transfers[username + virtual_path]
-> verifies only that local token is active OR path is failed/queued
-> aborts active transfer
-> sends CloseConnection(active F socket)
-> cancels request timer
-> removes active_users[username][token]
-> sets legacy_attempt and retry_attempt
-> requeues the same virtual path via QueueUpload
```

### U-158 / UploadDenied queued-state mutation

A queued download can be moved to failed state using `UploadDenied(file, reason)` with only claimed username plus virtual path.

Observed current behavior:

```text
UploadDenied(filename, arbitrary reason)
-> finds queued_users[username][virtual_path]
-> removes queued transfer
-> places transfer in failed_users
-> sets transfer.status to the peer-supplied reason unless normalized as an internal/limit status
```

### U-166 / PlaceInQueueResponse queue-position mutation

A queued download's visible queue position can be updated by `PlaceInQueueResponse(filename, place)` with claimed username plus virtual path.

Observed current behavior:

```text
PlaceInQueueResponse(filename, 4294967295)
-> finds queued_users[username][virtual_path]
-> sets transfer.queue_position = 4294967295
-> emits update-download
```

## Affected lanes

```text
github-tag-3.3.10: caf9e101a841ff2e0a96aebc8e07bbf7ff1b2026
github-branch-3.3.x: 98089ac233aa57786e8dbdc48123f6ac1c4767d8
github-branch-master: f4e17d59783dbc48ea31d2e899a681e2dd1ed500
```

## Why this is not promoted as a strict standalone report

The behavior is real, but the strict document should stay small and coherent.

- A legitimate uploading peer is expected to be able to fail or deny its own upload. The more interesting boundary is whether another connection/source can successfully claim that username and status-message authority.
- PB-01 already proves the stronger source-binding/primary-election problem. TR-STATUS-01 is best kept as a transfer-status regression companion unless a network-level path independent of PB-01 is proven.
- U-166 is low standalone value: queue-position mutation is visible state/UI/queue accounting, not transfer-session control.
- Public material already covers `UploadFailed`/`UploadDenied` semantics and upload queue position/request performance. No direct match was found for the exact claimed-username + virtual-path binding invariant, but it is public-adjacent.

## Suggested fix shape if maintainers choose to address it

One coherent fix is preferable to separate ad hoc checks:

```text
- Attach transfer-status authority to a transfer generation/session, not only username + virtual_path.
- For UploadFailed, require a current transfer session/source expectation before closing an active F socket or requeueing.
- For UploadDenied, distinguish expected response to our QueueUpload from unsolicited status messages; ignore or quarantine unmatched statuses.
- For PlaceInQueueResponse, require a pending PlaceInQueueRequest generation or cap/coerce queue positions before UI state mutation.
- Preserve compatibility with older clients that legitimately use UploadFailed for retry and UploadDenied for abort.
```

## Evidence files

```text
maintainer_artifacts/tr-status-01/test_transfer_status_message_binding_reproducer.py
evidence/rev0012-tr-status-reproducer-run.txt
evidence/rev0012-tr-status-source-trace.md
evidence/rev0012-web-public-overlap-tr-status.md
data/rev0012_tr_status_probe_summary.csv
```
