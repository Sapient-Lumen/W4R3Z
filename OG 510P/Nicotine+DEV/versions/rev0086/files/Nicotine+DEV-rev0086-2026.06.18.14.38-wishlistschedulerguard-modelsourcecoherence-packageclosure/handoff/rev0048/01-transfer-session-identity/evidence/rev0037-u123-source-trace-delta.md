# rev0037 U-123 source-trace delta

Rev0037 keeps the rev0036 source anchors and adds a fix-choice delta. The additional source invariant is that `Downloads._transfer_request_downloads()` accepts a peer-supplied `TransferRequest` token before checking whether that username+token slot already belongs to a different active download.

## Delta anchors

| lane | downloads.py collision check insertion point | transfers.py deactivation guard insertion point |
|---|---|---|
| github-tag-3.3.10 | after `download = queued_users... or failed_users...`; before `_unfail_transfer()` / `_dequeue_transfer()` | inside `_deactivate_transfer()` before deleting `active_users[username][token]` |
| github-branch-3.3.x | same source shape | same source shape |
| github-branch-master | same source shape | same source shape |

## Why the insertion point matters

The collision check must happen before `_dequeue_transfer(download)` so a colliding queued transfer remains queued when the peer reuses an active token. Checking only in `_activate_transfer()` would be too late unless every caller honored a new return value and restored queue state.
