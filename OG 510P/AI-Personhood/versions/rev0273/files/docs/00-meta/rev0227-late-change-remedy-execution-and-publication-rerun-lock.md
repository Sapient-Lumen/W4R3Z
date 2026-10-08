# rev0227 late-change remedy execution and publication rerun lock

## Why this revision exists

rev0226 closed the remedy-window problem: a late revocation, supersession, correction, rollback signal, or appeal could not be marked resolved unless the remedy window closed with retained submissions, scoped authority, and a decision record. The next risky seam was simpler and more operational: a remedy decision could be treated as if the remedy had actually been carried out.

rev0227 adds a distinct **late-change remedy execution record**. It is the object for proof that the ordered rollback, correction, supersession, no-change completion, or recompute-routing action has actually happened, with non-host execution proof and affected-party completion notice. It still cannot continue publication, upgrade reliance, or increment the floor.

## Current live route

`evidence drop → pilot → LEAP candidate → candidate challenge/replay → custody authority gate → custody record → response verification gate → response record → intake conversion gate → intake record → import readiness gate → actual import gate → floor activation record → quorum participation record → computed floor → floor recompute receipt → publication rollback adjudication → late-change ingress → late-change notice dispatch → late-change remedy resolution → late-change remedy execution`

## What is now blocked

- Treating a remedy-resolution decision as corrective-action execution.
- Continuing a published floor posture after a rollback-required decision without rollback completion proof.
- Marking a correction or supersession complete without public-shell corrective-action refs.
- Treating silence or elapsed time as execution completion.
- Publishing private-vault remedy material or sealed corrective-action evidence.
- Incrementing live floor or upgrading reliance from the remedy execution record itself.

## The refactor

`tools/prepare_live_receipt_publication_rollback_adjudication.py` now replays remedy execution records. A live remedy resolution that is ready but not executed blocks publication as `blocked-remedy-resolution-unexecuted`; an incomplete execution blocks as `blocked-late-change-remedy-execution-open`.

The admission graph and artifact import invariant report now include `LATE_CHANGE_REMEDY_EXECUTION` after `LATE_CHANGE_REMEDY_RESOLUTION`, so the late-change path has an executable final corrective-action gate rather than a paper-resolution endpoint.

## Reliance limit

The live floor remains zero/stayed. The new execution record is a completion-and-rerun routing object, not proof that a genuine late signal exists and not proof that publication can continue. After any ready execution, the archive still requires floor recompute receipt and publication rollback adjudication reruns before public posture can move.
