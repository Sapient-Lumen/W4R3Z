# rev0288 post-readout recheck due-date gate audit

## What changed

`rev0288` turns the final manual seam after a terminal live-window readout into an executable local gate. A bounded readout no longer routes to “open a document and decide what to do.” It now routes to `make owner-post-readout-action`, which writes `scratch/owner-post-readout-actions/**/post-readout-action.json` from one hash-checked `live-window-readout.json`.

## Risk corrected

The risky pattern was post-readout drift. A careful terminal readout could still be followed by silent expansion, service-record edits, lifecycle movement, public-language changes, or closure language because the next step was prose-driven. That is wasteful because it asks maintainers to preserve discipline by memory after the archive has already invested heavily in executable gates.

## New executable firebreak

The post-readout action recorder preserves only:

- the source readout path and SHA-256 hash;
- the normalized dispatch lane derived from the readout disposition;
- bounded action, re-ask, drop, reviewer, and disagreement counts;
- a due/recheck date;
- class labels for the next owner-held action or recheck;
- explicit no-expansion, no-public-claim, no-service-edit, no-lifecycle-change, and no-closure confirmations.

It blocks raw learner data, protected facts, security payloads, public-claim upgrades, owner answers, live-window notes, contact details, and public-claim text.

## What this still does not do

This gate does not contact an owner, import a real owner packet, accept evidence, edit service records, move lifecycle state, support public language, create custody evidence, or close `FT-0181`. It only prevents the next local action from being invented outside the bounded readout chain.

## Correct next move

Use `owner-field-next`. If it sees a terminal readout, it emits the bounded `owner-post-readout-action` command. Once that dispatch exists, the router stops with no further archive command until genuinely new real owner context exists.
