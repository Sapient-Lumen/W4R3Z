# rev0270 route-first operator pack and current-pointer refactor

rev0270 keeps the route-first/no-attachment branch in a no-send state, but removes two execution risks that could otherwise waste the next session.

First, it adds an exact operator execution pack for the route-first branch. The pack binds the current recipient, subject, body, `.eml`, hashes, no-attachment limit, stage-two deferral, unsigned human/sender authority slots, private-vault placeholders, and send/reply/stage-two checklist in one place. It is deliberately not an authorization record. The remaining blockers still require off-release human signature, sender authority, send-time public locator recheck, private vault roots, final hashes, and actual transport proof.

Second, it repairs current-pointer drift. `SURFACE-STATUS.json` still had current queue/resource pointers stuck on rev0258, even though later revisions moved the active branch to route-first hold. rev0270 updates those pointers to current surfaces and adds a pointer-integrity report/audit so active front-door and status lanes cannot quietly point at stale current artifacts. Historical changelog references remain historical; only current operating surfaces are constrained.

## What is now more executable

The operator can begin from `examples/external-contact-route-first-operator-execution-pack-rev0270-aiid.json` instead of assembling the send branch from scattered gates. The pack says exactly what must be supplied before any route-first send:

- human signature binding the exact recipient, subject, body hash, `.eml` hash, no-attachment rule, and stage-two deferral;
- sender account or role authority;
- send-time public locator recheck;
- off-release private roots for sent copy, transport trace, delivery/status evidence, and raw inbound replies;
- final route-first body and `.eml` hash recompute immediately before dispatch;
- actual transport proof if a message is sent.

The pack also preserves the reason no message is sent in this revision. It does not close first-artifact tasks, create silence or no-response evidence, start a wait window, or authorize stage two.

## Refactor result

The active queue still has exactly seven items. Their receiving surfaces have been moved from older rev0258 branch docs to current rev0270 execution artifacts. This is not a doctrinal expansion; it is a pointer and operator-readiness correction.

## Locks preserved

No organization has been contacted. There is no send, transport proof, delivery status, DSN, Message-ID, response clock, inbound artifact, custody, intake, import, recognition, or live-floor effect. A public locator, public operator pack, draft, branch hold, hash, or checklist remains preparation only.
