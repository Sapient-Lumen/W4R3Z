# rev0270 route-first send and reply runbook

Use this runbook only for the preferred no-attachment first hop.

## Branch point

Do exactly one of these:

1. authorize and send the route-first draft with proof capture; or
2. record explicit no-send.

Do not create a no-response, failed-gate, custody, intake, import, recognition, waiver, adverse-inference, or floor shell from a draft.

## Before sending

Confirm all six unresolved blockers in `examples/external-contact-route-first-send-capture-gate-rev0270-aiid.json`:

- human signature over recipient, subject, body hash, no-attachment limit, and stage-two deferral;
- sender authority for the account and role;
- send-time public locator recheck;
- off-release private vault roots for sent copy, transport trace, delivery/DSN status, and raw reply;
- final route-first body and `.eml` hash recompute after signature and before dispatch;
- transport-proof capture procedure ready for the exact send channel.

## Immediately after sending, if sent

Capture the sent copy and provider trace before doing anything else. Record sent timestamp, sender role, recipient, subject, body hash, Message-ID or provider equivalent, and delivery/DSN status if available. Raw transport bytes stay outside the public release tree.

A response/no-response wait window can start only after transport proof is captured.

## Before opening or summarizing any reply

Prepare the raw inbound reply vault path outside the release tree. Preserve raw bytes and headers/provider metadata first. Public release may get only a shell or summary allowed by the reply class and retention limits.

## Reply handling

- DSN/bounce: delivery status only.
- Auto-ack/ticket: transport-adjacent status only.
- Decline/out of scope: close without waiver or adverse inference.
- Referral: new route-fit and locator review before any resend.
- Willingness to look: prepare stage-two authorization; do not automatically send payload.
- Request for incident submission: pause for new route-fit review because the current ask is collaboration/routing, not incident filing.
- Conditional retention: apply conditions before any public shell.
- Redacted-only material: record as control artifact, not raw custody.
- Protocol/tool output: preserve as protocol output, not authority.

Stage two requires fresh human authorization and final hash recompute even after a willing reply.
