# Production-draft report — U-123

## Title

Duplicate peer-supplied download transfer tokens can orphan an active F-connection transfer session

## Status

Production-draft packet complete in rev0036. This is still marked **not production-ready** until the maintainer-facing fix strategy is chosen and the final disclosure/issue wording is reviewed.

## Summary

A peer that can send two accepted download-side `TransferRequest` messages for the same username and token can cause Nicotine+ to overwrite the active transfer map entry for the first `Transfer` object with a second `Transfer` object. If the stale timeout callback for the first object later fires, the shared `active_users[username][token]` entry is deleted without checking whether that entry still belongs to the first object. The later F-connection session is then no longer reachable by file-progress or connection-closed callbacks that route through the same username+token map.

The proof is local and socket-free. It demonstrates transfer-session state confusion and callback orphaning. It does **not** claim remote code execution, credential exposure, or file disclosure.

## Affected code invariant

Across the archived `github-tag-3.3.10`, `github-branch-3.3.x`, and `github-branch-master` lanes:

```text
Transfers._activate_transfer():
  self.active_users[transfer.username][token] = transfer

Transfers._deactivate_transfer():
  del self.active_users[username][token]

Downloads._file_transfer_init(), _file_download_progress(), and _file_connection_closed():
  download = self.active_users.get(username, {}).get(token)
```

The activation key is username+token, but deactivation is not object-identity aware. A timer callback closes over the old `Transfer` object, while the active map slot may already point to a later object.

## Protocol context

`TransferRequest` carries a peer-visible uint32 token, and `FileTransferInit` uses the same token on the file (`F`) connection. This makes the implementation map key understandable, but it also means the local transfer object/session identity must not be inferred solely from username+token once duplicate or stale callbacks are possible.

## Reproduction outline

Use the rev0036 maintainer artifact:

```text
maintainer_artifacts/u123/test_downloads_duplicate_transfer_token_reproducer.py
```

The test queues two downloads from the same user, injects two `TransferRequest` messages with the same token, lets the second request reach F-connection state, and then fires the stale request timeout for the first transfer object.

Observed current behavior on all three archived lanes:

```text
1. first activation maps active_users[user][token] -> first
2. second activation maps active_users[user][token] -> second
3. second receives FileTransferInit and opens its file handle/socket state
4. first timeout calls _deactivate_transfer(first)
5. _deactivate_transfer deletes active_users[user][token]
6. progress/close callbacks for second are ignored because the map lookup now returns None
```

Rev0036 rerun evidence:

```text
github-tag-3.3.10:   current witness OK; fixed regression expected-fails; identity-guard simulation OK
github-branch-3.3.x: current witness OK; fixed regression expected-fails; identity-guard simulation OK
github-branch-master: current witness OK; fixed regression expected-fails; identity-guard simulation OK
```

## Expected fixed behavior

A stale timeout for an older transfer object may fail and clean up that old object, but it must not delete an active username+token mapping that now belongs to a newer transfer/session object. After the stale first timeout fires, later progress and close callbacks for the second F-connection session should still route to the second transfer.

The rev0036 fixed-behavior regression skeleton captures that expectation:

```text
maintainer_artifacts/u123/test_downloads_duplicate_transfer_token_fixed_regression.py
```

## Fix guidance

At minimum, destructive deactivation should be identity-aware. A conservative shape is:

```python
active_transfer = self.active_users.get(username, {}).get(token)
if active_transfer is transfer:
    del self.active_users[username][token]
elif active_transfer is not None:
    # The slot belongs to a newer same-user/same-token session.
    # Do not delete it while cleaning/failing the stale object.
    pass
```

The transfer-local cleanup path should still be considered carefully: stale request timers, stale sockets, token fields, bandwidth accounting, failed-user tracking, and user-watch lifetime need to remain consistent for the object being aborted. The final upstream fix may instead reject duplicate same-user/same-token activation while active, or introduce an explicit local session/generation identity. The required property is that a stale callback for object A cannot remove or corrupt object B's active session.

## Compatibility notes

The fix should preserve legitimate transfer flows:

```text
- normal QueueUpload -> TransferRequest -> TransferResponse -> FileTransferInit flow;
- queued transfer becoming ready after a delay;
- retry/requeue/resume of the same transfer object;
- duplicate FileTransferInit on an already-socketed transfer should still close/ignore the duplicate as today;
- user-watch lifetime should not be prematurely unwatched while queued/active/failed transfers remain.
```

The report should not prescribe a protocol change. This can be fixed locally with identity checks, duplicate activation policy, or local session generation.

## Impact boundary

Bounded impact: availability and transfer-session integrity. A malicious or buggy peer can cause a live download session to become orphaned from its progress/close callbacks, leaving stale transfer state and an open local file/session until other cleanup paths intervene. This proof does not establish arbitrary file access, authentication bypass, or code execution.

## Public-overlap classification

Use the conservative class:

```text
candidate no exact direct public match found; transfer-lifecycle adjacent public issues exist
```

Public materials cover transfer-token protocol context and adjacent transfer-lifecycle symptoms, but the rev0036 searches did not identify a direct public duplicate of the narrower chain: duplicate peer-supplied download token, stale first timeout, active-map deletion, and ignored later F-connection callbacks.

## Attachments to include

```text
maintainer_artifacts/u123/test_downloads_duplicate_transfer_token_reproducer.py
maintainer_artifacts/u123/test_downloads_duplicate_transfer_token_fixed_regression.py
evidence/rev0036-u123-current-and-fixed-regression-rerun.txt
evidence/rev0036-u123-identity-guard-simulation.txt
evidence/rev0036-u123-source-trace.md
evidence/rev0036-web-public-overlap-u123.md
```
