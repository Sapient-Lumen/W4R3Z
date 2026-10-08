# rev0291 post-readout context receipt gate audit

## Gate posture

`rev0291` does not change the rev0290 post-readout context receipt gate. The prior repair remains the correct executable seam: a recorded `post-readout-context-receipt.json` is an explicit stop-and-reroute state, and returned-context intake requires a receipt tied to the current selected `new_owner_context_available` recheck by both reference and hash.

## Why the gate still matters

The mission/interface audit found that the main current risk is not a missing post-readout validator. It is operator drift: local artifacts can feel like progress and distract from the next real owner step. Keeping this gate unchanged avoids another control-layer expansion while preserving the important late-lineage firebreak.

## What stays forbidden

The context receipt does not contact an owner, import a real `SRC2+` packet, accept evidence, edit service records, move lifecycle state, create custody, support public language, run a live window, or close `FT-0181`. It only prevents a local context receipt from becoming a dead-end, stale-clock fallback, stale-recheck shortcut, or evidence-laundering shortcut.

## Correct next move

Keep using the router. After a post-readout context receipt exists, run the router again with the same actual returned CSV/source packet. Intake must occur through `SOURCE_POST_READOUT_CONTEXT_RECEIPT`, and only after the returned-CSV source/smoke/path guards run. In a clean extract with no real owner packet, start with packet prep, not post-readout context work.
