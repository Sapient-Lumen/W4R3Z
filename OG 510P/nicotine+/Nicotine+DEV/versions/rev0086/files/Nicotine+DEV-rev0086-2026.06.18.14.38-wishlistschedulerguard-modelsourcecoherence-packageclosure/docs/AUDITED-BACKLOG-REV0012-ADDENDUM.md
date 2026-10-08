# Audited backlog addendum — rev0012

## Summary

rev0012 completed the planned TR-STATUS-01 batch and did not promote it to the strict document.

## U-158 — UploadFailed/UploadDenied status-message provenance

**Status:** source-confirmed and dynamically witnessed across all three archived lanes.

**Current-behavior witness:** `maintainer_artifacts/tr-status-01/test_transfer_status_message_binding_reproducer.py`.

**Observed:**

- `UploadFailed(filename)` can close an active download F socket and requeue the transfer when the message is associated with the matching claimed username and virtual path.
- `UploadDenied(filename, reason)` can move a queued download to failed state with peer-supplied reason semantics.
- The message shapes lack transfer token/generation fields.

**Backlog decision:** keep as audited hardening / PB-01 adjunct, not standalone strict in rev0012.

## U-166 — PlaceInQueueResponse queue-position mutation

**Status:** source-confirmed and witnessed across all three archived lanes.

**Observed:** `PlaceInQueueResponse(filename, place)` can update `queue_position` using only claimed username and virtual path.

**Backlog decision:** demote/absorb under TR-STATUS-01. Low standalone value unless a stronger downstream consequence is proven.

## Queue changes

- U-158: proved then pruned to audited hardening.
- U-166: proved low-impact and absorbed.
- U-163: raised as next substantive target.
- U-262/U-267: raised as SEARCH-RESP-01 supporting subcases only.
