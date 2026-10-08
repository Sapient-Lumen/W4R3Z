# rev0270 — send-readiness gate and contact-trim refactor

## What changed

rev0270 moves the archive from an exact payload manifest to an executable send-readiness gate. The risky unfinished step is no longer doctrine or registry coverage; it is whether a human operator can make a real send without losing proof, drifting the payload, misrouting the request, or accidentally turning a draft/checklist into response, custody, intake, import, waiver, adverse inference, status, or live-floor evidence.

The new current surface is `examples/external-contact-send-readiness-gate-rev0270-aiid.json`, checked by `tools/audit_external_contact_send_readiness_gate.py`. It binds the request packet, send handoff, public payload manifest, mail-ready draft, dispatch authorization card, send-proof record, send-trace shell, delivery-status shell, inbound-vault precommit, inbound-capture shell, response-triage record, and seven-item operating board.

## Substantive correction

The first-contact body now says the RAIC/AIID path is a collaboration/routing inquiry, not an incident submission. That matters because the point of first contact is to find a responsible public-interest route for preservation and formation review, not to force an AIID incident record or imply that a harm event has already been accepted by a database steward.

The attached one-page ask also has a routing note: an out-of-scope or alternate-channel reply is useful, but it is not recognition, refusal evidence, custody, intake, import, waiver, adverse inference, or floor credit.

## Waste removed

Before rev0270, a future operator still had to infer which blocker mattered most. The payload was exact, but the send/no-send branch was spread across several surfaces. rev0270 consolidates the live operator question into eight hard blockers:

1. human signature;
2. sender authority;
3. conflict review;
4. public locator recheck;
5. route-fit review;
6. private outbound/inbound vault roots;
7. transport proof capture plan;
8. payload/body hash recompute.

All eight are intentionally unsatisfied. The gate fails closed until an operator either performs a signed send with proof or records an explicit no-send decision.

## Current state

No organization has been contacted. No message has been sent. No transport proof, delivery status, DSN, Message-ID, response clock, inbound artifact, raw retention permission, custody, response, intake, import, recognition, waiver, adverse inference, or live-floor effect exists.

## Next action

Run the send-readiness audit. If it remains blocked, do not pretend the first-artifact lane advanced. The only substantive next branch is a human-signed send with private-vault and transport-proof preparation, or an explicit no-send record.
