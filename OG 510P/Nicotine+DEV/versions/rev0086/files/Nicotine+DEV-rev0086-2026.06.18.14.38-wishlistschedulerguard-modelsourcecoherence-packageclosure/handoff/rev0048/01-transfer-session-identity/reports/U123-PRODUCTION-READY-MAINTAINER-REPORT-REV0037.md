# Maintainer-ready report — U-123 / duplicate transfer-token active-owner collision

## Title

Duplicate peer-supplied download transfer tokens can replace or orphan the active F-connection owner

## Status

Rev0037 production-gated maintainer-ready packet. This text is suitable as the cube's first production-ready maintainer report draft, subject to normal private filing/review choices.

## Summary

A peer can send two accepted download-side `TransferRequest` messages for the same username and token. Nicotine+ stores active downloads in `active_users[username][token]`. Current source accepts the second request and overwrites that slot even if a different transfer already owns the token and has an active F connection. Later progress/close callbacks route only by username+token, so the original active F-connection owner can become unreachable. A stale timeout/deactivation callback can also delete a username+token slot without verifying that the slot still belongs to the timed-out `Transfer` object.

The proof is local and socket-free. It demonstrates transfer-session state confusion and callback orphaning. It does not claim remote code execution, credential exposure, arbitrary file access, or file disclosure.

## Affected invariant

```text
active_users[username][token] must have exactly one live owner.
A new TransferRequest must not replace a different active owner for the same username+token.
A stale cleanup callback must not delete a slot unless that slot still points to the cleanup object.
```

## Reproduction attachments

```text
maintainer_artifacts/u123/test_downloads_duplicate_transfer_token_collision_rejection_regression.py
maintainer_artifacts/u123/test_downloads_duplicate_transfer_token_reproducer.py
evidence/rev0037-u123-collision-rejection-rerun.txt
evidence/rev0037-u123-rejection-patch-diff.md
```

The new regression fails on current source across `github-tag-3.3.10`, `github-branch-3.3.x`, and `github-branch-master`: the second same-user/same-token request is accepted, rather than left queued/rejected. Under the selected prototype patch, the regression passes on all three lanes.

## Expected fixed behavior

If `active_users[username][token]` already points to a different active download, a new same-user/same-token `TransferRequest` must not dequeue and activate another transfer into that slot. For a queued/failed download, keep it queued and return a queued transfer response; for a non-queued remotely initiated colliding request, reject it without creating a new active owner.

Destructive deactivation should also be identity-aware: cleanup for object A may clear the active map only if `active_users[username][token] is A`. Transfer-local cleanup for A should still run.

## Selected fix skeleton

See `report_drafts/U123-SELECTED-FIX-SKELETON-REV0037.md`. The prototype patch touches `downloads.py` and `transfers.py` only. It does not require protocol changes.

## Impact boundary

Bounded impact: availability and transfer-session integrity. A malicious or buggy peer can cause active download state to be replaced or orphaned from progress/close callbacks. This can leave stale transfer state and open local transfer resources until another cleanup path intervenes.

## Public-overlap classification

Conservative class retained: candidate, no exact direct public match found in captured searches; transfer lifecycle and protocol-token public context exists.
