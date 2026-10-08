# rev0290 post-readout context receipt reroute audit

## What changed

`rev0290` tightens the post-readout new-context lane after the `rev0289` receipt gate. A recorded `post-readout-context-receipt.json` is now an explicit stop-and-reroute state: rerunning `owner-field-next` without the actual CSV no longer falls through to older packet/contact logic. The router tells the operator to rerun with the same returned owner-context CSV/source packet so the returned-CSV guards and receipt-sourced intake path run together.

## Risk corrected

Two false-progress patterns were still possible:

1. A context receipt could become the latest scratch artifact, but the router had no branch for it. In that state, a maintainer could be sent back toward stale packet/contact state or a fresh first-contact packet instead of the intended intake path.
2. A receipt was matched by CSV hash alone. If a later `new_owner_context_available` recheck appeared for the same CSV, an older receipt could satisfy the newer recheck by accident and erase the current recheck lineage.

## New executable firebreak

The router now validates the latest `post-readout-context-receipt.json` directly. If it is well-formed and no CSV argument is supplied, the only recommended command is `owner-field-next CSV=...` with the same returned context. If a CSV argument is supplied, a matching receipt must be tied to the current selected new-context recheck by both recheck reference and recheck hash, not by CSV hash alone.

## What this still does not do

This gate does not contact an owner, import a real `SRC2+` packet, accept evidence, edit service records, move lifecycle state, create custody, support public language, run a live window, or close `FT-0181`. It only prevents a local context receipt from becoming a dead-end, a stale-clock fallback, or a stale-recheck shortcut.

## Correct next move

Keep using the router. After a post-readout context receipt exists, run the router again with the same actual returned CSV/source packet. Intake must occur through `SOURCE_POST_READOUT_CONTEXT_RECEIPT`, and only after the returned-CSV source/smoke/path guards run.
