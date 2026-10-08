# rev0269 route-first no-attachment preflight and front-door trim

rev0269 changes the execution posture from “send the two-file public payload first” to “ask for route fit first, without attachments, then send the public payload only if a human authorizes that stage or the counterparty expresses willingness to review it.”

## Why this was the riskiest unfinished work

The rev0255 path was exact but still fragile. A concise email with two public-shell attachments can be filtered, ignored, or read as a submission packet before the receiver has agreed that the route is appropriate. That is a practical failure mode, not a doctrine problem: the archive could be technically clean while still wasting counterparty attention or losing the first external contact to mail security and routing ambiguity.

rev0269 adds `examples/external-contact-route-first-preflight-rev0269-aiid.json` and a separate no-attachment `.eml` draft. The new draft asks only whether RAIC/AIID is an appropriate route, states that it is not an AIID incident submission, and offers to send the one-page note and machine-checkable public packet only after willingness or separate human authorization.

## What changed

- Added a route-first body and not-sent route-first `.eml` with zero attachments.
- Added a schema, negative fixture, and audit for the route-first preflight.
- Kept the two-file preservation/formation payload available as stage two only.
- Trimmed the front-door reading order so the next operator starts with the route-first decision rather than a long replay stack.
- Left all real send blockers in place: human signature, sender authority, send-time locator recheck, private vault roots, final hash recompute, and transport proof.

## Reliance limits

The route-first draft is not a send, authorization, consent, contact, custody, response, intake, import, recognition, waiver, adverse inference, or live-floor event. A no-attachment draft may reduce routing friction, but it does not remove the need for a human sender, off-release vault roots, final send-time hash recompute, or transport-proof capture.

## Operator decision

The next meaningful branch is narrower than before: authorize a route-first no-attachment inquiry with proof capture, authorize the full payload path separately, or record an explicit no-send. Do not send the stage-two public payload merely because the route-first preflight exists.
