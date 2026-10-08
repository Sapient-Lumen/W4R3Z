# rev0288 post-readout recheck gate audit

## What changed

`rev0288` turns the due/recheck date inside a post-readout recheck due-date firebreak into an executable gate. A dispatch no longer becomes a permanent stop after it is recorded. If the dispatch due date has not arrived, the router waits. If the due date has arrived, the router emits `make owner-post-readout-recheck`, which writes one bounded `scratch/owner-post-readout-rechecks/**/post-readout-recheck.json` record.

## Risk corrected

The risky pattern was quiet expiration. `rev0288` correctly stopped after the post-readout dispatch, but that meant a due/recheck date could pass with no executable reminder, no source-hash recheck, and no explicit record of whether new owner context exists. That can look safe while failing to complete the owner-held action lane.

## New executable firebreak

The recheck recorder preserves only:

- the source dispatch path and SHA-256 hash;
- dispatch lane, owner action class, source truth class, and due date;
- the actual check date, which must be on or after the dispatch due date;
- a bounded recheck outcome;
- reviewer role and new-context counts;
- explicit no-expansion, no-public-claim, no-service-edit, no-lifecycle-change, and no-closure confirmations.

The recheck cannot copy owner answers, raw CSV rows, live-window notes, contact details, public claim text, or new owner context. If new owner context exists, the recheck can only say that it is held outside the archive and must be routed later through `owner-field-next CSV=...`.

## What this still does not do

This gate does not contact an owner, import a real packet, accept evidence, edit service records, move lifecycle state, support public language, create custody evidence, or close `FT-0181`. It only prevents the post-readout owner-action lane from expiring into silence or being mistaken for completion.

## Correct next move

Use `owner-field-next`. When it sees a post-readout dispatch before its due date, it waits. On or after the due date, it emits `owner-post-readout-recheck`. After a no-context recheck, the router stops. After a new-context recheck, it routes only to `owner-field-next CSV=/path/to/actual-returned-owner-context.csv`; the recheck itself is never the intake source.
