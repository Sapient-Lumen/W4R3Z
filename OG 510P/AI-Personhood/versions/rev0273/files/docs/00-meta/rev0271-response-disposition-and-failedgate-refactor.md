# rev0271 response disposition and failed-gate refactor

rev0271 addresses the riskiest post-packet gap: the cube was prepared to say “not sent,” but less prepared to handle what happens if a human later authorizes contact and the response is messy. The first external outcome might be no authority, failed send, delivery-only metadata, an auto-reply, a human decline, a referral, a narrow scoping yes, no response after expiry, or a request for private material.

The new rule is simple: every non-success outcome must have a safe public shell before anyone can convert it into progress. Public shells preserve non-satisfaction, non-waiver, cure paths, and harassment/retaliation controls without exposing raw private records.

## Substance added

- `examples/reviewer-response-disposition-playbook-rev0271.json` gives the operator a classification table for messy outcomes.
- `examples/failed-gate-public-summary-rev0271-reviewer-route-unavailable-template.json` gives A3/A6 a public failed-gate shell.
- The reviewer-first message now explicitly allows a one-line disposition and says decline, referral, auto-reply, delivery, or silence is not waiver or recognition.
- Queue P0 items now close only through signed authority plus A1-A6 evidence or a public failed-gate record.

## Refactor effect

This pass trims additional generated duplicate history from the working ZIP and records the trim in the compaction ledger. The purpose is not to erase history; immutable release bundles carry history. The current cloudtainer should stay light enough to keep live execution work possible.

## Non-effect

No live evidence is created here. The refactor deliberately preserves zero-floor state.
