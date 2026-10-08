# rev0269 operator note — route-first hold is not closure

Use this note after reading `docs/00-meta/rev0269-routefirst-branch-hold-nosend-refactor.md`.

## Current branch decision

The public tree records an explicit current-revision no-send hold at `examples/external-contact-route-first-branch-hold-rev0269-aiid.json`.

The reason is narrow and practical: no human signature, no sender authority, no send-time locator recheck, no selected private vault roots, no final immediate hash recompute, and no actual transport proof.

## What the hold does

It prevents drift. Future operators should not infer that the route-first branch was forgotten, implicitly rejected, or silently completed.

## What the hold does not do

It does not contact RAIC/AIID. It does not start any response clock. It does not create silence, decline, waiver, custody, intake, import, recognition, or live-floor effect. It does not close `FT-0205-FIRST-REAL-ARTIFACT-DROP`, `FT-0207-FIRST-LIVE-EVIDENCE-ACQUISITION`, or `FT-0199-ACTUAL-LIVE-COUNTERPARTY-RESPONSE`.

## To reopen the branch

A human operator must supply signature and sender authority, select private vault roots, recheck the public locator immediately before send, recompute the exact route-first body and `.eml` hashes, send through an authorized channel, and preserve transport proof.

If that does not happen, keep the hold recorded and do not add more doctrine to compensate.
